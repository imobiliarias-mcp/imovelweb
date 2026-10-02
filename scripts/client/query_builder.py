"""URL and query builder for Imovelweb search routing."""

import unicodedata
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

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

    def public_base_url(self) -> str:
        """Return the configured public portal origin."""
        return self._config.base_url

    def resolve_public_property_url(self, url: str, code: PropertyCode) -> str:
        """Resolve card links or the documented posting-code fallback."""
        if not url.strip():
            if code.value() == "0" or not code.value().isdigit():
                raise ValueError(f"No public property URL or usable code for {code.value()}")
            return self.build_property_detail_url(code)
        resolved_url = urljoin(f"{self.public_base_url().rstrip('/')}/", url.strip())
        self._validate_public_url(resolved_url)
        return self._remove_tracking_parameters(resolved_url)

    def _validate_public_url(self, url: str) -> None:
        """Reject non-web URLs and hosts outside the configured public portal."""
        parsed_url = urlsplit(url)
        base_url = urlsplit(self.public_base_url())
        valid_scheme = parsed_url.scheme in {"http", "https"}
        same_host = self._normalize_host(parsed_url.hostname) == self._normalize_host(base_url.hostname)
        is_property_route = parsed_url.path.startswith("/propriedades/")
        is_html_page = parsed_url.path.endswith(".html")
        if not valid_scheme or not parsed_url.hostname or not same_host:
            raise ValueError(f"URL is not on the configured public host: {url}")
        if not is_property_route or not is_html_page:
            raise ValueError(f"URL is not a public property detail page: {url}")

    def _normalize_host(self, hostname: str | None) -> str:
        """Treat www and apex hostnames as the same configured portal."""
        return (hostname or "").removeprefix("www.").lower()

    def _remove_tracking_parameters(self, url: str) -> str:
        """Drop known Imovelweb tracking keys while preserving property identifiers."""
        parsed_url = urlsplit(url)
        query = parse_qsl(parsed_url.query, keep_blank_values=True)
        retained_query = [(key, value) for key, value in query if not key.startswith("n_")]
        return urlunsplit(parsed_url._replace(query=urlencode(retained_query)))

    def build_property_detail_url(self, code: PropertyCode) -> str:
        """Construct direct generic property detail URL by code."""
        code_str = code.value()
        return f"{self._config.base_url}/propriedades/imovel-{code_str}.html"

    def build_facets_url(self, city: str = "") -> str:
        """Construct base rental listings URL for facet discovery."""
        active_city = self._slugify(city) if city else self._config.default_city
        loc = f"-{active_city}-{self._config.default_state}"
        return f"{self._config.base_url}/imoveis-aluguel{loc}.html"
