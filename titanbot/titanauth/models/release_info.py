from django.db import models


class ReleaseInfoManager(models.Manager):
    def grab(self, version):
        if len(self.filter(version=version)) == 0:
            return self.create(version=version)
        else:
            return self.get(version=version)


class ReleaseInfo(models.Model):
    """
    ReleaseInfo Model.

    Store instances of the databases current status in regards to the
    information about specific releases based on the semantic version
    for our released versions.

    ie: 1.7.0, 1.7.1, 1.8.0.1

    These versions would all have their own field, as well as a boolean to
    determine whether or not they've had their information retrieved
    through our authentication backend, after this happens, we do not
    display it ever again.
    """
    class Meta:
        verbose_name = "Release Info"
        verbose_name_plural = "Release Info's"

    objects = ReleaseInfoManager()
    version = models.CharField(verbose_name="Version", max_length=255)
    grabbed = models.BooleanField(verbose_name="Grabbed", default=False)

    def __str__(self):
        return "{version} - {grabbed}".format(version=self.version, grabbed=self.grabbed)
