from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from titandash.models.configuration import Configuration


class ConfigurationForm(forms.ModelForm):
    """Configuration ModelForm."""
    def __init__(self, *args, **kwargs):
        super(ConfigurationForm, self).__init__(*args, **kwargs)

        helper = FormHelper(self)
        helper.add_input(Submit("submit", "Save", css_class="btn-primary"))
        helper.form_method = "POST"

    class Meta:
        model = Configuration
        fields = "__all__"
