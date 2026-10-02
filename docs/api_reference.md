# Imovelweb API & URL Reference

Quick reference for Imovelweb rental search URLs, parameters, and patterns.

## Target Search URL (Prompt Reference)
```
https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-desde-1-ate-2-quartos.html
```

---

## Canonical Search URLs

### Property Types (Timóteo, MG)
- **All Rentals**: `https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg.html`
- **Apartments**: `https://www.imovelweb.com.br/apartamentos-aluguel-timoteo-mg.html`
- **Houses**: `https://www.imovelweb.com.br/casas-aluguel-timoteo-mg.html`
- **Commercial**: `https://www.imovelweb.com.br/comerciais-aluguel-timoteo-mg.html`

### Bedroom Filters
- **1 Bedroom**: `https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-1-quarto.html`
- **2 Bedrooms**: `https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-2-quartos.html`
- **3 Bedrooms**: `https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-3-quartos.html`
- **1 to 2 Bedrooms (Range)**: `https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-desde-1-ate-2-quartos.html`
- **More than 2 Bedrooms**: `https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-mais-de-2-quartos.html`

### Neighborhoods (Timóteo)
- **Centro**: `https://www.imovelweb.com.br/imoveis-aluguel-centro-timoteo.html`
- **Recanto Verde**: `https://www.imovelweb.com.br/imoveis-aluguel-recanto-verde-timoteo.html`
- **Olaria**: `https://www.imovelweb.com.br/imoveis-aluguel-olaria-timoteo.html`
- **Funcionários**: `https://www.imovelweb.com.br/imoveis-aluguel-funcionarios-timoteo.html`

### Price Bounds in the Python Client

Canonical price-filter routing is not implemented. Nonzero `SearchBudget` bounds (including `with_price_ceiling()`) raise `InvalidFilterException` instead of silently returning unfiltered results. Fetch an unbounded search, paginate through its results, and explicitly compare published rental prices to the desired interval. This restriction applies to the client, not to the portal's filter capabilities.

### Sorting Orders
- **Lowest Price**: `https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-ordem-preco-menor.html`
- **Highest Price**: `https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-ordem-preco-maior.html`
- **Newest First**: `https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-ordem-publicado-maior.html`
- **Most Visited**: `https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-ordem-visitas-maior.html`

### Pagination
- **Page 1**: `https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg.html`
- **Page 2**: `https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-pagina-2.html`
- **Page 3**: `https://www.imovelweb.com.br/imoveis-aluguel-timoteo-mg-pagina-3.html`

---

## Direct Property Detail URLs
- **By ID**: `https://www.imovelweb.com.br/propriedades/imovel-{property_id}.html`
- **Canonical**: `https://www.imovelweb.com.br/propriedades/{slug}-{property_id}.html`
- Example: `https://www.imovelweb.com.br/propriedades/imovel-3037421600.html` redirects to `https://www.imovelweb.com.br/propriedades/casa-para-aluguel-em-recanto-verde-timoteo-3037421600.html`
