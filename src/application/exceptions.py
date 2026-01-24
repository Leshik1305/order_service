class ItemNotFoundError(Exception):
    """Exception raised when an item is not found."""


class IdempotencyConflictError(Exception):
    """Exception raised when no Idempotency."""


class IsAvailableQtyError(Exception):
    """Exception raised when quantity is not available"""


class PaymentCreationError(Exception):
    """Exception raised when a payment not created"""


class OrderNotFoundError(Exception):
    """Exception raised when an order is not found."""
