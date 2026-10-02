"""Specialized HTML and data parsers for Imovelweb rental search."""

import re

from bs4 import BeautifulSoup

from scripts.client.configuration import ImovelwebConfiguration
from scripts.client.query_builder import ImovelwebQueryBuilder
from scripts.domain.collections import (
    FacetCollection,
    FacetGroup,
    FacetOption,
    ListingCollection,
    PaginationMetadata,
    RentalSearchResult,
)
from scripts.domain.entities import (
    DetailedProfile,
    ListingCore,
    ListingDetails,
    ListingIdentity,
    ListingLocation,
    ListingMedia,
    ListingNavigation,
    ListingPresentation,
    ListingSpecs,
    ListingValuation,
    PropertyDetailContext,
    PublisherInfo,
    RentalListing,
    RentalPropertyDetail,
)
from scripts.domain.exceptions import ParsingException, PropertyNotFoundException
from scripts.domain.value_objects import ListingPrice, PropertyCode


class CardFieldExtractor:
    """Helper extracting individual fields from an Imovelweb listing card."""

    def extract_price(self, card_soup: BeautifulSoup) -> ListingPrice:
        """Extract monetary price from card price element."""
        price_el = card_soup.select_one('[data-qa="POSTING_CARD_PRICE"]')
        raw_text = price_el.text if price_el else ""
        digits = re.sub(r"[^\d]", "", raw_text)
        amount = float(digits) if digits else 0.0
        return ListingPrice(amount)

    def extract_expenses(self, card_soup: BeautifulSoup) -> ListingPrice:
        """Extract condo or maintenance expenses."""
        exp_el = card_soup.select_one('[data-qa="expensas"]')
        raw_text = exp_el.text if exp_el else ""
        digits = re.sub(r"[^\d]", "", raw_text)
        amount = float(digits) if digits else 0.0
        return ListingPrice(amount)

    def extract_specs(self, card_soup: BeautifulSoup) -> ListingSpecs:
        """Extract area dimensions and room counts."""
        features_el = card_soup.select_one('[data-qa="POSTING_CARD_FEATURES"]')
        raw_text = features_el.text.strip().replace("\n", " ") if features_el else ""
        clean_text = " · ".join([p.strip() for p in raw_text.split("  ") if p.strip()])
        return ListingSpecs(dimensions=clean_text, room_summary=clean_text)

    def extract_location(self, card_soup: BeautifulSoup) -> ListingLocation:
        """Extract street and locality text."""
        loc_el = card_soup.select_one('[data-qa="POSTING_CARD_LOCATION"]')
        locality = loc_el.text.strip() if loc_el else ""
        street_el = card_soup.select_one(".postingLocations-module__location-address")
        street = street_el.text.strip() if street_el else ""
        return ListingLocation(street=street, locality=locality)

    def extract_media(self, card_soup: BeautifulSoup, public_url: str) -> ListingMedia:
        """Extract thumbnail and both public and legacy property links."""
        to_posting = card_soup.get("data-to-posting", "")
        img_el = card_soup.select_one("img[src*='avisos'], img[src*='imovelwebcdn']")
        thumb_url = img_el.get("src", "") if img_el else ""
        clean_path = to_posting.split("?")[0]
        navigation = ListingNavigation(public_url=public_url, url_path=clean_path)
        return ListingMedia(thumbnail_url=thumb_url, url_path=navigation)

    def extract_identity(self, card_soup: BeautifulSoup) -> ListingIdentity:
        """Extract listing code and public title."""
        code_str = card_soup.get("data-id", "0")
        desc_el = card_soup.select_one('[data-qa="POSTING_CARD_DESCRIPTION"]')
        title = desc_el.text.strip() if desc_el else f"Imóvel {code_str}"
        return ListingIdentity(code=PropertyCode(code_str), title=title)


