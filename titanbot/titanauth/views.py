from django.http.response import JsonResponse
from django.shortcuts import render, redirect

from titanauth.models.user_reference import ExternalAuthReference
from titanauth.authentication.wrapper import AuthWrapper
from titanauth.authentication.constants import AUTH_SIGNUP_URL

import json


def authenticate(request):
    """
    Main authentication view. Allow the user to enter their external credentials from here.
    """
    return render(request, "auth/authenticate.html", context={
        "signup": AUTH_SIGNUP_URL
    })


def logout(request):
    """
    Logging a user out through their authentication reference.

    Really, we just delete the existing authentication reference and ensure we send an offline
    signal before doing so.
    """
    wrapper = AuthWrapper()
    wrapper.offline()
    wrapper.reference.delete()

    # Send the user back to the authentication page. The middleware
    # will likely do this for us anyways, but we explicit redirect to be sure.
    return redirect("authenticate")


def credentials(request):
    """
    Attempt to authenticate the users entered credentials to authenticate the user.
    """
    email = request.POST.get("email")
    token = request.POST.get("token")

    # Ensure our token is correctly stripped of unwanted characters.
    token = token.lstrip().rstrip()

    # Are all required variables present and filled out?
    if not email or not token:
        return JsonResponse(data={
            "status": "error",
            "message": "All fields must be filled out."
        })

    # Let's create our external authentication reference object
    # that we will use to attempt to validate the information provided.
    reference = ExternalAuthReference.objects.generate(
        email=email,
        token=token
    )

    # Attempt to retrieve authentication response.
    response = AuthWrapper().authenticate()
    response_content = json.loads(response.content)
    response_status = response.status_code

    if response_status == 200:
        if response_content["status"] == "success":
            reference.valid = True
    else:
        reference.valid = False

    reference.save()

    # Response should have a json dictionary and the status code is returned.
    return JsonResponse(
        data=json.loads(response.content),
        status=response.status_code
    )

