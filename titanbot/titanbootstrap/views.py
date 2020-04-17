from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.management import call_command
from django.http.response import JsonResponse

from titanbootstrap.models.settings import ApplicationSettings
from titanbootstrap.utils import VersionChecker, purge_dir

from itertools import chain

import fnmatch
import shutil
import redis
import subprocess
import traceback
import dirsync
import datetime
import os
from itertools import chain

class DependencyError(Exception):
    """
    Base Dependency Error.
    """
    pass


class TesseractCheckError(DependencyError):
    """
    Tesseract Dependency Error.
    """
    pass


class NodeCheckError(DependencyError):
    """
    NodeJS Dependency Error.
    """
    pass


def _exception_response(title, exception, as_json=False, extra=None):
    """
    Given a title and exception, create  response that represents our exception.

    We can optionally decide to return the data as a json dictionary instead of
    returning a valid JsonResponse object.

    Use the extra parameter to include some text below the traceback.
    """
    data = {
        "status": "ERROR",
        "title": title,
        "traceback": traceback.format_exc().replace("\n", "<br/>"),
        "type": exception.__class__.__name__
    }

    if extra:
        data["traceback"] += "<br/><br/>{extra}".format(extra=extra)
    if as_json:
        return data

    # By default, we return the data as a JsonResponse object.
    # We can specify to return as pure data for use with dependencies.
    return JsonResponse(data=data)


def bootstrap(request):
    """
    Render the bootstrapping page with a unique filename for our bootstrap javascript file.
    """
    return render(request, "bootstrap/bootstrap.html", context={
        "bootstrap_js": mark_safe("js/bootstrap/bootstrap.js?{uniq}".format(
            uniq=str(datetime.datetime.utcnow().timestamp()).split(".")[0]))
    })


def check_update(request):
    """
    Check for an available update for the titandash program.
    """
    # Note that this can't fail so no need for try: except here.
    # If a new version can't be obtained, falling back to an error status.
    version = VersionChecker()

    return JsonResponse(data={
        "status": version.perform_check(),
        "current": version.current,
        "newest": version.newest
    })


def perform_update(request):
    """
    Perform an update on the titandash program.

    This is a potentially dangerous command and as such, certain things are put
    in place to ensure errors are handled gracefully.

    The following functionality is handled here:

    1. Download the most recent titandash release.
    2. Create a backup of the users current code base.
    3. Synchronize newest release with current code base.
    4. If no exceptions occur, return json response with data about finished process.
    5. If exceptions occur, attempt to synchronize the backup into the users code base.
    6. If exceptions occurs here, return helpful error message.
    """
    version = VersionChecker()
    try:
        # Downloading the source package containing all the newest source code.
        directory = version.download_newest()
        # Remove the most recent backup from our local data directory.
        purge_dir(path=settings.LOCAL_DATA_BACKUP_DIR)

        # Create a backup of the current code directory by syncing the current
        # directory into our local backups directory.
        dirsync.sync(
            sourcedir=settings.ROOT_DIR,
            targetdir=settings.LOCAL_DATA_BACKUP_DIR,
            action="sync",
            exclude=(
                "node_modules", "titanbot/static", "titanbot/logs", ".git",
                ".github", ".idea", ".gitattributes", ".gitignore"
            )
        )

        # Let's go ahead and attempt to synchronize our newly downloaded
        # version package into our current code.
        try:
            dirsync.sync(
                sourcedir=directory,
                targetdir=settings.ROOT_DIR,
                action="sync",
                purge=True
            )
        except Exception as exc:
            # An exception has occurred while attempting to update the code base,
            # our best bet here is to recover our backup so that the code goes back
            # to what it was before the update.
            dirsync.sync(
                sourcedir=settings.LOCAL_DATA_BACKUP_DIR,
                targetdir=settings.ROOT_DIR,
                action="sync"
            )

            # Returning a recovered status to the javascript...
            # Since we're restoring our backup directory, our code
            # should not have changed, we can continue with bootstrapping and
            # display a message at the end about what happened.
            return JsonResponse(data={
                "status": "RECOVERED",
                "exception": _exception_response(
                    title="Perform Update",
                    exception=exc,
                    as_json=True,
                    extra="The exception above occurred while attempting to update titandash to the newest version, "
                          "a backup of all your application files was safely recovered and the program has not been "
                          "updated.<br/><br/>You can attempt to auto update again by refreshing the page, or, download "
                          "the newest release manually."
                )
            })

        # After an update is successful, we perform both the node install,
        # and the static files collection process. Since cache busting can break
        # after an update is complete, since all files are purged.
        perform_node_packages(request)
        perform_static(request)

        # We were able to successfully synchronize the newest codebase into our main directory.
        # We should now return some useful information to the bootstrapping javascript
        # to let the user know that it has been updated successfully, and that they should
        # restart their application to see the newest changes.
        return JsonResponse(data={
            "status": "DONE"
        })

    # Very unrecoverable error has occurred, This means the code base is not reliable.
    # The user may need to manually download the latest release themselves at this point.
    # The users database and logs will remain.
    except Exception as exc:
        return _exception_response(
            title="Perform Update",
            exception=exc,
            extra="<br/>This error could not be recovered from and your code base is now in an inconsistent state. "
                  "Don't worry though! You can go and download the newest release manually still. Check out "
                  "<a href='https://titandash.net'>this</a> link to do that now.<br/>You're data has <strong>not</strong> been "
                  "lost due to this error."
        )


