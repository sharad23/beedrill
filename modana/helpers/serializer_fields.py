import re
import json
from io import BytesIO

from rest_framework import serializers
from rest_framework.fields import (
    get_attribute, is_simple_callable
)
import pytz
from PIL import Image

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __


class CompressionImageField(serializers.ImageField):
    portrait_size = 1280, 720
    landscape_size = 720, 1280

    def _get_new_size(self, value):
        h, w = value.image.size
        if h > w:
            # if height is higher than it is a portrait
            return self.portrait_size
        else:
            return self.landscape_size

    def _needs_resize(self, value, size):
        h, w = value.image.size
        needs_scale = h > size[0] or w > size[1]

        one_mb = 1024 * 1024
        needs_resize = value.size > one_mb
        return needs_scale or needs_resize

    def to_internal_value(self, value):
        value = super().to_internal_value(value)
        h, w = value.image.size

        new_size = self._get_new_size(value)

        if self._needs_resize(value, new_size):
            output = BytesIO()

            image = Image.open(BytesIO(value.read()))
            image.thumbnail(new_size)
            image.save(output, format=image.format)

            value.file = output

        return value


class TzDateTimeField(serializers.DateTimeField):
    """
    Timezone aware DateTimeField for DRF.
    """

    def to_representation(self, obj):
        default_timezone = pytz.timezone(settings.TIME_ZONE)
        obj = obj.astimezone(default_timezone)
        date = super(TzDateTimeField, self).to_representation(obj)
        # format date here or just by pass above super call
        return date


def validate_name_length(value):
    if len(value) > 50:
        raise serializers.ValidationError("Name should not exceed 50 characters in length.")


def validate_delimiter(value, delimiter):
    """
    Ensure that delimiters such as hyphen, slash, comma don't
    fall at the start or end of the input value
    """
    message = "Separator ({}) must not be at the {} of the value."
    if value.startswith(delimiter):
        raise serializers.ValidationError(message.format(delimiter, "start"))

    if value.endswith(delimiter):
        raise serializers.ValidationError(message.format(delimiter, "end"))


def validate_yyyy_mm_dd(value):
    match = re.match('^(?P<year>\d{4})\-(?P<month>\d{1,2})\-(?P<day>\d{1,2})$', value)
    if match:
        d = match.groupdict()
        if int(d['month']) not in range(1, 13):
            raise serializers.ValidationError("Please enter a valid month.")

        if int(d['day']) not in range(1, 33):
            raise serializers.ValidationError("Please enter a valid day.")

        if int(d['year'][:2]) not in [19, 20]:
            raise serializers.ValidationError("Please enter a valid year.")
    else:
        raise serializers.ValidationError("Please enter a valid date in YYYY-MM-DD format.")
    return value


class DateCharField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs['min_length'] = 8
        kwargs['max_length'] = 10
        super().__init__(**kwargs)

    def to_internal_value(self, value):
        value = str(value).strip()
        validate_yyyy_mm_dd(value)
        return value


class HyphenAlphaNumericCharField(serializers.CharField):
    """
    This field only allows alphanumeric characters, hyphens and spaces.
    """

    def to_internal_value(self, value):
        value = str(value).strip()
        validate_delimiter(value, "-")

        if not value.replace(' ', '').replace('-', '').isalnum():
            raise serializers.ValidationError(
                "This field should contain alphabets, numbers, hyphen and space only."
            )
        return value


class NameField(serializers.CharField):
    def to_internal_value(self, name):
        name = name.strip()
        name = " ".join(map(lambda x: x.capitalize(), name.split()))
        validate_name_length(name)

        if not name.replace(' ', '').isalpha():
            raise serializers.ValidationError(
                "Name should contain alphabets and space only."
            )

        if not re.match("[a-zA-Z]{2,}(\s[a-zA-Z]{2,})+", name):
            raise serializers.ValidationError("Please pass full name.")

        return name


class CompanyNameField(HyphenAlphaNumericCharField):
    def to_internal_value(self, value):
        validate_name_length(value)
        return super().to_internal_value(value)


