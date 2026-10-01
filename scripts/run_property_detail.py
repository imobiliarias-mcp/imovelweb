"""CLI runner for retrieving Imovelweb property details."""

import sys
from scripts.domain.value_objects import PropertyCode
from scripts.providers.imovelweb import ImovelwebRentalProvider


def main() -> None:
    """Execute property detail retrieval."""
    print("=== Imovelweb Property Detail Runner ===")
    code_input = sys.argv[1] if len(sys.argv) > 1 else "3037421600"
    code = PropertyCode(code_input)

    provider = ImovelwebRentalProvider.create_default()
    print(f"Retrieving details for property code: {code.value()}...")
    detail = provider.get_property_detail(code)

    print("-" * 60)
    print(detail.format_detailed_view())
    print("-" * 60)
    print(f"Thumbnail URL: {detail.listing.presentation.media.thumbnail_url}")
    print(f"Canonical Path: {detail.listing.presentation.media.url_path}")


if __name__ == "__main__":
    main()
