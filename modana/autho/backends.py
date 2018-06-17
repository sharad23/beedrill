# from django.conf.settings import AUTH_USER_MODEL
# from django.contrib.auth.backends import ModelBackend
#
# class EmailOrUsernameModelBackend(ModelBackend):
#     """
#     This is a ModelBacked that allows authentication with either a username or an email address.
#
#     """
#     def authenticate(self, username=None, password=None):
#         User = settings.AUTH_USER_MODEL
#         if '@' in username:
#             kwargs = {'email': username}
#         else:
#             kwargs = {'username': username}
#         try:
#             user = User.objects.get(**kwargs)
#             if user.check_password(password):
#                 return user
#         except User.DoesNotExist:
#             return None
#
#     def get_user(self, username):
#         try:
#             return User.objects.get(pk=username)
#         except User.DoesNotExist:
#             return None