"""First-class collections for Imovelweb search results and facets."""

from dataclasses import dataclass
from typing import Iterator
from scripts.domain.entities import RentalListing


@dataclass(frozen=True)
class ListingCollection:
    """First-class collection wrapping rental listings."""

    items: tuple[RentalListing, ...] = ()

    def __len__(self) -> int:
        """Return total items in collection."""
        return len(self.items)

    def __iter__(self) -> Iterator[RentalListing]:
        """Iterate over listings."""
        return iter(self.items)

    def __getitem__(self, index: int) -> RentalListing:
        """Access listing by index."""
        return self.items[index]

    def is_empty(self) -> bool:
        """Check if collection has zero elements."""
        return len(self.items) == 0

    def to_list(self) -> list[dict]:
        """Convert collection to list of dictionaries."""
        return [item.to_dictionary() for item in self.items]


@dataclass(frozen=True)
class PaginationMetadata:
    """Metadata regarding current search pagination state."""

    current_page: int
    total_count: int

    def page_size(self) -> int:
        """Imovelweb fixed listing page size."""
        return 30


@dataclass(frozen=True)
class RentalSearchResult:
    """First-class domain result for a rental search execution."""

    listings: ListingCollection
    pagination: PaginationMetadata

    def total_count(self) -> int:
        """Return total items found across all pages."""
        return self.pagination.total_count

    def current_page(self) -> int:
        """Return current 1-indexed page number."""
        return self.pagination.current_page

    def page_count(self) -> int:
        """Return count of items on current page."""
        return len(self.listings)

    def to_dictionary(self) -> dict:
        """Serialize search result into structured dictionary."""
        return {
            "current_page": self.pagination.current_page,
            "total_count": self.pagination.total_count,
            "page_items_count": len(self.listings),
            "listings": self.listings.to_list(),
        }


@dataclass(frozen=True)
class FacetOption:
    """Single selectable facet option."""

    label: str
    value: str


@dataclass(frozen=True)
class FacetGroup:
    """Group of related facet options."""

    name: str
    options: tuple[FacetOption, ...]

    def to_dictionary(self) -> dict:
        """Convert facet group to dictionary."""
        return {
            "name": self.name,
            "options": [{"label": opt.label, "value": opt.value} for opt in self.options],
        }


@dataclass(frozen=True)
class FacetCollection:
    """First-class collection of available search facets."""

    groups: tuple[FacetGroup, ...] = ()

    def to_dictionary(self) -> dict:
        """Convert all facet groups to dictionary."""
        return {group.name: group.to_dictionary()["options"] for group in self.groups}
