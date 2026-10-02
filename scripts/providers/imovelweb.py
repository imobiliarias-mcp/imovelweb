"""Imovelweb rental search provider implementation."""

from scripts.client.configuration import ImovelwebConfiguration
from scripts.client.http_transport import (
    BrowserTransport,
    ImovelwebTransportProtocol,
)
from scripts.client.parsers import (
    FacetParser,
    PropertyDetailParser,
    SearchResultParser,
)
from scripts.client.query_builder import ImovelwebQueryBuilder
from scripts.domain.collections import FacetCollection, RentalSearchResult
from scripts.domain.criteria import RentalFilter
from scripts.domain.entities import RentalPropertyDetail
from scripts.domain.value_objects import PropertyCode
from scripts.interfaces.provider import RentalProviderProtocol


class ImovelwebRentalProvider(RentalProviderProtocol):
    """Adapter implementing RentalProviderProtocol for Imovelweb portal."""

    def __init__(
        self,
        transport: ImovelwebTransportProtocol,
        query_builder: ImovelwebQueryBuilder,
    ) -> None:
        """Initialize provider with transport and query builder."""
        self._transport = transport
        self._builder = query_builder

    @classmethod
    def create_default(cls) -> "ImovelwebRentalProvider":
        """Factory method constructing provider with default configurations."""
        config = ImovelwebConfiguration()
        transport = BrowserTransport(configuration=config)
        builder = ImovelwebQueryBuilder(configuration=config)
        return cls(transport=transport, query_builder=builder)

    def provider_name(self) -> str:
        """Return unique provider identifier for central MCP registry."""
        return "imovelweb"

    def search_rentals(self, search_filter: RentalFilter) -> RentalSearchResult:
        """Search rental listings using criteria."""
        search_url = self._builder.build_search_url(search_filter)
        html_content = self._transport.get_html(search_url)
        parser = SearchResultParser(query_builder=self._builder)
        return parser.parse_search_response(html_content)

    def get_property_detail(self, code: PropertyCode) -> RentalPropertyDetail:
        """Retrieve full details for a single property by code."""
        detail_url = self._builder.build_property_detail_url(code)
        html_content = self._transport.get_html(detail_url)
        parser = PropertyDetailParser(query_builder=self._builder)
        return parser.parse_detail_response(html_content)

    def get_facets(self) -> FacetCollection:
        """Retrieve available cities, neighborhoods, and filter options."""
        facets_url = self._builder.build_facets_url()
        html_content = self._transport.get_html(facets_url)
        parser = FacetParser()
        return parser.parse_facets_response(html_content)
