"""Search criteria and filter value objects for Imovelweb."""

from dataclasses import dataclass
from scripts.domain.exceptions import InvalidFilterException
from scripts.domain.value_objects import (
    BedroomConstraint,
    ListingPrice,
    PageNumber,
)


@dataclass(frozen=True)
class SearchBudget:
    """Represents a validated monetary budget interval."""

    minimum_price: ListingPrice
    maximum_price: ListingPrice

    def __post_init__(self) -> None:
        """Validate that minimum price does not exceed maximum price."""
        has_positive_maximum = self.maximum_price.value() > 0.0
        is_inverted = self.minimum_price.value() > self.maximum_price.value()
        if has_positive_maximum and is_inverted:
            raise InvalidFilterException("Minimum price cannot exceed maximum price.")

    @classmethod
    def create_unbounded(cls) -> "SearchBudget":
        """Create an open budget range."""
        zero_min = ListingPrice(0.0)
        zero_max = ListingPrice(0.0)
        return cls(minimum_price=zero_min, maximum_price=zero_max)


@dataclass(frozen=True)
class LocationCriteria:
    """Represents geographical search destination filters."""

    city: str = ""
    neighborhood: str = ""


@dataclass(frozen=True)
class SpecificationCriteria:
    """Represents property type and bedroom constraints."""

    property_type: str = ""
    bedrooms: BedroomConstraint = BedroomConstraint()


@dataclass(frozen=True)
class SearchPagination:
    """Represents pagination and sorting settings."""

    page_number: PageNumber = PageNumber(1)
    sort_order: str = ""


@dataclass(frozen=True)
class SearchConstraints:
    """Combines budget and pagination/sort constraints."""

    budget: SearchBudget = SearchBudget.create_unbounded()
    pagination: SearchPagination = SearchPagination()


@dataclass(frozen=True)
class RentalSearchCriteria:
    """Combines location and typology specification criteria."""

    location: LocationCriteria = LocationCriteria()
    specifications: SpecificationCriteria = SpecificationCriteria()


@dataclass(frozen=True)
class RentalFilter:
    """Comprehensive immutable rental search filter."""

    criteria: RentalSearchCriteria = RentalSearchCriteria()
    constraints: SearchConstraints = SearchConstraints()

    def with_city(self, city_name: str) -> "RentalFilter":
        """Return a copy with specified city."""
        current_nb = self.criteria.location.neighborhood
        new_loc = LocationCriteria(city=city_name, neighborhood=current_nb)
        new_crit = RentalSearchCriteria(location=new_loc, specifications=self.criteria.specifications)
        return RentalFilter(criteria=new_crit, constraints=self.constraints)

    def with_neighborhood(self, neighborhood_name: str) -> "RentalFilter":
        """Return a copy with specified neighborhood."""
        current_city = self.criteria.location.city
        new_loc = LocationCriteria(city=current_city, neighborhood=neighborhood_name)
        new_crit = RentalSearchCriteria(location=new_loc, specifications=self.criteria.specifications)
        return RentalFilter(criteria=new_crit, constraints=self.constraints)

    def with_property_type(self, property_type: str) -> "RentalFilter":
        """Return a copy with specified property type."""
        curr_beds = self.criteria.specifications.bedrooms
        new_specs = SpecificationCriteria(property_type=property_type, bedrooms=curr_beds)
        new_crit = RentalSearchCriteria(location=self.criteria.location, specifications=new_specs)
        return RentalFilter(criteria=new_crit, constraints=self.constraints)

    def with_bedrooms(self, count: int) -> "RentalFilter":
        """Return a copy with exact bedroom count."""
        bed_constraint = BedroomConstraint(minimum=count, maximum=count)
        curr_type = self.criteria.specifications.property_type
        new_specs = SpecificationCriteria(property_type=curr_type, bedrooms=bed_constraint)
        new_crit = RentalSearchCriteria(location=self.criteria.location, specifications=new_specs)
        return RentalFilter(criteria=new_crit, constraints=self.constraints)

    def with_bedroom_range(self, minimum: int, maximum: int) -> "RentalFilter":
        """Return a copy with bedroom range."""
        bed_constraint = BedroomConstraint(minimum=minimum, maximum=maximum)
        curr_type = self.criteria.specifications.property_type
        new_specs = SpecificationCriteria(property_type=curr_type, bedrooms=bed_constraint)
        new_crit = RentalSearchCriteria(location=self.criteria.location, specifications=new_specs)
        return RentalFilter(criteria=new_crit, constraints=self.constraints)

    def with_page(self, page: int) -> "RentalFilter":
        """Return a copy with specified page number."""
        page_vo = PageNumber(page)
        curr_sort = self.constraints.pagination.sort_order
        new_pag = SearchPagination(page_number=page_vo, sort_order=curr_sort)
        new_constraints = SearchConstraints(budget=self.constraints.budget, pagination=new_pag)
        return RentalFilter(criteria=self.criteria, constraints=new_constraints)

    def with_sort(self, sort_order: str) -> "RentalFilter":
        """Return a copy with specified sort order."""
        curr_page = self.constraints.pagination.page_number
        new_pag = SearchPagination(page_number=curr_page, sort_order=sort_order)
        new_constraints = SearchConstraints(budget=self.constraints.budget, pagination=new_pag)
        return RentalFilter(criteria=self.criteria, constraints=new_constraints)

    def with_price_ceiling(self, ceiling: ListingPrice) -> "RentalFilter":
        """Return a copy with upper price bound."""
        curr_min = self.constraints.budget.minimum_price
        new_budget = SearchBudget(minimum_price=curr_min, maximum_price=ceiling)
        new_constraints = SearchConstraints(budget=new_budget, pagination=self.constraints.pagination)
        return RentalFilter(criteria=self.criteria, constraints=new_constraints)
