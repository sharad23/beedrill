from rest_framework.exceptions import APIException


class ParameterNotFoundException(APIException):
    status_code = 400
    default_detail = 'Parameter Not Found'


class DbIntergrityException(APIException):
    status_code = 400
    default_detail = 'Parameter Not Found'