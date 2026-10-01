# Reverse-Engineered API Specification: Imovelweb

## 1. Overview & Architecture

Imovelweb (`https://www.imovelweb.com.br`) is one of Brazil's largest real estate portals, operating under the **Navent** technology stack (a subsidiary of QuintoAndar Group).

The portal architecture is composed of:
1. **Frontend Presentation Layer**: Modern React application utilizing Loadable Components (`__LOADABLE_REQUIRED_CHUNKS__`), client-side state management (Redux store in Webpack bundle `main.js`), and server-side rendering (SSR) for search engine indexing.
2. **CDN & Assets Infrastructure**: Hosted across Navent CDNs (`img10.naventcdn.com`, `imgbr.imovelwebcdn.com`) with versioned micro-frontend chunks:
   - `RPLIS` (*Real Properties Listing*): search listings, filters, sorting, and pagination engine (e.g. `RPLISv8.322.0-RC2`).
   - `RPFIC` (*Real Properties Ficha*): property detail page and media gallery engine (e.g. `RPFICv5.432.0-RC3`).
3. **Bot Mitigation & WAF**: Cloudflare Turnstile and Managed Challenges protect against automated scrapers. Requests from standard non-browser HTTP clients receive HTTP 403 unless TLS fingerprints and browser JavaScript execution environments (e.g. Patchright / Playwright) are utilized.

### 1.1 Authentication & Security Requirements
- **Authentication**: **None required**. All rental searches, filter queries, pagination requests, and property details are publicly accessible without authentication, user logins, API keys, or session tokens.
- **WAF / Cloudflare Turnstile**: Automated access requires browser TLS emulation (Patchright / Playwright) with `domcontentloaded` wait states. Direct external HTTP POST requests to internal endpoints trigger managed challenges unless verified by Turnstile clearance tokens.
- **HTTP Methods**:
  - `GET`: Used for canonical SEO search listings, filtered queries, pagination, property detail retrieval, and media.
  - `POST`: Used by the internal AJAX search API (`/rplis-api/postings`).

---

## 2. Rental Search Endpoints & Routing

Imovelweb utilizes a dual search architecture:
1. **Canonical SEO SSR Search Routes**: Primary public interface, delivering complete server-side rendered HTML with structured microdata (`Schema.org` JSON-LD) and embedded state.
2. **Internal REST Search API**: Asynchronous AJAX endpoint utilized by client-side filter updates.

---

## 3. Canonical SEO Search Routing (Primary Interface)

The canonical search routing maps user criteria into hierarchical URL slugs:

```http
GET /{tipo_propriedade}-{finalidade}-{localizacao}{filtros}{ordenacao}{paginacao}.html HTTP/1.1
Host: www.imovelweb.com.br
```

### 3.1 Path Segments Breakdown

| Segment | Meaning | Pattern / Format | Example Values |
| :--- | :--- | :--- | :--- |
| `{tipo_propriedade}` | Property category | Lowercase slug | `imoveis` (all), `apartamentos`, `casas`, `comerciais`, `terrenos`, `rurais` |
| `{finalidade}` | Transaction purpose | Fixed string | `aluguel` (rental), `venda` (sales) |
| `{localizacao}` | Geographic target | `-cidade-uf` or `-bairro-cidade` | `-timoteo-mg`, `-centro-timoteo`, `-recanto-verde-timoteo`, `-olaria-timoteo` |
| `{filtros}` | Physical constraints | Room counts / ranges | `-desde-1-ate-2-quartos`, `-1-quarto`, `-2-quartos`, `-mais-de-2-quartos` |
| `{ordenacao}` | Sort order | `-ordem-{criterio}` | `-ordem-preco-menor`, `-ordem-preco-maior`, `-ordem-publicado-maior`, `-ordem-visitas-maior` |
| `{paginacao}` | Page index | `-pagina-{N}` | `-pagina-2`, `-pagina-3` (omitted for page 1) |

### 3.2 Target URL Analysis
- **Target URL from User Prompt**:
  `https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-desde-1-ate-2-quartos.html`
- **Route Decomposition**:
  - `tipo_propriedade`: `imoveis` (all property types)
  - `finalidade`: `aluguel` (rental)
  - `localizacao`: `-timoteo-mg` (Timóteo municipality, Minas Gerais state)
  - `filtros`: `-desde-1-ate-2-quartos` (bedroom range from 1 to 2 bedrooms)
  - Extension: `.html`

