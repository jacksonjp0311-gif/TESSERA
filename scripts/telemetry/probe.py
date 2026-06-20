from __future__ import annotations

import argparse
import time


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay-ms", type=int, default=10)
    parser.add_argument("--exit-code", type=int, default=0)
    args = parser.parse_args()
    time.sleep(max(0, args.delay_ms) / 1000.0)
    return args.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
