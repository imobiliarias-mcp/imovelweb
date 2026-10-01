"""Domain entities for Imovelweb rental property listings."""

from dataclasses import dataclass
from scripts.domain.value_objects import ListingPrice, PropertyCode


@dataclass(frozen=True)
class ListingIdentity:
    """Core identification fields for an Imovelweb listing."""

    code: PropertyCode
    title: str


@dataclass(frozen=True)
class ListingValuation:
    """Monetary pricing and recurring expenses for an Imovelweb listing."""

    rental_price: ListingPrice
    expenses: ListingPrice


@dataclass(frozen=True)
class ListingSpecs:
    """Area and room counts for a listing."""

    dimensions: str
    room_summary: str


@dataclass(frozen=True)
class ListingLocation:
    """Street and locality geographical summary."""

    street: str
    locality: str


@dataclass(frozen=True)
class ListingCore:
    """Combines identification and valuation attributes."""

    identity: ListingIdentity
    valuation: ListingValuation


@dataclass(frozen=True)
class ListingDetails:
    """Supplementary specifications and location data."""

    specs: ListingSpecs
    location: ListingLocation


@dataclass(frozen=True)
class ListingMedia:
    """Primary image thumbnail and canonical relative URL path."""

    thumbnail_url: str
    url_path: str


@dataclass(frozen=True)
class ListingPresentation:
    """Presentation components combining details and media."""

    details: ListingDetails
    media: ListingMedia


@dataclass(frozen=True)
class RentalListing:
    """Lightweight rental listing model for Imovelweb search results."""

    core: ListingCore
    presentation: ListingPresentation

    def code(self) -> str:
        """Return business listing code."""
        return self.core.identity.code.value()

    def title(self) -> str:
        """Return public display title."""
        return self.core.identity.title

    def format_summary(self) -> str:
        """Format listing into a readable single-line summary."""
        code_str = self.core.identity.code.value()
        price_str = self.core.valuation.rental_price.format_brl()
        loc_str = self.presentation.details.location.locality
        specs_str = self.presentation.details.specs.room_summary
        return f"[{code_str}] {loc_str} - {specs_str} - {price_str}/mês"

    def to_dictionary(self) -> dict:
        """Export entity into a plain dictionary representation."""
        return {
            "code": self.core.identity.code.value(),
            "title": self.core.identity.title,
            "rental_price": self.core.valuation.rental_price.value(),
            "rental_price_formatted": self.core.valuation.rental_price.format_brl(),
            "expenses": self.core.valuation.expenses.value(),
            "street": self.presentation.details.location.street,
            "locality": self.presentation.details.location.locality,
            "dimensions": self.presentation.details.specs.dimensions,
            "room_summary": self.presentation.details.specs.room_summary,
            "thumbnail_url": self.presentation.media.thumbnail_url,
            "url_path": self.presentation.media.url_path,
        }


@dataclass(frozen=True)
class DetailedProfile:
    """Extended description and features for an Imovelweb property."""

    description: str
    features_summary: str


@dataclass(frozen=True)
class PublisherInfo:
    """Realtor or publisher agency details."""

    name: str
    logo_url: str


@dataclass(frozen=True)
class PropertyDetailContext:
    """Supplemental detail context combining profile and publisher."""

    profile: DetailedProfile
    publisher: PublisherInfo


@dataclass(frozen=True)
class RentalPropertyDetail:
    """Comprehensive rental property detail view."""

    listing: RentalListing
    context: PropertyDetailContext

    def format_detailed_view(self) -> str:
        """Format full property information into structured text."""
        summary = self.listing.format_summary()
        pub_name = self.context.publisher.name
        features = self.context.profile.features_summary
        desc = self.context.profile.description
        return f"{summary}\nAnunciante: {pub_name}\nRecursos: {features}\n\nDescrição:\n{desc}"

    def to_dictionary(self) -> dict:
        """Export detailed property into dictionary representation."""
        base_dict = self.listing.to_dictionary()
        base_dict["publisher_name"] = self.context.publisher.name
        base_dict["publisher_logo"] = self.context.publisher.logo_url
        base_dict["features"] = self.context.profile.features_summary
        base_dict["description"] = self.context.profile.description
        return base_dict
