from django.db import models


class ApplicationSettingsManager(models.Manager):
    """
    Store all queryset methods used by the application settings manager here.
    """
    def grab(self):
        """
        Attempt to grab the current application settings, creating one if it does not exist already.
        """
        if self.count():
            # Return the first available instance.
            return self.first()

        # Create a new application settings instance if one does not exist
        # at this point.
        return self.create()


class ApplicationSettings(models.Model):
    """
    Store all titandash specific application settings that should be "remembered" for future use.
    """
    class Meta:
        verbose_name = "Application Settings"
        verbose_name_plural = "Application Settings"

    objects = ApplicationSettingsManager()
    tesseract_directory = models.CharField(verbose_name="Tesseract Directory", null=True, blank=True, max_length=255)

    def __str__(self):
        return "Application Settings {pk}".format(pk=self.pk)

    def __repr__(self):
        return "<ApplicationSettings: {application_settings}>".format(application_settings=self)
