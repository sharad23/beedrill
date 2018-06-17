from django.db import models
from helpers.models import BaseModel
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)
from autho.exceptions import (
    ParameterNotFoundException,
    DbIntergrityException
)
from django.db import IntegrityError
from permissions.models import Role
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation
)


class UserManager(BaseUserManager):
    def create_user(self, email, username, phone_number, password):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ParameterNotFoundException(detail='Email needed')

        if not username:
            raise ParameterNotFoundException(detail='Username needed')

        if not phone_number:
            raise ParameterNotFoundException(detail='Phone Number needed')

        try:
            user = self.model(
                email=self.normalize_email(email),
                username=username,
                phone_number=phone_number,
            )

            user.set_password(password)
            user.save(using=self._db)

        except IntegrityError as e:
            raise DbIntergrityException(detail=str(e))

        return user

    def create_company(self, **kwargs):
        user = self.create_user(**kwargs)
        user.roles.add(Role.objects.get(name='company'))
        return user

    def create_employee(self, **kwargs):
        user = self.create_user(**kwargs)
        user.roles.add(Role.objects.get(name='employee'))
        return user

    def create_admin(self, **kwargs):
        user = self.create_user(**kwargs)
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    phone_number = models.IntegerField(unique=True)
    roles = models.ManyToManyField(Role, related_name='users')
    profile_ct = models.ForeignKey(
        ContentType,
        limit_choices_to={"model__in": ("CompanyProfile", "EmployeeProfile")},
        related_name="user",
        on_delete=models.SET_NULL,
        null=True)
    profile_id = models.PositiveIntegerField(null=True)
    profile = GenericForeignKey('profile_ct', 'profile_id')
    profile_pic = models.ImageField(
        upload_to='profile_pics/',
        null=True, blank=True,
    )
    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number']

    def __str__(self):
        return self.email


class CompanyProfile(BaseModel):
    user = GenericRelation(
        User,
        on_delete=models.SET_NULL,
        related_query_name="user_profiles",
        content_type_field='profile_ct',
        object_id_field='profile_id',
    )


class EmployeeProfile(BaseModel):
    user = GenericRelation(
        User,
        on_delete=models.SET_NULL,
        related_query_name="user_profiles",
        content_type_field='profile_ct',
        object_id_field='profile_id',
    )
