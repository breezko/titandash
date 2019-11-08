from django.db import models


class ExternalAuthReferenceManager(models.Manager):
    """
    Store helper methods used on the auth reference objects to determine authentication and validation.
    """
    def generate(self, email, token):
        """
        Generate an authentication reference with the specified parameters.

        If one already exists, we modify it instead of creating multiple.
        """
        if self.all().count() == 0:
            return self.create(email=email, token=token)

        instance = self.first()
        instance.email = email
        instance.token = token
        instance.valid = False

        # Return modified instance.
        return instance

    def valid(self):
        """
        Determine if the current reference is valid, if one exists.
        """
        if self.all().count() == 0:
            return False

        # Return the valid state of the existing reference.
        return self.first().valid


class ExternalAuthReference(models.Model):
    """
    Storing a reference to the credentials used to login to the system.

    These can be used during the initial authentication check so a reference is
    available if the authentication succeeds.
    """
    objects = ExternalAuthReferenceManager()
    email = models.EmailField()
    token = models.CharField(max_length=255)
    valid = models.BooleanField(default=False)

    def __str__(self):
        return "{email} ({valid})".format(email=self.email, valid=self.valid)

    @property
    def hide_token(self):
        return "*" * len(self.token)

    def json(self, hide_sensitive=False):
        return {
            "email": self.email,
            "token": self.token if not hide_sensitive else self.hide_token,
            "valid": self.valid
        }
