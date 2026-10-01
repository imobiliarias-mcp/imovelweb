"""Configuration settings for Imovelweb portal client."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ImovelwebConfiguration:
    """Client configuration for Imovelweb scraper and portal client."""

    base_url: str = "https://www.imovelweb.com.br"
    default_city: str = "timoteo"
    default_state: str = "mg"
    timeout_seconds: float = 30.0
    headless: bool = True

    def user_agent(self) -> str:
        """Return modern desktop Chrome User-Agent header."""
        return (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        )

    def browser_locale(self) -> str:
        """Return browser locale setting."""
        return "pt-BR"

    def timezone_id(self) -> str:
        """Return Brazilian regional timezone."""
        return "America/Sao_Paulo"
