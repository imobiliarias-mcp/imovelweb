# Single Source of Truth (SOT): Imovelweb Navent Platform Specification

## 1. System Identity & Overview
- **Portal**: Imovelweb Brasil
- **Parent Network**: Grupo QuintoAndar / Navent
- **Domain**: `https://www.imovelweb.com.br`
- **Application Core**: Micro-frontend architecture based on RPLIS (Listing engine) and RPFIC (Property sheet/ficha engine).

---

## 2. Canonical SEO Search Interface

### 2.1 Route Contract
```http
GET /{tipo_propriedade}-{finalidade}-{localizacao}{filtros}{ordenacao}{paginacao}.html HTTP/1.1
Host: www.imovelweb.com.br
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36
```

### 2.2 Segment Definitions
- **`{tipo_propriedade}`**:
  - `imoveis`: All property categories (default).
  - `apartamentos`: Apartments.
  - `casas`: Houses.
  - `comerciais`: Commercial offices, stores, and warehouses.
  - `terrenos`: Lots and land parcels.
  - `rurais`: Farm and agricultural land.
- **`{finalidade}`**:
  - `aluguel`: Rental operations.
  - `venda`: Sales operations.
- **`{localizacao}`**:
  - Municipality format: `-{cidade}-{uf}` (e.g. `-timoteo-mg`).
  - Neighborhood format: `-{bairro}-{cidade}` (e.g. `-centro-timoteo`, `-recanto-verde-timoteo`, `-olaria-timoteo`, `-funcionarios-timoteo`).
- **`{filtros}`**:
  - Exact: `-{N}-quarto` ($N=1$) or `-{N}-quartos` ($N > 1$).
  - Range: `-desde-{min}-ate-{max}-quartos` (e.g. `-desde-1-ate-2-quartos`).
  - Minimum: `-mais-de-{N}-quartos` (e.g. `-mais-de-2-quartos`).
- **`{ordenacao}`**:
  - Lowest price: `-ordem-preco-menor`
  - Highest price: `-ordem-preco-maior`
  - Most recent: `-ordem-publicado-maior`
  - Most visited: `-ordem-visitas-maior`
- **`{paginacao}`**:
  - Page 1: omitted.
  - Page $N \ge 2$: `-pagina-{N}`. Fixed page size: **30 listings**.

---

## 3. Internal REST Search API

### 3.1 Endpoint
```http
POST /rplis-api/postings HTTP/1.1
Host: www.imovelweb.com.br
Content-Type: application/json
X-Requested-With: XMLHttpRequest
X-Search-Id: {uuid}
```

### 3.2 Payload Fields
- `tipoDeOperacion`: `"2"` for rent, `"1"` for sale.
- `city`: Navent city ID (e.g. `"104019"` for Timóteo).
- `habitacionesminimo`: Minimum bedroom count.
- `habitacionesmaximo`: Maximum bedroom count.
- `preciomin`: Minimum price bound.
- `preciomax`: Maximum price bound.
- `sort`: Sorting strategy (`"relevance"`, `"low_price"`, `"high_price"`, `"more_recent"`).

---

## 4. Property Detail Route & Microdata

### 4.1 Endpoints
- Canonical Route: `GET /propriedades/{slug}-{property_id}.html`
- Generic Direct Route: `GET /propriedades/imovel-{property_id}.html` (HTTP 301/302 redirects to canonical route)

### 4.2 Data Models
1. **`avisoInfo` Object**:
   - `idAviso`: Unique property numeric identifier.
   - `postingTitle`: Public listing headline.
   - `pricesData`: Array containing operation types, amounts, and currency symbols.
   - `expenses`: Recurring maintenance/condominium expenses.
   - `pictures`: Array of gallery images with `resizeUrl1200x1200`, `resizeUrl720x532`, `url360x266`.
   - `mainFeatures`: Dictionary of features (`CFT100` total area, `CFT101` useful area, `CFT2` bedrooms, `CFT3` bathrooms, `CFT1` garages).
   - `publisher`: Realtor name and logo URL.
2. **Schema.org JSON-LD**:
   - `@type: House` / `Apartment` / `Residence`
   - `numberOfRooms`, `numberOfBedrooms`, `numberOfBathroomsTotal`
   - `floorSize` with `QuantitativeValue`
   - `address` with `PostalAddress`
