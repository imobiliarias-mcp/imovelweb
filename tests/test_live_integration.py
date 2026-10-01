"""Live integration tests for Imovelweb portal communication."""

import pytest
from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import PropertyCode
from scripts.providers.imovelweb import ImovelwebRentalProvider


@pytest.mark.integration
def test_live_target_prompt_search() -> None:
    """Verify live search against target URL from prompt."""
    provider = ImovelwebRentalProvider.create_default()
    flt = (
        RentalFilter()
        .with_city("timoteo")
        .with_bedroom_range(1, 2)
    )

    result = provider.search_rentals(flt)
    assert result.total_count() > 0
    assert result.page_count() > 0
    first_listing = result.listings[0]
    assert first_listing.code() != ""
    assert first_listing.core.valuation.rental_price.value() > 0.0


@pytest.mark.integration
def test_live_property_detail_retrieval() -> None:
    """Verify live property detail retrieval by property ID."""
    provider = ImovelwebRentalProvider.create_default()
    code = PropertyCode("3037421600")

    detail = provider.get_property_detail(code)
    assert detail.listing.code() == "3037421600"
    assert detail.listing.core.valuation.rental_price.value() > 0.0
    assert detail.context.publisher.name != ""
