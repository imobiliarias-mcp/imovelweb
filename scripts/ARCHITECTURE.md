# Architectural Standards & Principles Enforcement

This document details the adherence to **SOLID**, **Clean Code**, **Object Calisthenics**, and **Design Patterns** across the Imovelweb research modules.

## 1. Prioritization Order

1. **Correctness First**: Real HTTP/browser execution, exact URL slug construction, resilient parsing with DOM and regex extractors, fail-fast boundary validation.
2. **Modularity Second**: Decoupled domain models, query builder, transport abstraction, specialized parsers, and a clean MCP provider facade.
3. **Style Principles Third**:
   - **SOLID**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.
   - **Object Calisthenics**: Max 1 indent level, no `else`, wrap primitives, first-class collections, 1 dot per line, no abbreviations, functions $\le 15$ lines, classes $\le 100$ lines, modules $< 200$ lines, $\le 2$ instance variables per class.

---

## 2. Object Calisthenics Enforcement Matrix

| Rule | Enforcement Strategy | Applied Location |
| :--- | :--- | :--- |
| **1. Only One Level of Indentation per Method** | Complex conditionals and loops decomposed into single-responsibility private helper methods. | [`PropertyDetailParser`](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/client/parsers.py#L125-L185), [`ImovelwebQueryBuilder`](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/client/query_builder.py#L10-L65). |
| **2. Don't Use the `else` Keyword** | 100% eliminated using early returns, guard clauses, and dictionary lookups. | Whole codebase contains **0** `else` statements. |
| **3. Wrap All Primitives and Strings** | Domain primitives wrapped into validated Value Objects. | [`ListingPrice`](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/domain/value_objects.py#L11-L35), [`PropertyCode`](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/domain/value_objects.py#L37-L56), [`BedroomConstraint`](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/domain/value_objects.py#L80-L125), [`PageNumber`](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/domain/value_objects.py#L127-L150). |
| **4. First-Class Collections** | Collections encapsulated in dedicated classes that expose only domain behaviors. | [`ListingCollection`](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/domain/collections.py#L9-L35), [`FacetCollection`](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/domain/collections.py#L80-L95). |
| **5. One Dot per Line** | Deep chaining eliminated in favor of explicit intermediate variable assignments. | All parsers, providers, and adapters. |
| **6. Don't Abbreviate** | Clear, expressive domain naming throughout (`search_filter`, `bedroom_constraint`, `listing_presentation`). | Standardized across all modules. |
| **7. Keep All Entities Small** | Functions $\le 15$ lines, classes $\le 100$ lines, modules $< 200$ lines. | All modules pass sizing limits. |
| **8. No More Than Two Instance Variables per Class** | Multi-attribute models decomposed into focused 2-element collaborator bundles. | [`ListingCore`](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/domain/entities.py#L42-L48), [`ListingPresentation`](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/domain/entities.py#L65-L72), [`RentalListing`](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/domain/entities.py#L74-L115), [`PropertyDetailContext`](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/domain/entities.py#L130-L136). |
| **9. No Getters/Setters/Properties (Tell, Don't Ask)** | Expose behavior and formatting rather than raw internal state. | [`ListingPrice.format_brl()`](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/domain/value_objects.py#L21-L26), [`RentalListing.format_summary()`](file:///home/samuelcaldas/repos/imobiliarias/imovelweb/scripts/domain/entities.py#L86-L92). |

---

## 3. SOLID Principles Breakdown

- **Single Responsibility (SRP)**: Each class has one clear concern. `ImovelwebQueryBuilder` formats URLs; `SearchResultParser` parses cards; `BrowserTransport` handles headless network operations.
- **Open/Closed (OCP)**: Interfaces and value objects can be extended with new capabilities without modifying existing callers.
- **Liskov Substitution (LSP)**: `BrowserTransport`, `HttpTransport`, and `StubTransport` all conform to `ImovelwebTransportProtocol` and can be substituted transparently.
- **Interface Segregation (ISP)**: Segregated capability protocols (`RentalSearchCapability`, `RentalDetailCapability`, `RentalFacetsCapability`) allow clients to depend only on the behaviors they require.
- **Dependency Inversion (DIP)**: `ImovelwebRentalProvider` depends on abstractions (`ImovelwebTransportProtocol`) rather than concrete implementations.
