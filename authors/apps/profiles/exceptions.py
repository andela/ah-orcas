from rest_framework.exceptions import APIException


class ProfileDoesNotExist(APIException):
    """
    This class handles DoesNotExist exception
    """
    status_code = 400
    default_detail = 'The requested profile does not exist.'