def perform_requirements(request):
    """
    Perform the pip install on our requirements file.

    Ensuring tht any new requirements or needed functionality is present in our application and available.
    """
    try:
        # As long as this command executes without raising an exception,
        # we can safely assume the requirements are now uo to date.
        return JsonResponse(data={
            "status": "DONE",
            "output": str(subprocess.check_output(["pip", "install", "-r", os.path.join(settings.ROOT_DIR, "requirements.txt")]))
        })

    # Catching a broad exception clause to ensure that we can move forward
    # with execution no matter what error occurs.
    except Exception as exc:
        return _exception_response(
            title="Python Requirements",
            exception=exc,
        )


def perform_node_packages(request):
    """
    Perform the node package manager install process to install all of our required modules.

    This command will fail if node is not installed by the user. But we can broads catch and
    catch the more detailed exception below with our dependency check.
    """
    try:
        # Again, as long as our subprocess command completes, we can assume the modules were all installed.
        # Also setting our working directory explicitly to ensure the install command uses proper package file.
        return JsonResponse(data={
            "status": "DONE",
            "output": str(subprocess.check_output("npm install", shell=True, cwd=settings.ROOT_DIR))
        })

    # Catching a broad exception again to ensure processes move forward on errors.
    except Exception as exc:
        return _exception_response(
            title="Node Package Install",
            exception=exc
        )


def perform_migration(request):
    """
    Perform the database migration functionality.
    """
    try:
        call_command("makemigrations")
        call_command("migrate")

        # After both commands have ran successfully, migrations
        # are guaranteed to be up to date.
        return JsonResponse(data={
            "status": "DONE"
        })

    # Broad exception clause here in case an odd error occurs
    # while attempting to migrate...
    except Exception as exc:
        return _exception_response(
            title="Database Migrations",
            exception=exc
        )


def perform_cache(request):
    """
    Perform the database caching migration command functionality.
    """
    try:
        call_command("createcachetable")

        # After command is complete, cache table is created successfully.
        return JsonResponse(data={
            "status": "DONE"
        })

    # Similar to other process exception clauses... See above.
    except Exception as exc:
        return _exception_response(title="Database Caching", exception=exc)