class SearchResultParser:
    """Parses HTML search results into domain RentalSearchResult."""

    def __init__(self, query_builder: ImovelwebQueryBuilder | None = None) -> None:
        """Initialize parser with field extraction and configured URL resolution."""
        self._extractor = CardFieldExtractor()
        self._builder = query_builder or ImovelwebQueryBuilder(ImovelwebConfiguration())

    def _extract_public_media(self, card: BeautifulSoup, code: PropertyCode) -> ListingMedia:
        """Resolve the public link while retaining the original card path."""
        raw_url = card.get("data-to-posting", "")
        try:
            public_url = self._builder.resolve_public_property_url(raw_url, code)
        except ValueError as error:
            message = f"Unable to resolve public URL for Imovelweb listing {code.value()}: {error}"
            raise ParsingException(message) from error
        return self._extractor.extract_media(card, public_url)

    def _parse_card(self, card: BeautifulSoup) -> RentalListing:
        """Convert a single DOM card into a RentalListing entity."""
        identity = self._extractor.extract_identity(card)
        price = self._extractor.extract_price(card)
        expenses = self._extractor.extract_expenses(card)
        valuation = ListingValuation(rental_price=price, expenses=expenses)
        core = ListingCore(identity=identity, valuation=valuation)
        specs = self._extractor.extract_specs(card)
        location = self._extractor.extract_location(card)
        details = ListingDetails(specs=specs, location=location)
        media = self._extract_public_media(card, identity.code)
        presentation = ListingPresentation(details=details, media=media)
        return RentalListing(core=core, presentation=presentation)

    def _extract_pagination(self, soup: BeautifulSoup, cards_count: int) -> PaginationMetadata:
        """Extract current page and total search count."""
        h1_el = soup.find("h1")
        h1_text = h1_el.text if h1_el else ""
        match = re.search(r"(\d+)\s+Im[oó]veis", h1_text, re.IGNORECASE)
        total_count = int(match.group(1)) if match else cards_count
        title_el = soup.find("title")
        title_text = title_el.text if title_el else ""
        page_match = re.search(r"Pagina\s+(\d+)", title_text, re.IGNORECASE)
        page_num = int(page_match.group(1)) if page_match else 1
        return PaginationMetadata(current_page=page_num, total_count=total_count)

    def parse_search_response(self, html_content: str) -> RentalSearchResult:
        """Parse full search page HTML into first-class search result."""
        soup = BeautifulSoup(html_content, "lxml")
        card_elements = soup.select("div[data-id]")
        parsed_cards = [self._parse_card(c) for c in card_elements]
        collection = ListingCollection(items=tuple(parsed_cards))
        pagination = self._extract_pagination(soup, len(parsed_cards))
        return RentalSearchResult(listings=collection, pagination=pagination)


