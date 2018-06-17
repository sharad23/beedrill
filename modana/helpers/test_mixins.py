from django.test import TestCase


class TestSerializerMixin(TestCase):
    serializer = None
    model = None
    data = None
    request = None
    format_kwarg = None

    def setUp(self):
        self.context = {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def test_serializer_validation(self):
        s = self.serializer(data=self.data, context=self.context)
        self.assertEqual(s.is_valid(), True)

    def test_serializer_create(self):
        s = self.serializer(data=self.data, context=self.context)
        if s.is_valid():
            s.save()
        self.assertEqual(self.model.objects.count(), 1)
        obj = self.model.objects.first()
        self.assertEqual(isinstance(obj, self.model), True)
        for key, value in self.data.items():
            self.assertEqual(getattr(obj, key), value)

    def test_serializer_update(self, **kwargs):
        obj = kwargs.pop('obj')
        s = self.serializer(obj, data=kwargs, context=self.context)
        if s.is_valid():
            s.save()
        obj.refresh_from_db()
        for key, value in kwargs.items():
            self.assertEqual(getattr(obj, key), value)

    def test_deserialization(self, **kwargs):
        obj = kwargs.pop('obj')
        c = self.serializer(obj)
        for key, value in kwargs.items():
            self.assertEqual(c.data.get(key), value)