### 3.3 Discovered Bedroom Encoding Conventions
| Bedroom Constraint | Slug Pattern | Example |
| :--- | :--- | :--- |
| Exact 1 bedroom | `-{N}-quarto` | `/imoveis-aluguel-timoteo-mg-1-quarto.html` |
| Exact N bedrooms ($N > 1$) | `-{N}-quartos` | `/imoveis-aluguel-timoteo-mg-2-quartos.html` |
| Range ($min$ to $max$) | `-desde-{min}-ate-{max}-quartos` | `/imoveis-aluguel-timoteo-mg-desde-1-ate-2-quartos.html` |
| Minimum ($N$ or more) | `-mais-de-{N}-quartos` | `/imoveis-aluguel-timoteo-mg-mais-de-2-quartos.html` |

### 3.4 Discovered Sorting Conventions
| Sort Goal | Slug Pattern | Internal Value |
| :--- | :--- | :--- |
| Relevantes (Default) | *(none)* | `relevantes` |
| Menor Preço (Lowest price first) | `-ordem-preco-menor` | `low_price` |
| Maior Preço (Highest price first) | `-ordem-preco-maior` | `high_price` |
| Mais Recentes (Newest listings) | `-ordem-publicado-maior` | `more_recent` |
| Mais Vistos (Most viewed) | `-ordem-visitas-maior` | `most_viewed` |

---

## 4. Pagination Behavior

- **Page Size**: **30 listings per page** across all search listings.
- **Page Parameter Slug**: `-pagina-{N}.html` (1-indexed; page 1 omits the slug).
- **DOM Pagination Elements**:
  - Container class: `div.paging-module__container-paging`
  - Current active page button: `a.paging-module__page-item-current[data-qa="PAGING_1"]`
  - Target page button: `a.paging-module__page-item[data-qa="PAGING_{N}"]`
  - Next page button: `a.paging-module__page-arrow[data-qa="PAGING_NEXT"]`
- **Boundary & Out-of-Bounds Behavior**:
  - Requesting an out-of-bounds page (e.g. requesting page 4 on a search containing 65 total items / 3 pages) results in an HTTP 200 server redirect to the **last valid page** (`pagina-3`).
  - Total count of available listings is explicitly available in the `h1` heading (e.g. `65 Imóveis para alugar em Timóteo, MG`) and in the title tag.

---

## 5. Internal REST Search API

When filters are changed interactively in the web browser, the client makes an asynchronous request to the internal posting service:

```http
POST /rplis-api/postings HTTP/1.1
Host: www.imovelweb.com.br
Content-Type: application/json
X-Requested-With: XMLHttpRequest
X-Search-Id: {uuid}
```

### 5.1 Request Payload Schema (Reverse-Engineered from `682.js` & Network Capture)

```json
{
  "q": null,
  "direccion": null,
  "moneda": "",
  "preciomin": null,
  "preciomax": null,
  "services": "",
  "general": "",
  "searchbykeyword": "",
  "amenidades": "",
  "caracteristicasprop": null,
  "comodidades": "",
  "disposicion": null,
  "roomType": "",
  "outside": "",
  "areaPrivativa": "",
  "areaComun": "",
  "multipleRets": "",
  "tipoDePropiedad": "",
  "subtipoDePropiedad": null,
  "tipoDeOperacion": "2",
  "garages": null,
  "antiguedad": null,
  "expensasminimo": null,
  "expensasmaximo": null,
  "withoutguarantor": null,
  "habitacionesminimo": "1",
  "habitacionesmaximo": "2",
  "ambientesminimo": 0,
  "ambientesmaximo": 0,
  "banos": null,
  "superficieCubierta": null,
  "idunidaddemedida": null,
  "metroscuadradomin": null,
  "metroscuadradomax": null,
  "metroscuadradocubiertosmin": null,
  "metroscuadradocubiertosmax": null,
  "tipoAnunciante": "ALL",
  "grupoTipoDeMultimedia": "",
  "publicacion": null,
  "sort": "low_price",
  "etapaDeDesarrollo": "",
  "auctions": null,
  "polygonApplied": null,
  "idInmobiliaria": null,
  "excludePostingContacted": "",
  "banks": "",
  "places": "",
  "condominio": "",
  "preTipoDeOperacion": "2",
  "city": "104019",
  "province": null,
  "zone": null,
  "valueZone": null,
  "subZone": null,
  "coordenates": null
}
```

