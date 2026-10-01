"""Unit tests for Imovelweb search and detail parsers using fixtures."""

from pathlib import Path
import pytest
from scripts.client.parsers import (
    FacetParser,
    PropertyDetailParser,
    SearchResultParser,
)
from scripts.domain.exceptions import PropertyNotFoundException

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_search_result_parser_with_fixture() -> None:
    """Ensure search parser extracts all 8 listings and metadata."""
    html_file = FIXTURES_DIR / "search_page.html"
    assert html_file.exists(), "search_page.html fixture must exist"
    html_content = html_file.read_text(encoding="utf-8")

    parser = SearchResultParser()
    result = parser.parse_search_response(html_content)

    assert result.total_count() == 8
    assert result.current_page() == 1
    assert result.page_count() == 8
    assert len(result.listings) == 8

    first_card = result.listings[0]
    assert first_card.code() == "3037421600"
    assert first_card.core.valuation.rental_price.value() == 1400.0
    assert first_card.presentation.details.location.locality == "Recanto Verde, Timóteo"
    assert "Manacá" in first_card.presentation.details.location.street
    assert "propriedades" in first_card.presentation.media.url_path
    assert "imovelwebcdn" in first_card.presentation.media.thumbnail_url


def test_property_detail_parser_with_fixture() -> None:
    """Ensure detail parser extracts avisoInfo and property attributes."""
    html_file = FIXTURES_DIR / "detail_page.html"
    assert html_file.exists(), "detail_page.html fixture must exist"
    html_content = html_file.read_text(encoding="utf-8")

    parser = PropertyDetailParser()
    detail = parser.parse_detail_response(html_content)

    assert detail.listing.code() == "3037421600"
    assert detail.listing.core.valuation.rental_price.value() == 1400.0
    assert "Recanto Verde" in detail.listing.title()
    assert detail.context.publisher.name == "BUSKAZA"
    assert "jardim das Flores" in detail.context.profile.description


def test_property_detail_parser_not_found_handling() -> None:
    """Ensure 404 response text triggers PropertyNotFoundException."""
    not_found_html = "<html><head><title>Não encontramos a página solicitada - Error 404</title></head><body>404</body></html>"
    parser = PropertyDetailParser()
    with pytest.raises(PropertyNotFoundException):
        parser.parse_detail_response(not_found_html)


def test_facet_parser_with_fixture() -> None:
    """Ensure facet parser extracts property types, sort orders, and neighborhoods."""
    html_file = FIXTURES_DIR / "search_page.html"
    html_content = html_file.read_text(encoding="utf-8")

    parser = FacetParser()
    facets = parser.parse_facets_response(html_content)
    facets_dict = facets.to_dictionary()

    assert "property_types" in facets_dict
    assert "sort_orders" in facets_dict
    assert "neighborhoods" in facets_dict
    assert len(facets_dict["property_types"]) > 0
    assert len(facets_dict["sort_orders"]) > 0