class PropertyDetailParser:
    """Parses Imovelweb property detail page into RentalPropertyDetail."""

    def __init__(self, query_builder: ImovelwebQueryBuilder | None = None) -> None:
        """Initialize parser with the public portal URL configuration."""
        self._builder = query_builder or ImovelwebQueryBuilder(ImovelwebConfiguration())

    def _build_media(self, thumbnail: str, path: str, code: str) -> ListingMedia:
        """Resolve detail navigation against the configured public portal."""
        property_code = PropertyCode(code)
        try:
            public_url = self._builder.resolve_public_property_url(path, property_code)
        except ValueError as error:
            message = f"Unable to resolve public URL for Imovelweb listing {code}: {error}"
            raise ParsingException(message) from error
        navigation = ListingNavigation(public_url=public_url, url_path=path)
        return ListingMedia(thumbnail_url=thumbnail, url_path=navigation)

    def _extract_id(self, html: str) -> str:
        """Extract posting ID from HTML script or meta."""
        match = re.search(r"['\"]?idAviso['\"]?\s*:\s*['\"]?(\d+)['\"]?", html)
        return match.group(1) if match else "0"

    def _extract_title(self, html: str, soup: BeautifulSoup) -> str:
        """Extract property title."""
        match = re.search(r"['\"]?postingTitle['\"]?\s*:\s*[\"']([^\"']+)[\"']", html)
        if match:
            return match.group(1)
        h1 = soup.find("h1")
        return h1.text.strip() if h1 else ""

    def _extract_price(self, html: str) -> ListingPrice:
        """Extract rental price from amount or price text."""
        match = re.search(r"['\"]?amount['\"]?\s*:\s*(\d+)", html)
        if match:
            return ListingPrice(float(match.group(1)))
        price_match = re.search(r"R\$\s*([\d\.]+)", html)
        digits = price_match.group(1).replace(".", "") if price_match else "0"
        return ListingPrice(float(digits) if digits else 0.0)

    def _extract_description(self, html: str, soup: BeautifulSoup) -> str:
        """Extract long description text."""
        match = re.search(r"['\"]?description['\"]?\s*:\s*\"([^\"]+)\"", html)
        if match:
            return match.group(1).encode("utf-8").decode("unicode_escape", errors="ignore")
        desc_el = soup.select_one("#reactDescription, .section-description")
        return desc_el.text.strip() if desc_el else ""

    def _extract_publisher(self, html: str) -> PublisherInfo:
        """Extract publisher name and logo."""
        name_match = re.search(r"publisher[\'\"]?\s*:\s*\{[^}]*?[\'\"]name[\'\"]?\s*:\s*[\'\"]([^\"\']+)[\'\"]", html)
        name = name_match.group(1) if name_match else ""
        logo_match = re.search(r"[\'\"]urlLogo[\'\"]?\s*:\s*[\'\"]([^\"\']+)[\'\"]", html)
        logo = logo_match.group(1) if logo_match else ""
        return PublisherInfo(name=name, logo_url=logo)

    def parse_detail_response(self, html_content: str) -> RentalPropertyDetail:
        """Parse property detail HTML into domain entity."""
        if "Error 404" in html_content or "Não encontramos a página" in html_content:
            raise PropertyNotFoundException("Property was not found on portal.")
        soup = BeautifulSoup(html_content, "lxml")
        code_str = self._extract_id(html_content)
        title = self._extract_title(html_content, soup)
        identity = ListingIdentity(code=PropertyCode(code_str), title=title)
        price = self._extract_price(html_content)
        valuation = ListingValuation(rental_price=price, expenses=ListingPrice(0.0))
        core = ListingCore(identity=identity, valuation=valuation)
        gen_title_match = re.search(r"['\"]?generatedTitle['\"]?\s*:\s*['\"]([^'\"]+)['\"]", html_content)
        gen_title = gen_title_match.group(1) if gen_title_match else ""
        specs = ListingSpecs(dimensions=gen_title, room_summary=gen_title)
        loc_match = re.search(r"['\"]?name['\"]?\s*:\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]?label['\"]?\s*:\s*['\"]ZONA['\"]", html_content)
        locality = loc_match.group(1) if loc_match else ""
        street_match = re.search(r"['\"]?address['\"]?\s*:\s*\{[^}]*?['\"]name['\"]?\s*:\s*['\"]([^'\"]+)['\"]", html_content)
        street = street_match.group(1) if street_match else ""
        details = ListingDetails(specs=specs, location=ListingLocation(street=street, locality=locality))
        pic_match = re.search(r"['\"]?resizeUrl1200x1200['\"]?\s*:\s*['\"]([^'\"]+)['\"]", html_content)
        thumb = pic_match.group(1) if pic_match else ""
        url_match = re.search(r"['\"]?url['\"]?\s*:\s*['\"](/propriedades/[^'\"]+)['\"]", html_content)
        rel_url = url_match.group(1) if url_match else ""
        media = self._build_media(thumb, rel_url, code_str)
        pres = ListingPresentation(details=details, media=media)
        listing = RentalListing(core=core, presentation=pres)
        desc = self._extract_description(html_content, soup)
        publisher = self._extract_publisher(html_content)
        context = PropertyDetailContext(profile=DetailedProfile(desc, gen_title), publisher=publisher)
        return RentalPropertyDetail(listing=listing, context=context)


class FacetParser:
    """Parses available search facets and options from portal HTML."""

    def parse_facets_response(self, html_content: str) -> FacetCollection:
        """Extract available facets into domain FacetCollection."""
        soup = BeautifulSoup(html_content, "lxml")
        links = soup.find_all("a", href=True)
        nb_options = []
        for a in links:
            href = a["href"]
            if "-timoteo" in href and "imoveis-aluguel-" in href:
                slug = href.replace(".html", "").replace("/imoveis-aluguel-", "")
                parts = slug.split("-timoteo")
                if parts[0]:
                    label = parts[0].replace("-", " ").title()
                    nb_options.append(FacetOption(label=label, value=parts[0]))
        nb_group = FacetGroup(name="neighborhoods", options=tuple(nb_options[:10]))
        sort_opts = (
            FacetOption("Mais Relevantes", "relevantes"),
            FacetOption("Menor Preço", "menor_preco"),
            FacetOption("Maior Preço", "maior_preco"),
            FacetOption("Mais Recentes", "recentes"),
            FacetOption("Mais Visitados", "visitas"),
        )
        sort_group = FacetGroup(name="sort_orders", options=sort_opts)
        type_opts = (
            FacetOption("Todos os Imóveis", "imoveis"),
            FacetOption("Apartamentos", "apartamentos"),
            FacetOption("Casas", "casas"),
            FacetOption("Comerciais", "comerciais"),
        )
        type_group = FacetGroup(name="property_types", options=type_opts)
        return FacetCollection(groups=(type_group, sort_group, nb_group))
