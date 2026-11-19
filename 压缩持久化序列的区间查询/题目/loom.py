"""Starter for the persistent sequence protocol described in README.md."""
import json
import sys


def main():
    for line in sys.stdin.buffer:
        command = json.loads(line.decode('utf-8'))
        raise NotImplementedError(command['op'])


if __name__ == '__main__':
    main()
