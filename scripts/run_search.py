"""CLI runner for searching Imovelweb rental listings."""

import sys
from scripts.domain.criteria import RentalFilter
from scripts.providers.imovelweb import ImovelwebRentalProvider


def main() -> None:
    """Execute search and print results to stdout."""
    print("=== Imovelweb Rental Search Runner ===")
    provider = ImovelwebRentalProvider.create_default()

    # Default to user target: Timóteo 1 to 2 bedrooms
    flt = (
        RentalFilter()
        .with_city("timoteo")
        .with_bedroom_range(1, 2)
    )

    print("Target Search: Timóteo (MG) - Desde 1 até 2 quartos")
    search_result = provider.search_rentals(flt)

    print(f"Total matching listings: {search_result.total_count()}")
    print(f"Current page: {search_result.current_page()} (Items on page: {search_result.page_count()})")
    print("-" * 60)

    for listing in search_result.listings:
        print(listing.format_summary())


if __name__ == "__main__":
    main()
