"""URL and query builder for Imovelweb search routing."""

import unicodedata

from scripts.client.configuration import ImovelwebConfiguration
from scripts.domain.criteria import RentalFilter
from scripts.domain.exceptions import InvalidFilterException
from scripts.domain.value_objects import PropertyCode


class ImovelwebQueryBuilder:
    """Builds canonical Imovelweb SEO routes and query URLs."""

    def __init__(self, configuration: ImovelwebConfiguration) -> None:
        """Initialize builder with portal configuration."""
        self._config = configuration

    def _slugify(self, text: str) -> str:
        """Convert arbitrary string into normalized lowercase slug."""
        normalized = unicodedata.normalize("NFKD", text)
        ascii_only = normalized.encode("ascii", "ignore").decode("utf-8")
        clean = ascii_only.strip().lower()
        slug = clean.replace(" ", "-")
        return slug

    def _determine_prefix(self, property_type: str) -> str:
        """Determine leading category slug for route."""
        cleaned = self._slugify(property_type)
        known_types = {"apartamentos", "casas", "comerciais", "terrenos", "rurais"}
        if cleaned in known_types:
            return f"{cleaned}-aluguel"
        return "imoveis-aluguel"

    def _determine_location(self, city: str, neighborhood: str) -> str:
        """Determine geographical slug component."""
        active_city = self._slugify(city) if city else self._config.default_city
        if neighborhood:
            active_nb = self._slugify(neighborhood)
            return f"-{active_nb}-{active_city}"
        return f"-{active_city}-{self._config.default_state}"

    def _determine_sort(self, sort_order: str) -> str:
        """Map sort order option into canonical slug."""
        sort_slugs = {
            "menor_preco": "-ordem-preco-menor",
            "preco_menor": "-ordem-preco-menor",
            "maior_preco": "-ordem-preco-maior",
            "preco_maior": "-ordem-preco-maior",
            "recentes": "-ordem-publicado-maior",
            "publicado_maior": "-ordem-publicado-maior",
            "visitas": "-ordem-visitas-maior",
        }
        return sort_slugs.get(sort_order.lower().strip(), "")

    def _validate_supported_budget(self, search_filter: RentalFilter) -> None:
        """Reject price bounds that cannot be encoded in supported routes."""
        budget = search_filter.constraints.budget
        minimum_price = budget.minimum_price
        maximum_price = budget.maximum_price
        if minimum_price.value() > 0 or maximum_price.value() > 0:
            raise InvalidFilterException(
                "Price bounds are not supported by canonical routes; "
                "use an unbounded search and filter fetched rental prices explicitly."
            )

    def build_search_url(self, search_filter: RentalFilter) -> str:
        """Build a canonical search URL; reject unsupported price bounds."""
        self._validate_supported_budget(search_filter)
        prop_type = search_filter.criteria.specifications.property_type
        city = search_filter.criteria.location.city
        nb = search_filter.criteria.location.neighborhood
        prefix = self._determine_prefix(prop_type)
        location_slug = self._determine_location(city, nb)
        bed_slug = search_filter.criteria.specifications.bedrooms.format_slug_part()
        sort_slug = self._determine_sort(search_filter.constraints.pagination.sort_order)
        page_slug = search_filter.constraints.pagination.page_number.format_slug_part()
        full_slug = f"{prefix}{location_slug}{bed_slug}{sort_slug}{page_slug}.html"
        return f"{self._config.base_url}/{full_slug}"

    def build_property_detail_url(self, code: PropertyCode) -> str:
        """Construct direct generic property detail URL by code."""
        code_str = code.value()
        return f"{self._config.base_url}/propriedades/imovel-{code_str}.html"

    def build_facets_url(self, city: str = "") -> str:
        """Construct base rental listings URL for facet discovery."""
        active_city = self._slugify(city) if city else self._config.default_city
        loc = f"-{active_city}-{self._config.default_state}"
        return f"{self._config.base_url}/imoveis-aluguel{loc}.html"
