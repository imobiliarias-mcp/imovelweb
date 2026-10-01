"""CLI runner for exploring Imovelweb search facets."""

from scripts.providers.imovelweb import ImovelwebRentalProvider


def main() -> None:
    """Execute facet exploration."""
    print("=== Imovelweb Facet Explorer ===")
    provider = ImovelwebRentalProvider.create_default()

    facets = provider.get_facets()
    facets_dict = facets.to_dictionary()

    for group_name, options in facets_dict.items():
        print(f"\nGroup: {group_name.upper()} ({len(options)} options)")
        for opt in options:
            print(f"  • {opt['label']} -> {opt['value']}")


if __name__ == "__main__":
    main()
