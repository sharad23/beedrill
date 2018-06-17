from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from experiment.models import TestModel
from experiment.serilalizer import TestSerializer


class TestViewSet(ModelViewSet):
    permission_classes = (AllowAny, )
    queryset = TestModel.objects.all()
    serializer_class = TestSerializer