def perform_static(request):
    """
    Perform the static files collection functionality.
    """
    try:
        call_command("collectstatic", interactive=False)

        # After command is complete, static files have been created successfully.
        return JsonResponse(data={
            "status": "DONE"
        })

    # Another broad exception catch here. See perform_migration comment stub
    # for more information about this.
    except Exception as exc:
        return _exception_response(title="Collect Staticfiles", exception=exc)

def _find_tesseract():
    """Force find 'tesseract.exe'
    
    Raises:
        exception: TesseractCheckError
    
    Returns:
        string -- path to tesseract.exe
    """

    exe = "tesseract.exe"
    import fnmatch
    exception = TesseractCheckError("It seems like tesseract is not currently installed on your system, or titandash "
                                    "was unable to find the program")
    match = None
    paths = ('C:/','D:/','E:/','F:/','G:/')
    for root, dirnames, filenames in chain.from_iterable(os.walk(path) for path in paths):
        for filename in fnmatch.filter(filenames, exe):
           return os.path.join(root)
    
    raise exception
     
def _check_tesseract():
    """
    Test that the tesseract is installed and that the executable (if one is available) is set
    to be used by our titandash settings.

    We'll check first to determine if we've already parsed out a tesseract path and see if it's still
    valid, if it is, we use it and move on.

    If the directory has changed, we check the default locations and fallback to a dynamic search
    of the system to make sure it's available. Application settings will remember the last used location.
    """
    def _ensure_trained_data(directory):
        """
        Ensure that the specified tesseract path does in fact contain our valid trained data file.

        As long as the file's raw contents are already the same, we don't need to worry
        about changing anything else in the directory.
        """
        proper_file = settings.TESSERACT_TRAINED_DATA_FILE

        current_file_directory = os.path.join(directory, "tessdata")
        current_file = os.path.join(current_file_directory, settings.TESSERACT_TRAINED_DATA_NAME)

        # First, retrieve the contents of our proper eng.traineddata file
        # that will be used as a replacement if needed.
        with open(proper_file, "rb") as ptd:
            proper_contents = ptd.read()

            # With our current proper directory, grab the contents from
            # the current trained data for comparison.
            try:
                with open(current_file, "rb") as ctd:
                    current_contents = ctd.read()

            # Unlikely, but maybe a user is missing the traineddata file.
            # Make sure we move the proper one over if it's missing.
            except FileNotFoundError:
                current_contents = None

            # If our content differs at all, we need to copy and replace the current
            # trained data with our proper data file.
            if proper_contents != current_contents:
                shutil.copy(
                    src=proper_file,
                    dst=current_file_directory
                )

    def _find_tesseract(paths, exclude):
        """
        Attempt to find the tesseract executable file on the system.
        """
        for root, dirs, files in chain.from_iterable(os.walk(p) for p in paths):
            for _ in fnmatch.filter(files, "tesseract.exe"):
                # tesseract.exe is on the system in a location
                # that's a "non default" and isn't in an excluded location.
                if not any(excl in root for excl in exclude):
                    return root

    possible_paths = ("C:/", "D:/", "E:/", "F:/", "G:/")
    # Make sure any recycle bin locations are excluded.
    # Could happen if old installations are deleted.
    exclude_paths = ["Recycle.Bin"]
    # We are explicitly adding the "ProgramW6432" environment variable to the end in case
    # issues come up with the os module when grabbing the paths.
    environ_vars = ["ProgramW6432", "ProgramFiles(x86)"]
    potential_paths = [os.path.join(os.environ[var], "Tesseract-OCR") for var in environ_vars]    

    try:
        # Grab a reference to our application settings instance.
        # We can use this to determine if we need to even bother
        # with dynamic location checking.
        app_settings = ApplicationSettings.objects.grab()
        tesseract_path = None

        if app_settings.tesseract_directory:
            # A previous boot had found a valid directory.
            # Check that this one still works before continuing.
            if os.path.exists(path=app_settings.tesseract_directory):
                tesseract_path = app_settings.tesseract_directory

        if not tesseract_path:
            # Instead, let's check our default paths that could
            # possibly (and most likely) house tesseract.
            for path in potential_paths:
                if os.path.exists(path):
                    tesseract_path = path

            # Tesseract is not present in any of our default paths,
            # try a system search to find it.
            if not tesseract_path:
                tesseract_path = _find_tesseract(paths=possible_paths, exclude=exclude_paths)

        # Final check after all conditional paths reached.
        # If we have a path, we can update our app settings if
        # it's changed from the previous one.
        if not tesseract_path:
            raise exception

        # Path is available, update and setup proper settings.
        if app_settings.tesseract_directory != tesseract_path:
            app_settings.tesseract_directory = tesseract_path
            app_settings.save()

        settings.TESSERACT_COMMAND = "{path}/tesseract".format(path=tesseract_path)

        # We also need to make sure that the proper english trained data
        # file is available within our tesseract directory.
        _ensure_trained_data(directory=tesseract_path)

    # Broadly catch exceptions so our TesseractCheckError is caught as well as any other error.
    except Exception as exc:
        return _exception_response(
            title="Dependencies - Tesseract",
            exception=exc,
            as_json=True
        )


