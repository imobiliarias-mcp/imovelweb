"""Model Context Protocol (MCP) tool adapters for Central Rental Research."""

from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import ListingPrice, PropertyCode
from scripts.interfaces.provider import RentalProviderProtocol
from scripts.providers.imovelweb import ImovelwebRentalProvider


class ImovelwebMcpAdapter:
    """Adapts domain rental provider for consumption by MCP servers and tool registries."""

    def __init__(self, provider: RentalProviderProtocol) -> None:
        """Initialize adapter with an abstract rental provider."""
        self._provider = provider

    @classmethod
    def create_default(cls) -> "ImovelwebMcpAdapter":
        """Factory constructor instantiating the default Imovelweb provider."""
        default_provider = ImovelwebRentalProvider.create_default()
        return cls(provider=default_provider)

    def _apply_bedrooms(self, target: RentalFilter, exact: int, min_beds: int, max_beds: int) -> RentalFilter:
        """Apply bedroom constraints to search filter."""
        if min_beds > 0 and max_beds > 0:
            return target.with_bedroom_range(min_beds, max_beds)
        if exact > 0:
            return target.with_bedrooms(exact)
        return target

    def _assemble_filter(
        self,
        city: str,
        exact_bedrooms: int,
        min_bedrooms: int,
        max_bedrooms: int,
        page: int,
        property_type: str,
        sort: str,
    ) -> RentalFilter:
        """Construct a validated RentalFilter from tool arguments."""
        working = RentalFilter().with_page(page)
        if city:
            working = working.with_city(city)
        if property_type:
            working = working.with_property_type(property_type)
        if sort:
            working = working.with_sort(sort)
        return self._apply_bedrooms(working, exact_bedrooms, min_bedrooms, max_bedrooms)

    def search_rentals(
        self,
        city: str = "",
        bedrooms: int = 0,
        min_bedrooms: int = 0,
        max_bedrooms: int = 0,
        property_type: str = "",
        sort_order: str = "",
        page: int = 1,
    ) -> dict:
        """Execute a rental property search for an MCP tool call."""
        flt = self._assemble_filter(city, bedrooms, min_bedrooms, max_bedrooms, page, property_type, sort_order)
        search_result = self._provider.search_rentals(flt)
        return search_result.to_dictionary()

    def get_property_detail(self, property_code: str) -> dict:
        """Retrieve complete property detail for an MCP tool call."""
        code_vo = PropertyCode(property_code)
        property_detail = self._provider.get_property_detail(code_vo)
        return property_detail.to_dictionary()

    def get_facets(self) -> dict:
        """Retrieve available search facets for an MCP tool call."""
        facet_collection = self._provider.get_facets()
        return facet_collection.to_dictionary()

    def get_provider_info(self) -> dict:
        """Retrieve metadata about this rental provider adapter."""
        name = self._provider.provider_name()
        return {
            "provider_name": name,
            "coverage_region": "Timóteo, Vale do Aço, Minas Gerais, Brasil",
            "supported_operations": ["search_rentals", "get_property_detail", "get_facets"],
        }
