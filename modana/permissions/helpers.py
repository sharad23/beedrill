import os
import importlib
import re
import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from permissions.exceptions import InstallationException
from permissions.models import Permission, Role

HTTP_METHODS = ["get", "post", "put", "patch", "delete"]

REST_ACTIONS = [
    "create", "list", "update", "destroy",
    "partial_update", "retrieve"]

CREATE_PERMISSION_MSG = "Please create permission for url '{}' and method '{}' \
	at permission.models.permission."


def get_ui_permissions_for(user):
    """
    These permissions determine which UI components to be shown to whom.
    It is based upon the url name and method.
    e.g. If a user cannot access post-list url, the POS menu won't be shown at the
    client (web and mobile app).
    """
    if not user.is_authenticated():
        return []

    role_permission_map = {
        "Superuser": [
            ("servicelog-refresh", "get"),
            ("dealer-list", "get"),
            ("fee-detail", "delete"),
            ("deposit-failure-list", "get"),
            ("consumer-sms", "post"),
        ],
        "Consumer": [
            ("profile-list", "post"),
            ("userreferral-list", "get"),
        ],
        "Dealer level 1": [
            ("pos-list", "get"),
            ("business-profile-list", "post")
        ],
        "Dealer level 2": [
            ("pos-list", "get"),
            ("business-profile-list", "post")
        ],
        "Dealer level 3": [
            ("pos-list", "get"),
            ("business-profile-list", "post")
        ],
        "POS": [
            ("business-profile-list", "post"),
            ("service-sms-inform", "get")
        ],
        # "Dishhome reseller": [
        # 	("business-profile-list", "post")
        # ],
        "Offline merchant": [
            ('qrcode-download', 'get'),
            ("business-profile-list", 'post')
        ],
        "Flight Support": [
            ("flight-support", "get")
        ],
        "KYC checker": [
            ("profile-detail", "get"),
        ],
        "Service Support": [
            ("servicelog-list", "get"),
            ("servicelog-refresh", "get")
        ],
        "Native merchant": [
            ("apikey-detail", "get"),
            ("transaction-list", "get"),
            ("native-merchant-staff-list", "get"),
            ("dealer-list", "get"),
            ("pos-list", "get"),
            ("offline-merchant-list", "get"),
            ("commission-list", "get"),
            ("fund-load-initiate", "get")
        ],
        "Native merchant dealer manager": [
            ("dealer-list", "get"),
            ("servicelog-list", "get")
        ],
        "Native merchant POS manager": [
            ("pos-list", "get"),
            ("emailsignature-list", "post"),
            ("servicelog-list", "get")
        ],
        "Offline merchant manager": [
            ("offline-merchant-list", "get"),
            ("servicelog-list", "get")
        ],
        "Merchant manager": [
            ("merchant-list", "get"),
        ],
        "POS transfer agent manager": [
            ("transfer-agent-list", "get"),
        ],
        "Bank": [
            ('bank-detail', 'get'),
        ],
        "Pushmessage staff": [
            ("pushmessage-list", "get")
        ],
        "Accountant": [
            ("deposit-failure-list", "get")
        ],
        "Quizmaster": [
            ('quizquestion-list', 'post')
        ]
    }

    permissions = []
    for role in user.roles.all():
        permission_map = role_permission_map.get(role.name)
        if not permission_map:
            continue

        for permission in permission_map:
            permissions.append(permission)

    return permissions


def remove_special_characters(string):
    return string.replace("\n", "").replace("\t", "").strip()


def get_detail(action):
    """
    Get __doc__ string from action.
    """

    return remove_special_characters(action.__doc__ or "")


def intersects(list1, list2):
    if (len(set(list1).intersection(set(list2))) > 0):
        return True
    else:
        return False


def is_django_function_view(url):
    # django function view
    # no cls
    if not getattr(url.callback, "cls", None) and \
            not getattr(url.callback, "view_class", None):
        return True
    else:
        return False


def is_django_class_view(url):
    # APIView
    # any of get/post/put/patch/delete/
    cls = getattr(url.callback, "cls", None) or \
          getattr(url.callback, "view_class", None)
    if not cls or re.search("WrappedAPIView", str(url.callback)):
        return False

    if intersects(HTTP_METHODS, dir(cls)):
        return True
    else:
        return False


def is_rest_decorated_view(url):
    # @api_view
    # WrappedAPIView
    if re.search("WrappedAPIView", str(url.callback)):
        return True
    else:
        return False


def is_rest_model_viewset(url):
    # ModelViewSet
    # any of list/retrieve/destroy/update/partial_update and queryset is present
    try:
        cls = getattr(url.callback, "cls")
        if intersects(REST_ACTIONS, dir(cls)) and cls.queryset.model:
            return True
        else:
            return False
    except AttributeError:
        return False


