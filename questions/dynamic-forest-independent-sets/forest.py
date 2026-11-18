"""Starter for the dynamic forest protocol described in README.md."""
import json
import sys


def main():
    for line in sys.stdin.buffer:
        cmd=json.loads(line)
        raise NotImplementedError(cmd['op'])


if __name__=='__main__':
    main()
