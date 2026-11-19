"""NDJSON process entry point. Engine and WAL are intentionally incomplete."""
import argparse
import json
import sys

from engine import Engine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    args = parser.parse_args()
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    engine = Engine(args.db)
    try:
        for line in sys.stdin:
            command = json.loads(line)
            result = engine.execute(command)
            print(json.dumps(result, ensure_ascii=False, separators=(",", ":")), flush=True)
    finally:
        engine.close()


if __name__ == "__main__":
    main()
