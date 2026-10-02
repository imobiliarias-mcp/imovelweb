# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Reverse-engineered rental search engine and API client for **Imovelweb** (`https://www.imovelweb.com.br/`), operating under Navent's technology stack (QuintoAndar Group). Engineered as a pluggable adapter for the **Central Rental Research Model Context Protocol (MCP)** server, following Hexagonal Architecture, SOLID principles, and strict Object Calisthenics in Python.

## Commands

### Environment Setup

The repository uses Python >= 3.11 with virtual environments managed via `uv` or `venv`:

```bash
# Set up virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run unit tests (offline, fast ~0.5s, skips live integration)
.venv/bin/pytest -v -m "not integration"

# Run a single test file
.venv/bin/pytest tests/test_domain.py
.venv/bin/pytest tests/test_url_builder.py
.venv/bin/pytest tests/test_parsers.py
.venv/bin/pytest tests/test_client.py

# Run a specific test function
.venv/bin/pytest tests/test_url_builder.py -k test_target_url_construction

# Run live integration tests (hits live Imovelweb portal via headless browser)
.venv/bin/pytest -v -m integration

# Run standalone test runner script
.venv/bin/python3 scripts/run_tests.py
```

### Linting & Code Quality

```bash
# Lint code with ruff
ruff check .

# Automatically apply safe fixes
ruff check --fix .
```

### Verification & CLI Tools

```bash
# Execute end-to-end verification (URL construction, live search, detail fetch, MCP adapter)
.venv/bin/python3 scripts/verify_research.py

# Run rental search CLI (default: Timóteo 1-2 bedrooms)
.venv/bin/python3 scripts/run_search.py

# Fetch full property details by property code (e.g. 3037421600)
.venv/bin/python3 scripts/run_property_detail.py 3037421600

# Inspect available search taxonomy and facets
.venv/bin/python3 scripts/run_facets.py
```

---

## High-Level Architecture & Structure

### Hexagonal Architecture (Ports and Adapters)

The codebase is organized into clean architectural layers with zero cyclic dependencies:

```
scripts/
├── domain/                    # Pure Domain Core (zero external dependencies)
│   ├── value_objects.py       # Immutable primitives: ListingPrice, PropertyCode, BedroomConstraint, PageNumber
│   ├── criteria.py            # Search specifications: RentalFilter, SearchBudget, SearchPagination
│   ├── entities.py            # Domain models: RentalListing, RentalPropertyDetail, ListingCore, ListingPresentation
│   ├── collections.py         # First-class collections: ListingCollection, RentalSearchResult, FacetCollection
│   └── exceptions.py          # Domain exceptions: InvalidPriceException, ListingNotFoundException, etc.
├── interfaces/                # Ports & Capability Protocols
│   └── provider.py            # RentalSearchCapability, RentalDetailCapability, RentalFacetsCapability, RentalProviderProtocol
├── client/                    # Portal Infrastructure & Transports
│   ├── configuration.py       # ImovelwebConfiguration (timeouts, user agents, locales, headless mode)
│   ├── query_builder.py       # ImovelwebQueryBuilder (canonical URL slug generator)
│   ├── http_transport.py      # Transports: BrowserTransport (Patchright/Turnstile bypass), HttpTransport, StubTransport
│   └── parsers.py             # DOM parsers: SearchResultParser, PropertyDetailParser, FacetParser
├── providers/                 # Provider Adapters
│   └── imovelweb.py           # ImovelwebRentalProvider (implements RentalProviderProtocol)
└── mcp/                       # Model Context Protocol Layer
    └── tools.py               # ImovelwebMcpAdapter (JSON-serializable MCP tool handlers)
```

### Key Technical Decisions

1. **Cloudflare Turnstile Bypass**: Imovelweb is protected by Cloudflare bot protection. `BrowserTransport` in `scripts/client/http_transport.py` launches a stealth headless browser using `patchright` with locale `pt-BR` and timezone `America/Sao_Paulo` to resolve challenges.
2. **Offline Testing via `StubTransport`**: Unit tests run in sub-second time without network access by injecting `StubTransport` loaded with HTML fixtures from `tests/fixtures/search_page.html` and `tests/fixtures/detail_page.html`.
3. **Canonical Slug Construction**: `ImovelwebQueryBuilder` formats filter criteria into Navent's hyphen-delimited URL pattern (e.g., `imoveis-aluguel-timoteo-mg-desde-1-ate-2-quartos.html`) rather than query parameters.

### Object Calisthenics & Coding Standards

All code under `scripts/` must strictly observe these constraints:

- **Entity Size Limits**: Functions $\le 15$ lines, Classes $\le 100$ lines, Modules $< 200$ lines.
- **Maximum 2 Instance Variables**: Classes with multiple attributes are decomposed into 2-element collaborator bundles (e.g. `RentalListing` contains `ListingCore` and `ListingPresentation`).
- **No `else` Keyword**: 100% eliminated using guard clauses, early returns, and dictionary dispatch.
- **Single Indent Level per Method**: Nested control structures are extracted into focused private helper methods.
- **Domain Primitive Wrapping**: Primitives are wrapped into validated Value Objects (`ListingPrice`, `PropertyCode`, `BedroomConstraint`, `PageNumber`).
- **First-Class Collections**: Any class containing a collection (`ListingCollection`, `FacetCollection`) holds no other member variables.
- **One Dot per Line**: Method chaining is eliminated in favor of explicit intermediate assignments (Law of Demeter).
- **No Abbreviations**: Variables and methods must use full, descriptive domain names.
- **Tell, Don't Ask**: Classes expose behavior and formatting methods (`format_brl()`, `format_summary()`, `to_dict()`) rather than public getters and setters.

### Key Documentation References

- `docs/api-research.md`: Reverse-engineered endpoint matrix, DOM card selectors, and property detail extraction rules.
- `docs/sot/imovelweb_navent_api_spec.md`: Single Source of Truth API spec for Navent RPLIS/RPFIC services.
- `docs/adr/0001-rental-search-mcp-module-design.md`: Hexagonal architecture and Object Calisthenics design record.
- `docs/api_reference.md`: Quick-reference URL slug recipes and parameter mappings.
- `scripts/ARCHITECTURE.md`: Calisthenics compliance breakdown and rule enforcement matrix.
- `scripts/USAGE.md`: Direct Python module and MCP server integration examples.