### 5.2 Key Parameter Mapping
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `tipoDeOperacion` | `string` | `"2"` for Rental (`aluguel`), `"1"` for Sale (`venda`). |
| `city` | `string` | Navent internal city identifier (e.g. `"104019"` for Timóteo). |
| `zone` | `string` | Navent neighborhood identifier (e.g. `"532073"` for Recanto Verde). |
| `habitacionesminimo` | `string` | Minimum bedroom count (`"1"`). |
| `habitacionesmaximo` | `string` | Maximum bedroom count (`"2"`). |
| `preciomin` | `number` | Minimum rental price ceiling in BRL. |
| `preciomax` | `number` | Maximum rental price ceiling in BRL. |
| `sort` | `string` | Sorting strategy (`"relevance"`, `"low_price"`, `"high_price"`, `"more_recent"`). |

---

## 6. Search Results Card Parsing

Search result cards are rendered inside `div` elements carrying structured attributes:

```html
<div class="postingCardLayout-module__posting-card-layout" 
     data-id="3037421600" 
     data-posting-type="PROPERTY" 
     data-qa="posting PROPERTY" 
     data-to-posting="/propriedades/casa-para-aluguel-em-recanto-verde-timoteo-3037421600.html?...">
  <div class="postingGallery-module__gallery-container" data-qa="POSTING_CARD_GALLERY">
    <img src="https://imgbr.imovelwebcdn.com/avisos/2/30/37/42/16/00/360x266/6802748716.jpg" />
  </div>
  <div class="postingCard-module__posting-container">
    <h2 class="postingPrices-module__price" data-qa="POSTING_CARD_PRICE">R$ 1.400</h2>
    <div class="postingPrices-module__expenses" data-qa="expensas"></div>
    <h3 data-qa="POSTING_CARD_FEATURES">
      <span>50 m² tot.</span>
      <span>1 quarto</span>
      <span>1 banheiro</span>
    </h3>
    <h4 class="postingLocations-module__location-address">Rua Manacá</h4>
    <h4 data-qa="POSTING_CARD_LOCATION">Recanto Verde, Timóteo</h4>
    <h2 data-qa="POSTING_CARD_DESCRIPTION">
      <a href="/propriedades/casa-para-aluguel-em-recanto-verde-timoteo-3037421600.html">Casa para locação...</a>
    </h2>
  </div>
</div>
```

### 6.1 DOM Field Extraction Matrix
| Domain Field | DOM Selector / Attribute | Example Extracted Value |
| :--- | :--- | :--- |
| `property_code` | `card.get('data-id')` | `3037421600` |
| `url_path` | `card.get('data-to-posting').split('?')[0]` | `/propriedades/casa-para-aluguel-em-recanto-verde-timoteo-3037421600.html` |
| `price` | `card.select_one('[data-qa="POSTING_CARD_PRICE"]').text` | `R$ 1.400` -> `1400.0` |
| `expenses` | `card.select_one('[data-qa="expensas"]').text` | `R$ 350` -> `350.0` (or `0.0`) |
| `specs` | `card.select_one('[data-qa="POSTING_CARD_FEATURES"]').text` | `50 m² tot. · 1 quarto · 1 banheiro` |
| `street` | `card.select_one('.postingLocations-module__location-address').text` | `Rua Manacá` |
| `locality` | `card.select_one('[data-qa="POSTING_CARD_LOCATION"]').text` | `Recanto Verde, Timóteo` |
| `thumbnail_url` | `card.select_one('img[src*="avisos"]')['src']` | `https://imgbr.imovelwebcdn.com/avisos/2/.../360x266/6802748716.jpg` |
| `title` | `card.select_one('[data-qa="POSTING_CARD_DESCRIPTION"]').text` | `Casa para locação, nos fundo...` |

### 6.2 Structured Microdata (`Schema.org` JSON-LD)
The search page also embeds microdata containing aggregated and itemized listings:
1. `@type: RealEstateListing`:
   - `offers.offerCount`: Total listings on search page (`"8"`).
   - `offers.highPrice` / `lowPrice`: Minimum and maximum prices.
   - `mainEntity`: List of all listings with `name`, `description`, `url`, `image`, `datePosted`, `contentLocation`.
2. `@type: House` / `Apartment` / `Residence`:
   - Individual property types with `address`, `name`, `image`.

---

## 7. Property Detail Retrieval

Full property specifications are accessible via both canonical SEO URLs and direct ID routing.

### 7.1 Detail Endpoints
- **Canonical Route**: `GET https://www.imovelweb.com.br/propriedades/{slug}-{property_id}.html`
- **Direct Generic Code Route**: `GET https://www.imovelweb.com.br/propriedades/imovel-{property_id}.html`
  - Automatically redirects (301/302) to the canonical slug page.
