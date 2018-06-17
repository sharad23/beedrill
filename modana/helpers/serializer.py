from rest_framework import serializers

from helpers.serializer_fields import FRelatedField


class FModelSerializer(serializers.ModelSerializer):
    serializer_related_field = FRelatedField
    idx = serializers.CharField(read_only=True)

    class Meta:
        exclude = ("id", "modified_on", "is_obsolete")
        extra_kwargs = {
            "created_on": {"read_only": True},
            "modified_on": {"read_only": True}
        }