def is_rest_non_model_viewset(url):
    # ViewSet
    # no list/retrieve/destroy/update/partial_update
    # TODO: check for fund-load/initiate, fund-load/verify
    try:
        cls = getattr(url.callback, "cls")
        frags = url.name.split("-")
        frags.pop(0)
        action = "_".join(frags)
        if getattr(cls, action):
            if intersects(REST_ACTIONS, dir(cls)):
                return False
            else:
                return True
                # cls.queryset.model
    except (AttributeError, ValueError):
        return False


def get_django_function_view_action(url):
    return url.callback


def get_django_class_view_action(url, method):
    cls = getattr(url.callback, "cls", None) or \
          getattr(url.callback, "view_class")
    try:
        return getattr(cls, method)
    except AttributeError:
        return None


def get_rest_decorated_view_action(url):
    return url.callback


def get_rest_model_viewset_action(url, action_name):
    cls = getattr(url.callback, "cls")
    try:
        return getattr(cls, action_name)
    except AttributeError:
        return None


def get_rest_non_model_viewset_action(url):
    cls = getattr(url.callback, "cls")
    frags = url.name.split("-")

    def get_action(frags):
        try:
            frags.pop(0)
            action_name = "_".join(frags)
            return getattr(cls, action_name)
        except AttributeError:
            return get_action(frags)

    return get_action(frags)


def user_has_permission(user, name, method):
    # try:
    # Permission.objects.get(
    # 	name=name, method=method, roles__in=user.roles.all())
    # 	return True
    # except ObjectDoesNotExist:
    # 	return False
    return Permission.objects.filter(
        name=name, method=method, roles__in=user.roles.all()).count() > 0


def unverified_user_has_permission(user, name, method):
    # for unverified users, we only allow access to whitelisted URLs
    # and URLs accessible by anonymous users
    unverified_user_whitelist = [
        "verification-page",
        "verify-link",
        "verify-verification-code",
        "send-verification-code"
    ]
    if name in unverified_user_whitelist:
        return True
    else:
        return anon_has_permission(name, method)


def anon_has_permission(name, method):
    try:
        permission = Permission.objects.get(name=name, method=method)
    except ObjectDoesNotExist:
        return False
    permission_roles = permission.roles.all().values_list("id", flat=True)
    try:
        anon_role = Role.objects.get(name="Anonymous").id
    except ObjectDoesNotExist:
        raise InstallationException(
            "Please create an 'Anonymous' role at 'permission.models.Role'.")

    if anon_role in permission_roles:
        return True
    return False


def has_permission(user, name, method):
    """
    Current user and name of permission which is usually name of a url.
    Except for rest url which is model_name-action-name. e.g. fee-retrieve
    """

    if user.is_authenticated():
        if user.is_verified:
            return user_has_permission(user, name, method)
        else:
            return unverified_user_has_permission(user, name, method)
    else:
        return anon_has_permission(name, method)
    return False


def get_django_function_view_permission(url):
    return [{
        "method": "any",
        "detail": get_detail(get_django_function_view_action(url))
    }]


def get_django_class_view_permission(url):
    # http_methods = ["get", "post", "put", "patch", "delete", "options"]
    http_methods = ["get", "post", "put", "patch", "delete"]
    permissions = []
    for method in http_methods:
        action = get_django_class_view_action(url, method)
        if action:
            permissions.append({
                "method": method,
                "detail": get_detail(action)
            })
    return permissions


def get_rest_decorated_view_permission(url):
    permissions = []
    for method in url.callback.cls.http_method_names:
        if method == "options":
            continue
        permissions.append({
            "method": method,
            "detail": get_detail(get_rest_decorated_view_action(url))
        })
    return permissions


def get_rest_model_viewset_permission(url):
    detail_action_map = {
        "retrieve": "get",
        "destroy": "delete",
        "update": "put",
        "partial_update": "patch"}
    #   "options": "options"}
    list_action_map = {
        "list": "get",
        "create": "post"}
    #   "options": "options"}
    permissions = []
    if re.match(r".*?-detail", url.name):
        for action_name in detail_action_map.keys():
            action = get_rest_model_viewset_action(url, action_name)
            if action:
                permissions.append({
                    "method": detail_action_map[action_name],
                    "detail": get_detail(action)
                })
    elif re.match(r".*?-list", url.name):
        for action_name in list_action_map.keys():
            action = get_rest_model_viewset_action(url, action_name)
            if action:
                permissions.append({
                    "method": list_action_map[action_name],
                    "detail": get_detail(action)
                })
    else:
        return get_rest_non_model_viewset_permission(url)

    return permissions


def get_rest_non_model_viewset_permission(url):
    action = get_rest_non_model_viewset_action(url)
    permissions = []
    for method in action.bind_to_methods:
        permissions.append({
            "method": method,
            "detail": remove_special_characters(action.__doc__ or "")
        })
    return permissions


