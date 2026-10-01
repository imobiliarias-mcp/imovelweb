"""Value objects wrapping domain primitives for Imovelweb."""

from dataclasses import dataclass
from scripts.domain.exceptions import (
    InvalidFilterException,
    InvalidPriceException,
    InvalidPropertyCodeException,
)


@dataclass(frozen=True)
class ListingPrice:
    """Represents a validated monetary price in Brazilian Reais."""

    amount: float

    def __post_init__(self) -> None:
        """Validate non-negative monetary amount."""
        if self.amount < 0.0:
            raise InvalidPriceException(f"Price cannot be negative: {self.amount}")

    def format_brl(self) -> str:
        """Format the monetary amount into Brazilian currency string."""
        formatted_number = f"{self.amount:,.2f}"
        localized = formatted_number.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {localized}"

    def is_zero(self) -> bool:
        """Check if price is zero."""
        return self.amount == 0.0

    def value(self) -> float:
        """Return raw numeric value."""
        return self.amount


@dataclass(frozen=True)
class PropertyCode:
    """Represents a unique real estate listing identifier."""

    identifier: str

    def __post_init__(self) -> None:
        """Validate non-empty code identifier."""
        cleaned = self.identifier.strip()
        if not cleaned:
            raise InvalidPropertyCodeException("Property code cannot be empty.")

    def value(self) -> str:
        """Return clean identifier string."""
        return self.identifier.strip()

    def __str__(self) -> str:
        """String representation."""
        return self.value()


@dataclass(frozen=True)
class GeoCoordinate:
    """Represents geographical latitude and longitude coordinates."""

    latitude: float
    longitude: float

    def is_valid(self) -> bool:
        """Check if coordinates fall within real geospatial bounds."""
        if self.latitude == 0.0 and self.longitude == 0.0:
            return False
        is_lat_valid = -90.0 <= self.latitude <= 90.0
        is_lng_valid = -180.0 <= self.longitude <= 180.0
        return is_lat_valid and is_lng_valid

    def format_coordinates(self) -> str:
        """Return coordinates formatted as string."""
        return f"({self.latitude:.6f}, {self.longitude:.6f})"


@dataclass(frozen=True)
class BedroomConstraint:
    """Represents bedroom range constraint for search queries."""

    minimum: int = 0
    maximum: int = 0

    def __post_init__(self) -> None:
        """Validate non-negative bedroom values."""
        if self.minimum < 0 or self.maximum < 0:
            raise InvalidFilterException("Bedrooms count cannot be negative.")
        has_max = self.maximum > 0
        if has_max and self.minimum > self.maximum:
            raise InvalidFilterException("Minimum bedrooms cannot exceed maximum.")

    def is_unbounded(self) -> bool:
        """Check if no bedroom constraint is active."""
        return self.minimum == 0 and self.maximum == 0

    def is_exact(self) -> bool:
        """Check if filter specifies an exact bedroom count."""
        return self.minimum > 0 and self.minimum == self.maximum

    def is_range(self) -> bool:
        """Check if filter specifies a range between min and max."""
        return self.minimum > 0 and self.maximum > self.minimum

    def is_minimum_only(self) -> bool:
        """Check if filter specifies only a lower bound."""
        return self.minimum > 0 and self.maximum == 0

    def format_slug_part(self) -> str:
        """Format into canonical Imovelweb URL slug fragment."""
        if self.is_unbounded():
            return ""
        if self.is_exact():
            plural = "quarto" if self.minimum == 1 else "quartos"
            return f"-{self.minimum}-{plural}"
        if self.is_range():
            return f"-desde-{self.minimum}-ate-{self.maximum}-quartos"
        return f"-mais-de-{self.minimum}-quartos"


@dataclass(frozen=True)
class PageNumber:
    """Represents a validated 1-indexed pagination number."""

    number: int = 1

    def __post_init__(self) -> None:
        """Validate page number is at least 1."""
        if self.number < 1:
            raise InvalidFilterException("Page number must be at least 1.")

    def value(self) -> int:
        """Return raw integer value."""
        return self.number

    def is_first_page(self) -> bool:
        """Check if this is page 1."""
        return self.number == 1

    def format_slug_part(self) -> str:
        """Format into canonical Imovelweb pagination slug."""
        if self.is_first_page():
            return ""
        return f"-pagina-{self.number}"