def _check_redis():
    """
    Test that the redis server is installed and currently running.

    We unfortunately cannot start it programmatically. But we can very easily report back the exact
    commands a user will have to enter to start the server.
    """
    try:
        # Using client_list() to just derive connection or not...
        # Disposing out result.
        redis.Redis("localhost").client_list()

        # If we can check the client list, it's safe to assume that the redis server
        # is running properly.
        return True

    # Catch broadly for errors that occur when trying to establish redis
    # connection. We can not actually fix this programmatically so we at least send a message.
    except Exception as exc:
        return _exception_response(
            title="Dependencies - Redis Server",
            exception=exc,
            as_json=True,
            extra="You can run the following command in an ubuntu window to ensure redis is started:<br/>"
                  "<em>sudo service redis-server restart</em>"
        )


def _check_node():
    """
    Test that node has been installed on the users machine.

    We can return a helpful message to users if it turns out that node is missing.

    Once a user installs node, no additional configuration is needed by us. Node is automatically
    included on the users system path so that it can be used from anywhere.
    """
    exception = NodeCheckError("It looks like node is not installed on your system. Node is used to download "
                               "numerous dependencies that are used by the web application. The dashboard may not "
                               "work correctly until you've installed node and ran the npm install command.")

    try:
        check = subprocess.run("npm --version", shell=True, universal_newlines=True)

        # Do we have a proper return code for the subprocess called?
        if check.returncode == 0:
            return True
        else:
            raise exception

    # Check for a file not found error which may occur when npm is not installed at all
    # on the users system.
    except subprocess.CalledProcessError:
        return _exception_response(
            title="Dependencies - Node",
            exception=exception,
            as_json=True
        )
    # Catch broadly for errors that occur when trying to check status of node.
    except Exception as exc:
        return _exception_response(
            title="Dependencies - Node",
            exception=exc,
            as_json=True)


def perform_dependency(request):
    """
    Perform dependency checks here.

    After a user installs the required dependencies, some steps may need to be taken
    to ensure they are all configured correctly. We can at least test for some of them
    here and return some helpful errors if it turns out that something is mis configured.
    """
    exceptions = []

    # Loop through every available dependency check.
    # A failed check should return a JsonResponse object.
    # Successful ones will just return a bool that can be ignored.
    for check in [_check_tesseract, _check_redis, _check_node]:
        res = check()
        if isinstance(res, dict):
            exceptions.append(res)

    if len(exceptions) > 0:
        return JsonResponse(data={
            "status": "ERROR",
            "exceptions": exceptions,
        })

    return JsonResponse(data={
        "status": "DONE"
    })
