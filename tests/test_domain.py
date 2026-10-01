"""Unit tests for Imovelweb domain value objects, criteria, and entities."""

import pytest
from scripts.domain.criteria import (
    LocationCriteria,
    RentalFilter,
    RentalSearchCriteria,
    SearchBudget,
    SearchConstraints,
    SearchPagination,
    SpecificationCriteria,
)
from scripts.domain.entities import (
    DetailedProfile,
    ListingCore,
    ListingDetails,
    ListingIdentity,
    ListingLocation,
    ListingMedia,
    ListingPresentation,
    ListingSpecs,
    ListingValuation,
    PropertyDetailContext,
    PublisherInfo,
    RentalListing,
    RentalPropertyDetail,
)
from scripts.domain.exceptions import (
    InvalidFilterException,
    InvalidPriceException,
    InvalidPropertyCodeException,
)
from scripts.domain.value_objects import (
    BedroomConstraint,
    GeoCoordinate,
    ListingPrice,
    PageNumber,
    PropertyCode,
)


def test_listing_price_validation() -> None:
    """Ensure price rejects negative numbers and formats BRL."""
    price = ListingPrice(1400.0)
    assert price.value() == 1400.0
    assert price.format_brl() == "R$ 1.400,00"
    assert not price.is_zero()

    zero_price = ListingPrice(0.0)
    assert zero_price.is_zero()

    with pytest.raises(InvalidPriceException):
        ListingPrice(-10.0)


def test_property_code_validation() -> None:
    """Ensure property code rejects empty or whitespace-only strings."""
    code = PropertyCode("3037421600")
    assert code.value() == "3037421600"
    assert str(code) == "3037421600"

    with pytest.raises(InvalidPropertyCodeException):
        PropertyCode("   ")


def test_geo_coordinate_validation() -> None:
    """Ensure coordinates validate geospatial bounds."""
    coord = GeoCoordinate(-19.58, -42.64)
    assert coord.is_valid()
    assert coord.format_coordinates() == "(-19.580000, -42.640000)"

    zero_coord = GeoCoordinate(0.0, 0.0)
    assert not zero_coord.is_valid()


def test_bedroom_constraint_slug_formatting() -> None:
    """Ensure bedroom constraints format correct canonical slugs."""
    unbounded = BedroomConstraint()
    assert unbounded.format_slug_part() == ""

    exact_one = BedroomConstraint(1, 1)
    assert exact_one.is_exact()
    assert exact_one.format_slug_part() == "-1-quarto"

    exact_two = BedroomConstraint(2, 2)
    assert exact_two.is_exact()
    assert exact_two.format_slug_part() == "-2-quartos"

    range_one_two = BedroomConstraint(1, 2)
    assert range_one_two.is_range()
    assert range_one_two.format_slug_part() == "-desde-1-ate-2-quartos"

    min_two = BedroomConstraint(2, 0)
    assert min_two.is_minimum_only()
    assert min_two.format_slug_part() == "-mais-de-2-quartos"

    with pytest.raises(InvalidFilterException):
        BedroomConstraint(minimum=3, maximum=1)


def test_page_number_validation() -> None:
    """Ensure page numbers reject values below 1."""
    p1 = PageNumber(1)
    assert p1.is_first_page()
    assert p1.format_slug_part() == ""

    p2 = PageNumber(2)
    assert not p2.is_first_page()
    assert p2.format_slug_part() == "-pagina-2"

    with pytest.raises(InvalidFilterException):
        PageNumber(0)


def test_search_budget_validation() -> None:
    """Ensure budget prevents inverted price ranges."""
    budget = SearchBudget(ListingPrice(500.0), ListingPrice(1500.0))
    assert budget.minimum_price.value() == 500.0
    assert budget.maximum_price.value() == 1500.0

    with pytest.raises(InvalidFilterException):
        SearchBudget(ListingPrice(2000.0), ListingPrice(1000.0))


def test_rental_filter_builder_methods() -> None:
    """Ensure rental filter builds immutable copies with updated criteria."""
    base_filter = RentalFilter()
    with_city = base_filter.with_city("timoteo")
    with_nb = with_city.with_neighborhood("centro")
    with_beds = with_nb.with_bedroom_range(1, 2)
    with_page = with_beds.with_page(2)
    with_sort = with_page.with_sort("menor_preco")

    assert with_sort.criteria.location.city == "timoteo"
    assert with_sort.criteria.location.neighborhood == "centro"
    assert with_sort.criteria.specifications.bedrooms.minimum == 1
    assert with_sort.criteria.specifications.bedrooms.maximum == 2
    assert with_sort.constraints.pagination.page_number.value() == 2
    assert with_sort.constraints.pagination.sort_order == "menor_preco"


def test_rental_listing_and_detail_formatting() -> None:
    """Ensure listing entities format readable summaries."""
    identity = ListingIdentity(PropertyCode("3037421600"), "Casa em Recanto Verde")
    valuation = ListingValuation(ListingPrice(1400.0), ListingPrice(0.0))
    core = ListingCore(identity=identity, valuation=valuation)
    specs = ListingSpecs("50 m²", "1 quarto · 1 banheiro")
    location = ListingLocation("Rua Manacá", "Recanto Verde, Timóteo")
    details = ListingDetails(specs=specs, location=location)
    media = ListingMedia("https://img.example/1.jpg", "/propriedades/casa-1.html")
    presentation = ListingPresentation(details=details, media=media)
    listing = RentalListing(core=core, presentation=presentation)

    summary = listing.format_summary()
    assert "[3037421600]" in summary
    assert "R$ 1.400,00/mês" in summary

    profile = DetailedProfile("Linda casa reformada", "Garagem, Quintal")
    pub = PublisherInfo("BUSKAZA", "https://img.example/logo.jpg")
    context = PropertyDetailContext(profile=profile, publisher=pub)
    detail = RentalPropertyDetail(listing=listing, context=context)

    detailed_text = detail.format_detailed_view()
    assert "Linda casa reformada" in detailed_text
    assert "Anunciante: BUSKAZA" in detailed_text
