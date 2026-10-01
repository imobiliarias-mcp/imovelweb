"""Domain exceptions for Imovelweb rental research."""


class ImovelwebException(Exception):
    """Base exception for all Imovelweb research domain errors."""


class InvalidPriceException(ImovelwebException):
    """Raised when a monetary price is invalid or negative."""


class InvalidPropertyCodeException(ImovelwebException):
    """Raised when a property listing code is empty or malformed."""


class InvalidFilterException(ImovelwebException):
    """Raised when search filter criteria are inconsistent or invalid."""


class PropertyNotFoundException(ImovelwebException):
    """Raised when a requested property cannot be found on the portal."""


class ParsingException(ImovelwebException):
    """Raised when parsing an HTML document or embedded data fails."""


class TransportException(ImovelwebException):
    """Raised when an HTTP or browser transport network operation fails."""
