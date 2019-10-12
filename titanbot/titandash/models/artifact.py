from django.db import models
from django.conf import settings

from titandash.models.mixins import ExportModelMixin


TIER_HELP_TEXT = {
    "tier": "Specify the tier.",
    "name": "Specify the readable name associated with this tier."
}


class Tier(models.Model, ExportModelMixin):
    """
    Tier Model.

    Store a tier by the character that represents it.
    """
    class Meta:
        verbose_name = "Tier"
        verbose_name_plural = "Tiers"

    tier = models.CharField(verbose_name="Tier", primary_key=True, max_length=255, help_text=TIER_HELP_TEXT["tier"])
    name = models.CharField(verbose_name="Name", max_length=255, help_text=TIER_HELP_TEXT["name"])

    def __str__(self):
        return "{name}".format(name=self.name)

    def export_key(self):
        return self.tier

    def import_model(self, export_kwargs):
        pass

    @staticmethod
    def import_model_kwargs(export_string, compression_keys=None):
        pass

    def json(self):
        return {
            "tier": self.tier,
            "name": self.name
        }


ARTIFACT_HELP_TEXT = {
    "name": "Specify the name of this artifact.",
    "tier": "Specify the tier associated with this artifact.",
    "key": "Specify the key of this artifact.",
    "image": "Specify the image path that leads to this artifact."
}


class ArtifactManager(models.Manager):
    """
    Allow for custom QuerySet method when retrieving artifacts.
    """
    def tier(self, tier, as_list=False, ignore=None):
        """
        Retrieve all artifacts of the specified tier.
        """
        if ignore is None:
            ignore = []

        arts = self.all().filter(tier__tier=tier)

        # Return artifacts as a flat list if specified.
        if as_list:
            return arts.exclude(name__in=ignore).values_list("name", flat=True)
        else:
            return arts.exclude(name__in=ignore)


class Artifact(models.Model, ExportModelMixin):
    """
    Artifact Model.

    Store an instance of an artifact. Containing a name, tier and key.
    """
    class Meta:
        verbose_name = "Artifact"
        verbose_name_plural = "Artifacts"

    objects = ArtifactManager()
    name = models.CharField(verbose_name="Name", max_length=255, help_text=ARTIFACT_HELP_TEXT["name"])
    tier = models.ForeignKey(verbose_name="Tier", to="Tier", on_delete=models.CASCADE, help_text=ARTIFACT_HELP_TEXT["tier"])
    key = models.PositiveIntegerField(verbose_name="Key", help_text=ARTIFACT_HELP_TEXT["key"])
    image = models.CharField(verbose_name="Image", max_length=255, help_text=ARTIFACT_HELP_TEXT["image"])

    def __str__(self):
        from titandash.utils import title
        return "{name} ({key}) - [{tier}]".format(name=title(self.name), key=self.key, tier=self.tier)

    def export_key(self):
        return self.key

    @staticmethod
    def import_model_kwargs(export_string, compression_keys=None):
        pass

    def import_model(self, export_kwargs):
        pass

    @property
    def title(self):
        """
        Return a titled version of the artifact name.
        """
        from titandash.utils import title
        return title(self.name)

    def json(self):
        """
        Return Artifact as a JSON Compliant Object.
        """
        return {
            "name": self.name,
            "title": self.title,
            "key": self.key,
            "image": self.image,
            "path": "{dir}{path}".format(dir=settings.STATIC_URL, path=self.image)
        }
