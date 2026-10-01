"""HTTP and browser transport layer for Imovelweb portal communication."""

import asyncio
from typing import Protocol, runtime_checkable
import httpx
from patchright.async_api import async_playwright
from scripts.client.configuration import ImovelwebConfiguration
from scripts.domain.exceptions import TransportException


@runtime_checkable
class ImovelwebTransportProtocol(Protocol):
    """Protocol for fetching HTML content from Imovelweb endpoints."""

    def get_html(self, url: str) -> str:
        """Retrieve rendered HTML content from target URL."""
        ...


class BrowserTransport(ImovelwebTransportProtocol):
    """High-fidelity headless browser transport capable of passing Cloudflare challenges."""

    def __init__(self, configuration: ImovelwebConfiguration) -> None:
        """Initialize browser transport with configuration."""
        self._config = configuration

    async def _async_fetch(self, url: str) -> str:
        """Asynchronously load page and retrieve DOM content."""
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=self._config.headless,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            context = await browser.new_context(
                user_agent=self._config.user_agent(),
                locale=self._config.browser_locale(),
                timezone_id=self._config.timezone_id(),
            )
            page = await context.new_page()
            timeout_ms = int(self._config.timeout_seconds * 1000)
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            for _ in range(6):
                title = await page.title()
                if "Um momento" not in title and "Just a moment" not in title:
                    break
                await asyncio.sleep(1)
            content = await page.content()
            await browser.close()
            return content

    def get_html(self, url: str) -> str:
        """Synchronously execute browser navigation and return page HTML."""
        try:
            return asyncio.run(self._async_fetch(url))
        except Exception as error:
            raise TransportException(f"Failed to fetch {url}: {error}") from error


class HttpTransport(ImovelwebTransportProtocol):
    """Direct HTTP client transport for testing or standard requests."""

    def __init__(self, http_client: httpx.Client) -> None:
        """Initialize transport with configured httpx client."""
        self._client = http_client

    def get_html(self, url: str) -> str:
        """Send HTTP GET and return response text."""
        try:
            resp = self._client.get(url)
            resp.raise_for_status()
            return resp.text
        except Exception as error:
            raise TransportException(f"HTTP request to {url} failed: {error}") from error


class StubTransport(ImovelwebTransportProtocol):
    """In-memory stub transport for unit tests."""

    def __init__(self, responses: dict[str, str]) -> None:
        """Initialize stub with mapping of URL to HTML response."""
        self._responses = responses

    def get_html(self, url: str) -> str:
        """Return registered response or default empty response."""
        if url in self._responses:
            return self._responses[url]
        for key, val in self._responses.items():
            if key in url:
                return val
        raise TransportException(f"No stub response found for {url}")
