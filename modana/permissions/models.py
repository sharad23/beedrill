from django.db import models
from helpers.models import BaseModel


class Permission(BaseModel):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=50)
    method = models.CharField(max_length=50)
    app_label = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=500, blank=True)

    class Meta:
        unique_together = (("name", "method"),)

    def __str__(self):
        return "{} ; {} ; {}".format(self.name, self.url, self.method)


class Role(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    alias = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=100)
    permissions = models.ManyToManyField(
        Permission, related_name="roles", blank=True)
    precedence = models.IntegerField(default=0)

    def get_basic_info(self):
        return {"idx": self.idx, "name": self.name, "alias": self.alias}

    def __str__(self):
        return self.name
