from django.db import models
from django.utils import timezone

from shortuuidfield import ShortUUIDField


class BaseModel(models.Model):
    """
    Base model for possibly every other model.
    """

    # the library does produce unique hash, but just in case
    idx = ShortUUIDField(unique=True)
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(auto_now=True)
    is_obsolete = models.BooleanField(default=False)

    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()
        return self

    @classmethod
    def new(cls, **kwargs):
        return cls.objects.create(**kwargs)

    @classmethod
    def flush(cls, force_delete=True, **kwargs):
        if force_delete:
            return cls.objects.filter(**kwargs).delete()
        else:
            return cls.objects.filter(**kwargs).update(is_obsolete=True)

    def delete(self, force_delete=True, **kwargs):
        if force_delete:
            super(BaseModel, self).delete(**kwargs)
        else:
            self.update(is_obsolete=True)
            return self

    class Meta:
        abstract = True
