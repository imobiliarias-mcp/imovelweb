# Imovelweb — Central Rental Research MCP Provider

Reverse-engineered rental search engine and API client for **Imovelweb** (`https://www.imovelweb.com.br/`).

Engineered as a pluggable adapter for the **Central Rental Research MCP (Model Context Protocol)** server following **SOLID**, **Clean Code**, **Object Calisthenics**, and **Design Patterns** in Python, operating as a sister provider to **Epifânio Imóveis** and **Casa Linhares**.

---

## 📚 Documentation

- **[Documentation Index](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/docs/README.md)** (`docs/README.md`): Overview of all project documentation.
- **[Reverse Engineering Analysis & API Spec](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/docs/api-research.md)** (`docs/api-research.md`): Complete endpoint contracts, canonical URL slugs, parameter matrices, card DOM selectors, and property detail extraction.
- **[Research Plan & Findings Report](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/research-plan.md)** (`scripts/research-plan.md`): Reverse-engineering methodology, chronological discovery log, WAF bypass analysis, and verification results.
- **[Single Source of Truth (SOT) API Spec](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/docs/sot/imovelweb_navent_api_spec.md)** (`docs/sot/imovelweb_navent_api_spec.md`): Complete endpoint contracts, payload schemas, and Navent platform architecture.
- **[ADR 0001: MCP Architecture & Design](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/docs/adr/0001-rental-search-mcp-module-design.md)** (`docs/adr/0001-rental-search-mcp-module-design.md`): Hexagonal architecture, Object Calisthenics enforcement, and design patterns.
- **[API Reference](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/docs/api_reference.md)** (`docs/api_reference.md`): Quick-reference URL recipes and parameter mappings.
- **[Scripts & MCP Module Guide](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/README.md)** (`scripts/README.md`): Package layout and CLI runner guide.
- **[Architecture Standards](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/ARCHITECTURE.md)** (`scripts/ARCHITECTURE.md`): Calisthenics and SOLID compliance breakdown.
- **[Usage & MCP Integration](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/USAGE.md)** (`scripts/USAGE.md`): How to use the Python modules and integrate into MCP servers.

---

## ⚡ Quickstart

### Run Automated Tests
```bash
python3 scripts/run_tests.py
```

### Search Rentals
```bash
# Search rentals matching prompt target: Timóteo (1 to 2 bedrooms)
python3 scripts/run_search.py
```

### View Listing Details
```bash
# View complete details for property code 3037421600
python3 scripts/run_property_detail.py 3037421600
```

### Inspect Available Localities & Facets
```bash
python3 scripts/run_facets.py
```

### Execute End-to-End Verification
```bash
python3 scripts/verify_research.py
```

---

## 🏛️ Code Architecture & Standards Compliance

- **Priority Order**: Correctness first, modularity second, style principles third.
- **No `else` Keyword**: 100% eliminated using guard clauses, early returns, and polymorphic handlers.
- **Single Level of Indentation**: All methods adhere to at most 1 indent level.
- **Wrapped Primitives**: Domain concepts (`ListingPrice`, `PropertyCode`, `BedroomConstraint`, `PageNumber`) are immutable Value Objects.
- **First-Class Collections**: `ListingCollection`, `RentalSearchResult`, and `FacetCollection` wrap items without leaking raw mutable collections.
- **Size Limits**: Functions ≤ 15 lines, Classes ≤ 100 lines, Modules < 200 lines.
- **Instance Variables**: All classes hold at most 2 instance variables.
- **One Dot per Line**: Method chaining is eliminated in favor of explicit intermediate assignments.
- **Zero Abbreviations**: Clear, descriptive domain naming across all modules.
