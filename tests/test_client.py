"""Unit tests for Imovelweb provider and MCP adapter using StubTransport."""

from pathlib import Path

from scripts import run_search
from scripts.client.configuration import ImovelwebConfiguration
from scripts.client.http_transport import StubTransport
from scripts.client.parsers import SearchResultParser
from scripts.client.query_builder import ImovelwebQueryBuilder
from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import PropertyCode
from scripts.mcp.tools import ImovelwebMcpAdapter
from scripts.providers.imovelweb import ImovelwebRentalProvider

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class CountingStubTransport(StubTransport):
    """Count deterministic transport calls made during the request path."""

    def __init__(self, responses: dict[str, str]) -> None:
        super().__init__(responses)
        self.requested_urls: list[str] = []

    def get_html(self, url: str) -> str:
        self.requested_urls.append(url)
        return super().get_html(url)


def test_provider_search_with_stub() -> None:
    """Ensure search returns domain collection from stubbed transport."""
    search_html = (FIXTURES_DIR / "search_page.html").read_text(encoding="utf-8")
    stub_responses = {
        "imoveis-aluguel-timoteo-mg-desde-1-ate-2-quartos.html": search_html,
    }
    transport = CountingStubTransport(stub_responses)
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
    transport = CountingStubTransport(stub_responses)
    config = ImovelwebConfiguration()
    builder = ImovelwebQueryBuilder(config)
    provider = ImovelwebRentalProvider(transport=transport, query_builder=builder)

    detail = provider.get_property_detail(PropertyCode("3037421600"))
    assert detail.listing.code() == "3037421600"
    assert detail.listing.core.valuation.rental_price.value() == 1400.0
    assert detail.context.publisher.name == "BUSKAZA"


def test_provider_uses_query_builder_public_base_without_detail_fetches() -> None:
    """Resolve card links against custom public config using only the search request."""
    search_html = (FIXTURES_DIR / "search_page.html").read_text(encoding="utf-8")
    transport = CountingStubTransport({"imoveis-aluguel-timoteo": search_html})
    configuration = ImovelwebConfiguration(base_url="https://listings.example")
    builder = ImovelwebQueryBuilder(configuration)
    provider = ImovelwebRentalProvider(transport=transport, query_builder=builder)

    results = provider.search_rentals(RentalFilter().with_city("timoteo"))

    assert results.listings[0].to_dictionary()["url"].startswith("https://listings.example/")
    assert len(transport.requested_urls) == 1


def test_search_runner_prints_each_public_property_url(monkeypatch, capsys) -> None:
    """Include the public listing URL beside each textual search result."""
    search_html = (FIXTURES_DIR / "search_page.html").read_text(encoding="utf-8")

    class StubProvider:
        def search_rentals(self, search_filter: RentalFilter):
            return SearchResultParser().parse_search_response(search_html)

    monkeypatch.setattr(
        run_search.ImovelwebRentalProvider, "create_default", lambda: StubProvider()
    )
    run_search.main()

    output = capsys.readouterr().out
    assert "Link: https://www.imovelweb.com.br/propriedades/casa-para-aluguel" in output


def test_mcp_adapter_with_stub() -> None:
    """Ensure MCP adapter translates tool parameters into provider calls."""
    search_html = (FIXTURES_DIR / "search_page.html").read_text(encoding="utf-8")
    detail_html = (FIXTURES_DIR / "detail_page.html").read_text(encoding="utf-8")
    stub_responses = {
        "imoveis-aluguel-timoteo-mg-desde-1-ate-2-quartos.html": search_html,
        "propriedades/imovel-3037421600.html": detail_html,
        "imoveis-aluguel-timoteo-mg.html": search_html,
    }
    transport = CountingStubTransport(stub_responses)
    config = ImovelwebConfiguration()
    builder = ImovelwebQueryBuilder(config)
    provider = ImovelwebRentalProvider(transport=transport, query_builder=builder)
    adapter = ImovelwebMcpAdapter(provider=provider)

    info = adapter.get_provider_info()
    assert info["provider_name"] == "imovelweb"

    search_dict = adapter.search_rentals(city="timoteo", min_bedrooms=1, max_bedrooms=2)
    assert search_dict["total_count"] == 8
    assert len(search_dict["listings"]) == 8
    assert search_dict["listings"][0]["url"].startswith(
        "https://www.imovelweb.com.br/propriedades/casa-para-aluguel"
    )
    assert search_dict["listings"][0]["url_path"].startswith("/propriedades/")
    assert len(transport.requested_urls) == 1

    detail_dict = adapter.get_property_detail("3037421600")
    assert detail_dict["code"] == "3037421600"
    assert detail_dict["rental_price"] == 1400.0
    assert detail_dict["publisher_name"] == "BUSKAZA"
