"""Domain entities for Imovelweb rental property listings."""

from dataclasses import dataclass
from urllib.parse import urlsplit

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
class ListingNavigation:
    """Public property URL and its legacy relative path."""

    public_url: str
    url_path: str


@dataclass(frozen=True, init=False)
class ListingMedia:
    """Thumbnail and navigation data, grouped to retain a two-field model."""

    thumbnail_url: str
    navigation: ListingNavigation

    def __init__(
        self,
        thumbnail_url: str,
        url_path: ListingNavigation | str,
        public_url: str | None = None,
    ) -> None:
        """Accept legacy url_path arguments or an explicit navigation bundle."""
        navigation_data = url_path
        if isinstance(url_path, str):
            navigation_data = ListingNavigation(public_url or url_path, url_path)
        object.__setattr__(self, "thumbnail_url", thumbnail_url)
        object.__setattr__(self, "navigation", navigation_data)

    @property
    def url_path(self) -> str:
        """Expose the preserved relative property path."""
        navigation = self.navigation
        return navigation.url_path

    @property
    def url(self) -> str:
        """Expose the resolved public property URL."""
        navigation = self.navigation
        return navigation.public_url


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

    def _validated_public_url(self) -> str:
        """Require an absolute web URL and include listing context on failure."""
        presentation = self.presentation
        media = presentation.media
        public_url = media.url
        return self._validate_absolute_public_url(public_url)

    def _validate_absolute_public_url(self, public_url: str) -> str:
        """Validate the scheme and host of a pre-resolved public URL."""
        try:
            parsed_url = urlsplit(public_url)
        except ValueError as error:
            raise self._public_url_error(public_url) from error
        valid_scheme = parsed_url.scheme in {"http", "https"}
        has_host = bool(parsed_url.hostname)
        has_credentials = parsed_url.username is not None or parsed_url.password is not None
        if not valid_scheme or not has_host or has_credentials:
            raise self._public_url_error(public_url)
        return public_url

    def _public_url_error(self, public_url: str) -> ValueError:
        """Build a contextual serialization error for this listing."""
        code = self.code()
        message = f"Imovelweb listing {code} requires an absolute public URL: {public_url}"
        return ValueError(message)

    def to_dictionary(self) -> dict:
        """Export entity into a plain dictionary representation."""
        presentation = self.presentation
        media = presentation.media
        navigation = media.navigation
        public_url = self._validated_public_url()
        return {
            "code": self.core.identity.code.value(),
            "title": self.core.identity.title,
            "rental_price": self.core.valuation.rental_price.value(),
            "rental_price_formatted": self.core.valuation.rental_price.format_brl(),
            "expenses": self.core.valuation.expenses.value(),
            "street": presentation.details.location.street,
            "locality": presentation.details.location.locality,
            "dimensions": presentation.details.specs.dimensions,
            "room_summary": presentation.details.specs.room_summary,
            "thumbnail_url": media.thumbnail_url,
            "url_path": navigation.url_path,
            "url": public_url,
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
