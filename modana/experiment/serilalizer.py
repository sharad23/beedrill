from rest_framework import serializers
from experiment.models import TestModel


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestModel
        fields = '__all__'
