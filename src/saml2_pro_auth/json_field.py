"""
Hacky patch to make JSONField work in sqlite for our tests.
"""
from django.conf import settings

if "sqlite" in settings.DATABASES["default"]["ENGINE"]:

    import json

    from django import forms
    from django.core import exceptions
    from django.db.models import Field
    from django.forms.widgets import Textarea
    from django.utils.translation import gettext_lazy as _

    class InvalidJSONInput(str):
        pass

    class JSONString(str):
        pass

    class JSONFormField(forms.CharField):
        default_error_messages = {
            "invalid": _("Enter a valid JSON."),
        }
        widget = Textarea

        def __init__(self, encoder=None, decoder=None, **kwargs):
            self.encoder = encoder
            self.decoder = decoder
            super().__init__(**kwargs)

        def to_python(self, value):
            if self.disabled:
                return value
            if value in self.empty_values:
                return None
            elif isinstance(value, (list, dict, int, float, JSONString)):
                return value
            try:
                converted = json.loads(value, cls=self.decoder)
            except json.JSONDecodeError:
                raise exceptions.ValidationError(
                    self.error_messages["invalid"],
                    code="invalid",
                    params={"value": value},
                )
            if isinstance(converted, str):
                return JSONString(converted)
            else:
                return converted

        def bound_data(self, data, initial):
            if self.disabled:
                return initial
            try:
                return json.loads(data, cls=self.decoder)
            except json.JSONDecodeError:
                return InvalidJSONInput(data)

        def prepare_value(self, value):
            if isinstance(value, InvalidJSONInput):
                return value
            return json.dumps(value, ensure_ascii=False, cls=self.encoder)

        def has_changed(self, initial, data):
            if super().has_changed(initial, data):
                return True
            # For purposes of seeing whether something has changed, True isn't the
            # same as 1 and the order of keys doesn't matter.
            return json.dumps(initial, sort_keys=True, cls=self.encoder) != json.dumps(
                self.to_python(data), sort_keys=True, cls=self.encoder
            )

    class JSONField(Field):
        empty_strings_allowed = False
        description = _("A JSON object")
        default_error_messages = {
            "invalid": _("Value must be valid JSON."),
        }
        _default_hint = ("dict", "{}")

        def db_type(self, connection):
            return "text"

        def from_db_value(self, value, expression, connection):
            if value is None:
                return value
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        def get_prep_value(self, value):
            if value is None:
                return value
            return json.dumps(value)

        def validate(self, value, model_instance):
            super().validate(value, model_instance)
            try:
                json.dumps(value)
            except TypeError:
                raise exceptions.ValidationError(
                    self.error_messages["invalid"],
                    code="invalid",
                    params={"value": value},
                )

        def value_to_string(self, obj):
            return self.value_from_object(obj)

        def formfield(self, **kwargs):
            return super().formfield(
                **{
                    "form_class": JSONFormField,
                    **kwargs,
                }
            )