def get_permission(url):
    """
    returns map of permission name and http method.
    """

    if is_django_function_view(url):
        return get_django_function_view_permission(url)
    if is_rest_decorated_view(url):
        return get_rest_decorated_view_permission(url)
    if is_rest_model_viewset(url):
        return get_rest_model_viewset_permission(url)
    if is_rest_non_model_viewset(url):
        return get_rest_non_model_viewset_permission(url)
    if is_django_class_view(url):
        return get_django_class_view_permission(url)


# def flatten(nested_list):
# 	return itertools.chain(*nested_list)

def regex2keyword(m):
    if m:
        return ":{}".format(m.groups()[0])
    return None


def normalize_url(url):
    t = url.replace("^", "").replace("$", "")

    if t == "":
        return url

    if not t[0] == "/":
        t = "/{}".format(t)

    if not t[-1] == "/":
        t = "{}/".format(t)

    t = re.sub(r"\(\?P<(.*?)>.*?\)", regex2keyword, t)

    return t


def get_url_meta(url):
    """
    returns url_name, url, permission_name and detail
    """
    return {
        "name": url.name,
        "url": normalize_url(str(url.pattern)),
        # get_permission returns action type present in that url
        "permissions": get_permission(url)

    }


def get_urls_for(app_name):
    try:
        urlpatterns = importlib.import_module("{}.urls".format(app_name)).urlpatterns

    except ImportError:
        return []

    urls = []
    for url in urlpatterns:
        url_meta = get_url_meta(url)
        if url_meta:
            url_meta['app_label'] = app_name
            urls.append(url_meta)
    return urls


def get_apps():
    return set(settings.NATIVE_APPS)


def get_urls(exclude=[], filtero=""):
    apps = get_apps()
    urls = []
    for app in apps.difference(set(exclude)):
        result = get_urls_for(app)
        urls.append(result)

    # return urls
    return list(filter(
        lambda aurl: re.search(filtero, aurl['url']), flatten(urls)
    ))


def create_permissions():
    """
    Creates permissions.
    """

    Permission.objects.all().delete()
    permissions = []

    urls = get_urls()
    for url in urls:
        for permission in url['permissions']:
            try:
                permissions.append(
                    Permission(
                        name=url['name'],
                        url=url['url'],
                        method=permission['method'],
                        description=permission['detail'],
                        app_label=url['app_label']
                    ))
            except IntegrityError:
                msg = "It seems multiple urls share same name '{}' and method '{}'. \
				Please make sure to override 'base_name' keyword in router.".format(
                    url["name"], permission["method"])
                raise Exception(msg)
    Permission.objects.bulk_create(permissions)


def get_url_for_client(user):
    url_maps = get_urls(exclude=[])

    new_map = {}
    for url_map in url_maps:
        url_name = url_map['name']

        if not url_name:
            raise InstallationException("Please name url: {}".format(url_map['url']))

        new_map[url_name] = {'url': url_map['url']}
        new_map[url_name]['permissions'] = {}
        for permission in url_map['permissions']:
            method = permission['method']
            new_map[url_name]['permissions'][method] = has_permission(
                user, url_map['name'], method)

    return new_map


def attach_permissions(role_name, permissions):
    """
    Attaches permissions to given role.
    """

    # uncomment for debug
    # print(role_name)
    role = Role.objects.get(name=role_name)
    permission_objs = []

    for permission in permissions:
        # uncomment for debug
        # print(permission)
        try:
            permission_objs.append(
                Permission.objects.get(name=permission[0], method=permission[1]))
        except Exception as e:
            raise Exception("{}".format(permission), e)

    role.permissions.add(*permission_objs)
    role.save()


def flatten(nested_permissions):
    return [
        permission for permission_list in nested_permissions
        for permission in permission_list]


def assign_permissions():
    """
    Assigns permissions to corresponding roles.
    """

    for role, permissions in PERMISSION_MAP.items():
        attach_permissions(role, flatten(permissions))


def update_permissions():
    """
    Creates permissions and assign them to respective roles.
    """

    create_permissions()
    assign_permissions()
    print("List of permissions", Permission.objects.all().count())


def flush_permissions():
    try:
        Permission.flush()
        print("All the permission flushed")
    except Exception as e:
        print("Some problem occurred " + str(e))


TEST_PAGE = [
    ("testmodel-list", "get"),
    ("testmodel-list", "post")
]

TEST_ANOTHER_PAGE = [
    ("testmodel-detail", "get"),
    ("testmodel-detail", "put"),
    ("testmodel-detail", "patch"),
    ("testmodel-detail", "delete"),
]

PERMISSION_MAP = {
    "company_admin": [
        TEST_PAGE,
        TEST_ANOTHER_PAGE
    ]
}
