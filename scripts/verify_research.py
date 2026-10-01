"""Verification script executing full Imovelweb reverse-engineered research flow."""

from scripts.client.configuration import ImovelwebConfiguration
from scripts.client.query_builder import ImovelwebQueryBuilder
from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import PropertyCode
from scripts.mcp.tools import ImovelwebMcpAdapter
from scripts.providers.imovelweb import ImovelwebRentalProvider


def main() -> None:
    """Run full verification suite."""
    print("================================================================")
    print("   IMOVELWEB RENTAL RESEARCH REVERSE-ENGINEERING VERIFICATION   ")
    print("================================================================\n")

    # 1. Verify URL Construction
    print("--- 1. Target URL Construction Verification ---")
    config = ImovelwebConfiguration()
    builder = ImovelwebQueryBuilder(config)
    target_filter = (
        RentalFilter()
        .with_city("timoteo")
        .with_bedroom_range(1, 2)
    )
    built_url = builder.build_search_url(target_filter)
    expected_url = "https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-desde-1-ate-2-quartos.html"
    print(f"Generated URL: {built_url}")
    print(f"Expected URL:  {expected_url}")
    assert built_url == expected_url, f"URL mismatch: {built_url} != {expected_url}"
    print("Result: URL generation verified successfully!\n")

    # 2. Live Search Execution
    print("--- 2. Live Target Search Execution ---")
    provider = ImovelwebRentalProvider.create_default()
    print("Executing search against live Imovelweb portal...")
    result = provider.search_rentals(target_filter)
    print(f"Total matching listings found: {result.total_count()}")
    print(f"Items on page: {result.page_count()}")
    assert result.page_count() > 0, "Expected at least 1 listing card!"
    sample_code = None
    for i, listing in enumerate(result.listings[:5]):
        if sample_code is None:
            sample_code = listing.code()
        print(f"  [{i+1}] {listing.format_summary()}")
    print("Result: Live rental search executed and verified successfully!\n")

    # 3. Live Property Detail Retrieval
    print(f"--- 3. Live Property Detail Retrieval (Code: {sample_code}) ---")
    detail = provider.get_property_detail(PropertyCode(sample_code))
    print(f"Title:       {detail.listing.title()}")
    print(f"Price:       {detail.listing.core.valuation.rental_price.format_brl()}")
    print(f"Location:    {detail.listing.presentation.details.location.locality}")
    print(f"Publisher:   {detail.context.publisher.name}")
    print(f"Description: {detail.context.profile.description[:120]}...")
    print("Result: Property detail retrieved and parsed successfully!\n")

    # 4. Central Rental Research MCP Adapter Execution
    print("--- 4. Central Rental Research MCP Adapter Verification ---")
    mcp_adapter = ImovelwebMcpAdapter.create_default()
    mcp_info = mcp_adapter.get_provider_info()
    print(f"MCP Provider Name: {mcp_info['provider_name']}")
    print(f"Coverage:          {mcp_info['coverage_region']}")
    print(f"Operations:        {mcp_info['supported_operations']}")

    mcp_result = mcp_adapter.search_rentals(
        city="timoteo",
        min_bedrooms=1,
        max_bedrooms=2,
    )
    print(f"MCP Tool Search Total: {mcp_result['total_count']} listings")
    assert mcp_result["page_items_count"] > 0, "MCP search should return items"
    print("Result: MCP adapter executed successfully!\n")

    print("================================================================")
    print("       ALL REVERSE-ENGINEERING RESEARCH CHECKS PASSED           ")
    print("================================================================")


if __name__ == "__main__":
    main()
