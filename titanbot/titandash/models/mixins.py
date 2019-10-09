"""
mixins.py

Store any mixins or generic functionality that can be used by other models here.
"""
from titandash.constants import (
    GENERIC_BLACKLIST, M2M_SEPARATOR, ATTR_SEPARATOR, VALUE_SEPARATOR,
    BOOLEAN_PREFIX, M2M_PREFIX, FK_PREFIX
)


class ExportModelMixin(object):
    """
    Add mixin functionality to export a model into a shareable formatted string.
    """
    def export_key(self):
        raise NotImplementedError()

    @staticmethod
    def import_model_kwargs(export_string, compression_keys=None):
        raise NotImplementedError()

    @staticmethod
    def import_model(export_kwargs):
        """
        Given a set of export kwargs with proper information, create the models import functionality.
        """
        raise NotImplementedError()

    def export_model(self, compression_keys=None, blacklist=None):
        """
        Export a specific model. We use the export key of our model to ensure keys are unique and can be imported back
        with information that exists regardless of the database it's being imported into.
        """
        if compression_keys is None:
            compression_keys = {}
        if blacklist is None:
            blacklist = []

        attrs = []
        for field in [f for f in self._meta.get_fields() if not f.one_to_many and f.name not in GENERIC_BLACKLIST]:
            if field.name in blacklist:
                continue

            field_value = getattr(self, field.name)
            # Using a compression key to make our export string smaller?
            compression_key = compression_keys.get(field.name, field.name)

            # Maybe its a relational field, if so, we make use of the "key" value
            # on the model... This should be a unique identifier on the model
            # that isn't the PK, because the PK could be different for different instance.s
            if field.many_to_one:
                value = FK_PREFIX + str(field_value.export_key())
            elif field.many_to_many:
                if len([v.export_key() for v in field_value.all()]) == 0:
                    value = M2M_PREFIX + "None".format(sep=M2M_PREFIX)
                else:
                    value = M2M_PREFIX + M2M_SEPARATOR.join([str(v.export_key()) for v in field_value.all()])

            # Normal field value being used?
            else:
                if field_value is True or field_value is False:
                    value = "{boolean_prefix}{boolean}".format(boolean_prefix=BOOLEAN_PREFIX, boolean=str(field_value)[0])
                else:
                    value = field_value

            value = "{name}{sep}{value}".format(name=compression_key, sep=VALUE_SEPARATOR, value=value)
            attrs.append(value)

        # We have all attributes we need, compress them and return output.
        return ATTR_SEPARATOR.join(attrs)
