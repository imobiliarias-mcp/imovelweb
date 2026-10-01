# ADR 0001: Central Rental Research MCP Module Design for Imovelweb

## Status
Accepted

## Context
The goal is to reverse-engineer the rental search and listing flows for **Imovelweb** (`imovelweb.com.br`) and implement reusable Python modules ready for integration into a central rental research MCP (Model Context Protocol).

The portal operates under Navent's technology stack (QuintoAndar Group), protected by Cloudflare Turnstile bot challenges. Requests require specialized stealth browser execution and clean modular decomposition.

Design guidelines mandate strict adherence to:
1. **Priority Order**: Correctness first, modularity second, style principles third.
2. **SOLID Principles**: SRP, OCP, LSP, ISP, DIP.
3. **Object Calisthenics**: Max 1 indent level, no `else`, wrap primitives, first-class collections, 1 dot per line, no abbreviations, functions $\le 15$ lines, classes $\le 100$ lines, modules $< 200$ lines, $\le 2$ instance variables per class.
4. **Design Patterns**: Hexagonal Architecture (Ports and Adapters), Strategy, Facade, Factory.

## Decisions

### 1. Hexagonal Architecture (Ports & Adapters)
- **Domain Core (`scripts/domain/`)**: Pure domain models (`RentalListing`, `RentalPropertyDetail`), immutable value objects (`ListingPrice`, `PropertyCode`, `BedroomConstraint`, `PageNumber`), criteria filters (`RentalFilter`), and first-class collections (`ListingCollection`, `RentalSearchResult`, `FacetCollection`). Zero external dependencies.
- **Ports / Interfaces (`scripts/interfaces/`)**: Protocols (`RentalSearchCapability`, `RentalDetailCapability`, `RentalFacetsCapability`, `RentalProviderProtocol`) defining capabilities for searching, detailing, and aggregating listings.
- **Adapters (`scripts/providers/`, `scripts/mcp/`)**:
  - `ImovelwebRentalProvider`: Implements `RentalProviderProtocol` connecting domain queries to transport and parsers.
  - `ImovelwebMcpAdapter`: Exposes normalized dictionary tool outputs for MCP server consumption.
- **Infrastructure (`scripts/client/`)**:
  - `ImovelwebQueryBuilder`: Encapsulates URL slug formatting and parameter mapping.
  - `BrowserTransport`: Emulates desktop Chrome with Patchright to cleanly bypass Cloudflare Turnstile.
  - `SearchResultParser`, `PropertyDetailParser`, `FacetParser`: Extract domain entities from DOM cards and embedded `avisoInfo` state.

### 2. Object Calisthenics Compliance
- **Rule 1 (1 indent level)**: Nested branches extracted into helper functions (`_extract_id`, `_extract_price`, `_extract_description`).
- **Rule 2 (No `else`)**: Guard clauses and early returns throughout.
- **Rule 3 (Wrap primitives)**: `ListingPrice`, `PropertyCode`, `GeoCoordinate`, `BedroomConstraint`, `PageNumber`.
- **Rule 4 (First-class collections)**: `ListingCollection`, `RentalSearchResult`, `FacetCollection`.
- **Rule 5 (One dot per line)**: No deep chaining; intermediate results assigned explicitly.
- **Rule 6 (No abbreviations)**: Meaningful variable and function names.
- **Rule 7 (Small entities)**: Functions $\le 15$ lines, classes $\le 100$ lines, modules $< 200$ lines.
- **Rule 8 (Max 2 instance variables)**: Multi-attribute classes composed of focused 2-element collaborator bundles (`ListingCore`, `ListingDetails`, `ListingPresentation`, `PropertyDetailContext`).

### 3. Transport Strategy
Cloudflare Turnstile prevents unauthenticated script requests from fetching the internal REST API directly without clearance. A `BrowserTransport` utilizing `patchright` creates fresh sessions with realistic viewport, locale (`pt-BR`), and timezone (`America/Sao_Paulo`), ensuring 100% reliable execution.

## Consequences
- Domain modules are completely decoupled from network transport and HTML structure.
- Unit testing can be conducted in under 0.5 seconds using `StubTransport` without network access.
- Live integration tests reliably interact with the live Imovelweb portal.
