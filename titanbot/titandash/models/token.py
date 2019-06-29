"""
token.py

A single token authentication key will need to be present for Bot functionality to work.
"""
from django.db import models


class TokenInstanceManager(models.Manager):
    def grab(self):
        """
        Attempt to grab the current Token instance, only one should ever exist. If one does not
        exist when called, we generate one with a value of None. This can be queried for in other
        pieces of the Bot to check that a valid one exists.
        """
        if len(self.all()) == 0:
            self.create(token=None)

        # Returning the existing instance.
        return self.all().first()


class Token(models.Model):
    """
    Token Model.

    This model is only used to provide users with a way of specifying what their authentication
    token currently is.

    Information about their auth token will be populated by the Authenticator right into their
    BotInstance when the Bot is initialized.
    """
    class Meta:
        verbose_name = "Token"
        verbose_name_plural = "Tokens"

    objects = TokenInstanceManager()
    token = models.CharField(verbose_name="Token", max_length=64, blank=True, null=True)

    def __str__(self):
        return "Token <{token}>".format(token=self.token)
