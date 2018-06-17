from django.db import models

from django_filters.filterset import (
	FILTER_FOR_DBFIELD_DEFAULTS,
	FilterSet,
)
from django_filters.compat import remote_queryset
from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import DjangoFilterBackend


FILTER_FOR_DBFIELD_DEFAULTS[models.OneToOneField] = {
	'filter_class': ModelChoiceFilter,
	'extra': lambda f: {
		'queryset': remote_queryset(f),
		'to_field_name': "idx",
	}
}

FILTER_FOR_DBFIELD_DEFAULTS[models.ForeignKey] = {
	'filter_class': ModelChoiceFilter,
	'extra': lambda f: {
		'queryset': remote_queryset(f),
		'to_field_name': "idx",
	}
}


class KFilterSet(FilterSet):
	FILTER_DEFAULTS = FILTER_FOR_DBFIELD_DEFAULTS


class KDjangoFilterBackend(DjangoFilterBackend):
	default_filter_set = KFilterSet


def filter_boolean(queryset, name, value):
	m = {"true": True, "false": False}
	filter = {name: m.get(value)}
	return queryset.filter(**filter)
