#!/usr/bin/env python3
"""CLI entry-point: generate controller HTML for one or more consoles.

Usage:
    python generate.py nes
    python generate.py nes snes genesis      # batch
"""

import importlib.util
import os
import sys

# Ensure the retrobox package is importable
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from retrobox import ControllerGenerator


def load_config(console_dir: str):
    """Dynamically import <console_dir>/config.py and call get_config()."""
    config_path = os.path.join(console_dir, "config.py")
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"No config.py found in {console_dir}")
    spec   = importlib.util.spec_from_file_location("config", config_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.get_config()


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate.py <console> [console2 ...]")
        print("  Each <console> must be a folder containing config.py")
        print("  Example: python generate.py nes")
        sys.exit(1)

    generator = ControllerGenerator()

    for console_name in sys.argv[1:]:
        console_dir = os.path.join(ROOT, console_name)
        if not os.path.isdir(console_dir):
            print(f"ERROR: folder '{console_name}/' not found — skipping")
            continue

        try:
            config = load_config(console_dir)
        except Exception as exc:
            print(f"ERROR loading {console_name}/config.py: {exc}")
            continue

        output = generator.generate(config, console_dir)
        print(f"  ✓  {config.brand_name} {config.name} → {output}")

    print("\nDone.")


if __name__ == "__main__":
    main()
