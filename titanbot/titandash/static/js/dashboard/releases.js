/**
 * releases.js
 *
 * Control functionality related to the checking of our current version and determining if the information
 * about that release has been displayed to the user yet or not.
 *
 * If a user has not yet seen the changelog for a release, we grab the information and explicitly display it
 * to the user within a modal.
 */
let ReleaseInfo = function() {
    /* Base Variables */
    let ajaxUrl = "/ajax/release";
    let ajaxDataType = "json";

    let elements = {
        alerts: $("#alert-container"),
        modal: $("#releaseModal"),
        header: $("#releaseModalTitle"),
        body: $("#releaseModalBody")
    };

    /**
     * Successful request, we will either show the modal, or exit early and do nothing.
     */
    let successCallback = function(data) {
        if (data["status"] === "success") {
            if (data["state"] === "not_shown") {
                if (data["release"]["status"] === "success") {
                    // The user has not yet seen the release information.
                    // Let's update the modal and display it.
                    elements.header.text(data["release"]["title"]);
                    elements.body.html(data["release"]["body"]);

                    // Display modal on screen.
                    elements.modal.modal("show");
                } else {
                    errorCallback(data["release"]);
                }
            }
        }

        if (data["status"] === "error") {
            errorCallback(data);
        }
    };

    /**
     * An error has occurred, we display a simple error alert, and continue as normal.
     */
    let errorCallback = function(data) {
        sendAlert(data["error"] || data.responseText, elements.alerts, null, "danger");
    };

    // Send the ajax request to retrieve information about the current release that
    // the program is on. If the information has already been seen, we do not display it again.
    $.ajax({
        url: ajaxUrl,
        dataType: ajaxDataType,
        success: successCallback,
        error: errorCallback
    });
};
