"""Run test suite for Imovelweb rental research."""

import sys
import pytest


def main() -> None:
    """Run pytest with arguments."""
    args = sys.argv[1:] if len(sys.argv) > 1 else ["-v", "-m", "not integration"]
    print(f"Running pytest with args: {args}")
    exit_code = pytest.main(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
