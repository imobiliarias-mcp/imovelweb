"""Unit tests for Imovelweb provider and MCP adapter using StubTransport."""

from pathlib import Path
from scripts.client.configuration import ImovelwebConfiguration
from scripts.client.http_transport import StubTransport
from scripts.client.query_builder import ImovelwebQueryBuilder
from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import PropertyCode
from scripts.mcp.tools import ImovelwebMcpAdapter
from scripts.providers.imovelweb import ImovelwebRentalProvider

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_provider_search_with_stub() -> None:
    """Ensure search returns domain collection from stubbed transport."""
    search_html = (FIXTURES_DIR / "search_page.html").read_text(encoding="utf-8")
    stub_responses = {
        "imoveis-aluguel-timoteo-mg-desde-1-ate-2-quartos.html": search_html,
    }
    transport = StubTransport(stub_responses)
    config = ImovelwebConfiguration()
    builder = ImovelwebQueryBuilder(config)
    provider = ImovelwebRentalProvider(transport=transport, query_builder=builder)

    flt = RentalFilter().with_city("timoteo").with_bedroom_range(1, 2)
    result = provider.search_rentals(flt)

    assert result.total_count() == 8
    assert result.page_count() == 8
    assert result.listings[0].code() == "3037421600"


def test_provider_detail_with_stub() -> None:
    """Ensure property detail retrieves and parses from stubbed transport."""
    detail_html = (FIXTURES_DIR / "detail_page.html").read_text(encoding="utf-8")
    stub_responses = {
        "propriedades/imovel-3037421600.html": detail_html,
    }
    transport = StubTransport(stub_responses)
    config = ImovelwebConfiguration()
    builder = ImovelwebQueryBuilder(config)
    provider = ImovelwebRentalProvider(transport=transport, query_builder=builder)

    detail = provider.get_property_detail(PropertyCode("3037421600"))
    assert detail.listing.code() == "3037421600"
    assert detail.listing.core.valuation.rental_price.value() == 1400.0
    assert detail.context.publisher.name == "BUSKAZA"


def test_mcp_adapter_with_stub() -> None:
    """Ensure MCP adapter translates tool parameters into provider calls."""
    search_html = (FIXTURES_DIR / "search_page.html").read_text(encoding="utf-8")
    detail_html = (FIXTURES_DIR / "detail_page.html").read_text(encoding="utf-8")
    stub_responses = {
        "imoveis-aluguel-timoteo-mg-desde-1-ate-2-quartos.html": search_html,
        "propriedades/imovel-3037421600.html": detail_html,
        "imoveis-aluguel-timoteo-mg.html": search_html,
    }
    transport = StubTransport(stub_responses)
    config = ImovelwebConfiguration()
    builder = ImovelwebQueryBuilder(config)
    provider = ImovelwebRentalProvider(transport=transport, query_builder=builder)
    adapter = ImovelwebMcpAdapter(provider=provider)

    info = adapter.get_provider_info()
    assert info["provider_name"] == "imovelweb"

    search_dict = adapter.search_rentals(city="timoteo", min_bedrooms=1, max_bedrooms=2)
    assert search_dict["total_count"] == 8
    assert len(search_dict["listings"]) == 8

    detail_dict = adapter.get_property_detail("3037421600")
    assert detail_dict["code"] == "3037421600"
    assert detail_dict["rental_price"] == 1400.0
    assert detail_dict["publisher_name"] == "BUSKAZA"