class RegNumberField(serializers.CharField):
    """
    Some numbers might contain hyphens and slashes such as
    citizenship number, company registration number etc.
    """

    def to_internal_value(self, value):
        value = str(value)
        if not value.replace(' ', '').replace('-', '').replace('/', '').isalnum():
            raise serializers.ValidationError(
                "This field can contain alphabets, numbers, hyphen and slash only."
            )

        if '-' in value and '/' in value:
            raise serializers.ValidationError("Please use either slash or hyphen and not both.")

        validate_delimiter(value, "-")
        validate_delimiter(value, "/")
        return value


class NumericCharField(serializers.CharField):
    """
    Fields such as PAN number
    """

    def to_internal_value(self, value):
        if not value.isnumeric():
            raise serializers.ValidationError(
                "This field can contain numeric characters only."
            )
        return value


class MobileField(serializers.CharField):
    def to_internal_value(self, mobile):
        if not len(str(mobile)) == 10:
            raise serializers.ValidationError("A mobile number should be 10 digit long.")

        if not re.match("9[678][0124568]\d{7}", str(mobile)):
            raise serializers.ValidationError("Invalid mobile number.")

        return mobile


class VirtualMobileField(serializers.CharField):
    def to_internal_value(self, mobile):
        if not len(str(mobile)) == 10:
            raise serializers.ValidationError(
                "Virtual mobile number must be 10 digits long."
            )

        if not settings.VIRTUAL_MOBILE_REGEX.match(str(mobile)):
            raise serializers.ValidationError(
                "Mobile number must have a 100 prefix."
            )
        return mobile


class PasswordField(serializers.CharField):
    def to_internal_value(self, password):
        if len(password) < 8:
            raise serializers.ValidationError("The password should at least be 8 characters long.")
        if len(password) > 50:
            raise serializers.ValidationError("The password should be shorter than 50 characters.")

        return password


class DetailRelatedField(serializers.RelatedField):
    """
    Read/write serializer field for relational field.
    Syntax:
        DetailRelatedField(Model, [lookup], representation)

        Model: model to which the serializer field is related to
        lookup: field for getting a model instance, if not supplied it defaults to idx
        representation: a model instance method name for getting serialized data
    """

    def __init__(self, model, **kwargs):
        if not kwargs.get("read_only"):
            kwargs["queryset"] = model.objects.all()

        self.lookup = kwargs.pop("lookup", None) or "idx"

        try:
            self.representation = kwargs.pop("representation")
        except KeyError:
            raise Exception("Please supply representation.")

        super(DetailRelatedField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            return self.queryset.get(**{self.lookup: data})
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Object does not exist.")

    def to_representation(self, obj):
        return getattr(obj, self.representation)()


class SpecificFieldsMixin(object):
    """
    Returns fields specified in query params 'fields'.
    """

    def __init__(self, *args, **kwargs):
        super(SpecificFieldsMixin, self).__init__(*args, **kwargs)

        if not self.context or not self.context.get("request"):
            return

        if self.context.get("request").method != "get":
            return

        fields = self.context["request"].query_params.get("fields")
        if fields:
            fields = fields.split(",")
            requested_fields = set(fields)
            available_fields = set(self.fields.keys())
            for field_name in available_fields - requested_fields:
                self.fields.pop(field_name)


class IDXOnlyObject:
    def __init__(self, idx):
        self.idx = idx

    def __str__(self):
        return "%s" % self.idx


class FRelatedField(serializers.PrimaryKeyRelatedField):
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _('Invalid idx "{pk_value}" - object does not exist.'),
        'incorrect_type': _('Incorrect type. Expected idx value, received {data_type}.'),
    }

    def get_attribute(self, instance):
        if self.use_pk_only_optimization() and self.source_attrs:
            # Optimized case, return a mock object only containing the pk attribute.
            try:
                instance = get_attribute(instance, self.source_attrs[:-1])
                value = instance.serializable_value(self.source_attrs[-1])
                if is_simple_callable(value):
                    # Handle edge case where the relationship `source` argument
                    # points to a `get_relationship()` method on the model
                    value = value().idx
                else:
                    value = getattr(instance, self.source_attrs[-1]).idx
                return IDXOnlyObject(idx=value)
            except AttributeError:
                pass

    def to_representation(self, obj):
        return obj.idx

    def to_internal_value(self, data):
        try:
            return self.queryset.get(idx=data)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)


class I18NField(serializers.CharField):
    """
    Converts i18n key-string to user selected language.
    """

    def to_representation(self, key_string):
        return __(key_string)


class JSONField(serializers.CharField):
    def to_representation(self, data):
        return json.loads(data)