- **Non-Existent Listing**: Returns HTTP 404 with error title `"Não encontramos a página solicitada - Error 404"`.

### 7.2 Embedded `avisoInfo` State Object
The detail page embeds a complete structured JavaScript object (`const avisoInfo = { ... };`) containing exhaustive property attributes:

```javascript
const avisoInfo = {
  idAviso: '3037421600',
  postingCode: "05cc82f9-9901-4cc8-b2f3-8ed610a996ed",
  postingType: 'PROPERTY',
  status: 'ONLINE',
  pricesData: [{
    operationType: { name: "aluguel", operationTypeId: "2" },
    prices: [{ isoCode: "BRL", currencyId: "3", currency: "R$", amount: 1400, formattedAmount: "1.400" }]
  }],
  price: 'R$ 1.400',
  expenses: '0',
  location: {
    locationId: "V1-D-532073",
    name: "Recanto Verde",
    label: "ZONA",
    parent: {
      locationId: "V1-C-104019",
      name: "Timóteo",
      label: "CIUDAD",
      parent: {
        locationId: "V1-B-253",
        name: "Minas Gerais",
        acronym: "MG"
      }
    }
  },
  address: { name: "Rua Manacá", visibility: "EXACT" },
  description: "Casa para locação, nos fundo...",
  publisher: {
    publisherId: '47831697',
    name: 'BUSKAZA',
    urlLogo: 'https://imgbr.imovelwebcdn.com/empresas/2/00/47/83/16/97/130x70/logo_buskaza.jpg',
    license: 'creci'
  },
  pictures: [
    {
      order: 0,
      resizeUrl1200x1200: "https://imgbr.imovelwebcdn.com/avisos/resize/2/30/37/42/16/00/1200x1200/6802748716.jpg",
      resizeUrl720x532: "https://imgbr.imovelwebcdn.com/avisos/resize/2/30/37/42/16/00/720x532/6802748716.jpg",
      url360x266: "https://imgbr.imovelwebcdn.com/avisos/2/30/37/42/16/00/360x266/6802748716.jpg"
    }
  ],
  mainFeatures: {
    CFT100: { featureId: "CFT100", label: "tot.", measure: "m²", value: "50" },
    CFT101: { featureId: "CFT101", label: "útil", measure: "m²", value: "50" },
    CFT3: { featureId: "CFT3", label: "banheiro", value: "1" },
    CFT2: { featureId: "CFT2", label: "quarto", value: "1" }
  },
  postingTitle: "Casa para aluguel em Recanto Verde, Timóteo",
  generatedTitle: "Casa · 50m² · 1 quarto"
};
```

---

## 8. Summary of Discovered Capabilities

| Capability | Canonical Path / Endpoint | Key Parameter / Format | Return Format |
| :--- | :--- | :--- | :--- |
| **Rental Search** | `/imoveis-aluguel-{localizacao}.html` | `localizacao` (e.g. `timoteo-mg`) | SSR HTML + JSON-LD |
| **Room Filtering** | `...-desde-{min}-ate-{max}-quartos.html` | `min`, `max` integers | SSR HTML + JSON-LD |
| **Single Bedroom** | `...-{N}-quarto(s).html` | `N` integer | SSR HTML + JSON-LD |
| **Min Bedrooms** | `...-mais-de-{N}-quartos.html` | `N` integer | SSR HTML + JSON-LD |
| **Typology Filter** | `/{tipo}-aluguel-...html` | `apartamentos`, `casas`, `comerciais` | SSR HTML + JSON-LD |
| **Neighborhood** | `/imoveis-aluguel-{bairro}-{cidade}.html` | `centro`, `recanto-verde`, `olaria` | SSR HTML + JSON-LD |
| **Sorting** | `...-ordem-{criterio}.html` | `preco-menor`, `preco-maior`, `publicado-maior`, `visitas-maior` | SSR HTML + JSON-LD |
| **Pagination** | `...-pagina-{N}.html` | `N >= 2` (30 items/page) | SSR HTML + JSON-LD |
| **Direct Detail** | `/propriedades/imovel-{id}.html` | `id` numeric listing code | HTTP 301/302 Redirect |
| **Canonical Detail** | `/propriedades/{slug}-{id}.html` | Embedded `avisoInfo` state | SSR HTML + JSON Microdata |
| **REST Search API** | `POST /rplis-api/postings` | JSON payload (`tipoDeOperacion: "2"`, `city`, etc.) | JSON Listings Array |
