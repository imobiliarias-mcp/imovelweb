# Usage & MCP Integration Guide

How to integrate and use the Imovelweb rental research modules within Python applications and Central Rental Research MCP servers.

## 1. Direct Python Module Usage

### Search Rental Listings
```python
from scripts.domain.criteria import RentalFilter
from scripts.providers.imovelweb import ImovelwebRentalProvider

# Instantiate provider
provider = ImovelwebRentalProvider.create_default()

# Configure criteria matching user prompt target
search_filter = (
    RentalFilter()
    .with_city("timoteo")
    .with_bedroom_range(1, 2)
)

# Execute search
search_result = provider.search_rentals(search_filter)

print(f"Total found: {search_result.total_count()}")
for listing in search_result.listings:
    print(listing.format_summary())
    print(f"Link: {listing.to_dictionary()['url']}")
```

### Retrieve Property Detail
```python
from scripts.domain.value_objects import PropertyCode
from scripts.providers.imovelweb import ImovelwebRentalProvider

provider = ImovelwebRentalProvider.create_default()
detail = provider.get_property_detail(PropertyCode("3037421600"))

print(detail.format_detailed_view())
```

---

## 2. Central Rental Research MCP Server Integration

The [`ImovelwebMcpAdapter`](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/mcp/tools.py) provides a standardized, dictionary-based interface designed for direct registration as MCP tools.

### Registration Example
```python
from scripts.mcp.tools import ImovelwebMcpAdapter

# Create default MCP adapter
mcp_adapter = ImovelwebMcpAdapter.create_default()

# Tool 1: search_rentals
def handle_search(city: str, min_bedrooms: int = 0, max_bedrooms: int = 0, page: int = 1) -> dict:
    return mcp_adapter.search_rentals(
        city=city,
        min_bedrooms=min_bedrooms,
        max_bedrooms=max_bedrooms,
        page=page,
    )

# Tool 2: get_property_detail
def handle_detail(property_code: str) -> dict:
    return mcp_adapter.get_property_detail(property_code)

# Tool 3: get_facets
def handle_facets() -> dict:
    return mcp_adapter.get_facets()
```
