"""Unit tests for Imovelweb query builder."""

from scripts.client.configuration import ImovelwebConfiguration
from scripts.client.query_builder import ImovelwebQueryBuilder
from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import PropertyCode


def test_target_url_construction() -> None:
    """Ensure exact reproduction of target search URL from user prompt."""
    config = ImovelwebConfiguration()
    builder = ImovelwebQueryBuilder(config)

    target_filter = (
        RentalFilter()
        .with_city("timoteo")
        .with_bedroom_range(1, 2)
    )

    url = builder.build_search_url(target_filter)
    expected = "https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-desde-1-ate-2-quartos.html"
    assert url == expected


def test_property_type_url_construction() -> None:
    """Ensure property type URLs map to canonical prefixes."""
    config = ImovelwebConfiguration()
    builder = ImovelwebQueryBuilder(config)

    apartments_filter = RentalFilter().with_city("timoteo").with_property_type("apartamentos")
    assert builder.build_search_url(apartments_filter) == "https://www.imovelweb.com.br/apartamentos-aluguel-timoteo-mg.html"

    houses_filter = RentalFilter().with_city("timoteo").with_property_type("casas")
    assert builder.build_search_url(houses_filter) == "https://www.imovelweb.com.br/casas-aluguel-timoteo-mg.html"

    commercial_filter = RentalFilter().with_city("timoteo").with_property_type("comerciais")
    assert builder.build_search_url(commercial_filter) == "https://www.imovelweb.com.br/comerciais-aluguel-timoteo-mg.html"


def test_neighborhood_url_construction() -> None:
    """Ensure neighborhood search replaces state with city slug."""
    config = ImovelwebConfiguration()
    builder = ImovelwebQueryBuilder(config)

    flt = (
        RentalFilter()
        .with_city("timoteo")
        .with_neighborhood("centro")
    )
    url = builder.build_search_url(flt)
    assert url == "https://www.imovelweb.com.br/imoveis-aluguel-centro-timoteo.html"


def test_bedroom_variations_url_construction() -> None:
    """Ensure exact, range, and minimum bedroom filters map correctly."""
    config = ImovelwebConfiguration()
    builder = ImovelwebQueryBuilder(config)

    one_bed = RentalFilter().with_city("timoteo").with_bedrooms(1)
    assert builder.build_search_url(one_bed) == "https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-1-quarto.html"

    three_beds = RentalFilter().with_city("timoteo").with_bedrooms(3)
    assert builder.build_search_url(three_beds) == "https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-3-quartos.html"


def test_sorting_and_pagination_url_construction() -> None:
    """Ensure sorting and pagination slugs append correctly."""
    config = ImovelwebConfiguration()
    builder = ImovelwebQueryBuilder(config)

    sorted_paged = (
        RentalFilter()
        .with_city("timoteo")
        .with_sort("menor_preco")
        .with_page(2)
    )
    url = builder.build_search_url(sorted_paged)
    assert url == "https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-ordem-preco-menor-pagina-2.html"


def test_property_detail_url_construction() -> None:
    """Ensure generic property code route matches canonical pattern."""
    config = ImovelwebConfiguration()
    builder = ImovelwebQueryBuilder(config)

    code = PropertyCode("3037421600")
    url = builder.build_property_detail_url(code)
    assert url == "https://www.imovelweb.com.br/propriedades/imovel-3037421600.html"
