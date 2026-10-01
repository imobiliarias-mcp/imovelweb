"""Interfaces package exports for Imovelweb rental research."""

from scripts.interfaces.provider import (
    RentalDetailCapability,
    RentalFacetsCapability,
    RentalProviderProtocol,
    RentalSearchCapability,
)

__all__ = [
    "RentalDetailCapability",
    "RentalFacetsCapability",
    "RentalProviderProtocol",
    "RentalSearchCapability",
]
