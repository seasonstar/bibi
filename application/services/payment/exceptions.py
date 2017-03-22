class WXPayException(Exception):
    '''Base Alipay Exception'''


class MissingParameter(WXPayException):
    """Raised when the create payment url process is missing some
    parameters needed to continue"""


class ParameterValueError(WXPayException):
    """Raised when parameter value is incorrect"""


class TokenAuthorizationError(WXPayException):
    '''The error occurred when getting token '''
