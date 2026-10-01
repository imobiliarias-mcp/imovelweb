# Scripts & MCP Module Guide: Imovelweb Rental Research

This directory contains the Python modules, CLI runners, and MCP adapter for the **Imovelweb** rental research engine.

## Directory Layout

```
scripts/
├── __init__.py                # Package root
├── domain/                    # Pure domain models (zero external dependencies)
│   ├── __init__.py
│   ├── exceptions.py          # Domain-specific exceptions
│   ├── value_objects.py       # ListingPrice, PropertyCode, BedroomConstraint, PageNumber
│   ├── criteria.py            # RentalFilter, SearchBudget, SearchPagination
│   ├── entities.py            # RentalListing, RentalPropertyDetail
│   └── collections.py         # ListingCollection, RentalSearchResult, FacetCollection
├── interfaces/                # Central MCP integration capability protocols
│   ├── __init__.py
│   └── provider.py            # RentalSearchCapability, RentalProviderProtocol
├── client/                    # Portal infrastructure, transports, and parsers
│   ├── __init__.py
│   ├── configuration.py       # ImovelwebConfiguration
│   ├── query_builder.py       # ImovelwebQueryBuilder
│   ├── http_transport.py      # BrowserTransport, HttpTransport, StubTransport
│   └── parsers.py             # SearchResultParser, PropertyDetailParser, FacetParser
├── providers/                 # Portal adapter implementations
│   ├── __init__.py
│   └── imovelweb.py           # ImovelwebRentalProvider
├── mcp/                       # Model Context Protocol adapter
│   ├── __init__.py
│   └── tools.py               # ImovelwebMcpAdapter
├── run_search.py              # CLI rental search runner
├── run_property_detail.py     # CLI property detail runner
├── run_facets.py              # CLI facet explorer
├── run_tests.py               # Test runner script
└── verify_research.py         # End-to-end verification script
```

## CLI Usage

### 1. Execute Rental Search
```bash
python3 scripts/run_search.py
```

### 2. Retrieve Property Details
```bash
python3 scripts/run_property_detail.py 3037421600
```

### 3. Explore Facets
```bash
python3 scripts/run_facets.py
```

### 4. Run Full Verification
```bash
python3 scripts/verify_research.py
```

### 5. Run Tests
```bash
python3 scripts/run_tests.py
```
