"""Regression tests for unsupported price bounds in canonical search routes."""

import pytest

from scripts.client.configuration import ImovelwebConfiguration
from scripts.client.query_builder import ImovelwebQueryBuilder
from scripts.domain.criteria import RentalFilter, SearchBudget, SearchConstraints
from scripts.domain.exceptions import InvalidFilterException
from scripts.domain.value_objects import ListingPrice


@pytest.mark.parametrize("minimum,maximum", ((650, 0), (0, 1600), (650, 1600)))
def test_price_bounds_are_not_silently_ignored(minimum, maximum):
    """Nonzero budgets fail explicitly until price routing is supported."""
    budget = SearchBudget(ListingPrice(minimum), ListingPrice(maximum))
    search_filter = RentalFilter(constraints=SearchConstraints(budget=budget))
    builder = ImovelwebQueryBuilder(ImovelwebConfiguration())
    with pytest.raises(InvalidFilterException, match="Price bounds"):
        builder.build_search_url(search_filter)


def test_unbounded_budget_keeps_existing_search_route():
    """An unbounded budget keeps the validated canonical rental route."""
    builder = ImovelwebQueryBuilder(ImovelwebConfiguration())
    url = builder.build_search_url(RentalFilter())
    assert url == "https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg.html"
