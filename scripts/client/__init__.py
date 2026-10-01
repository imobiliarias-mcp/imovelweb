"""Client package exports for Imovelweb rental research."""

from scripts.client.configuration import ImovelwebConfiguration
from scripts.client.http_transport import (
    BrowserTransport,
    HttpTransport,
    ImovelwebTransportProtocol,
    StubTransport,
)
from scripts.client.parsers import (
    FacetParser,
    PropertyDetailParser,
    SearchResultParser,
)
from scripts.client.query_builder import ImovelwebQueryBuilder

__all__ = [
    "BrowserTransport",
    "FacetParser",
    "HttpTransport",
    "ImovelwebConfiguration",
    "ImovelwebQueryBuilder",
    "ImovelwebTransportProtocol",
    "PropertyDetailParser",
    "SearchResultParser",
    "StubTransport",
]
