class PayPalPaymentError(Exception):
    """Base exception for PayPal payment errors"""

    pass


class PayPalOrderFetchError(PayPalPaymentError):
    """Raised when fetching PayPal order fails"""

    pass


class PayPalTransactionNotFoundError(PayPalPaymentError):
    """Raised when transaction is not found"""

    pass


class PayPalCaptureError(PayPalPaymentError):
    """Raised when payment capture fails"""

    pass


class PayPalOrderCreationError(PayPalPaymentError):
    """Raised when order creation fails"""

    pass
