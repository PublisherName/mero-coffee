class PayPalPaymentError(Exception):
    """Base exception for PayPal payment errors"""


class PayPalOrderFetchError(PayPalPaymentError):
    """Raised when fetching PayPal order fails"""


class PayPalTransactionNotFoundError(PayPalPaymentError):
    """Raised when transaction is not found"""


class PayPalCaptureError(PayPalPaymentError):
    """Raised when payment capture fails"""


class PayPalOrderCreationError(PayPalPaymentError):
    """Raised when order creation fails"""
