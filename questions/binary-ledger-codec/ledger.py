#!/usr/bin/env python3
"""Indexed binary ledger command-line tool (starter).

Implement this file completely according to SPEC.md.

Run with:  python ledger.py <command> ...

Commands:
    build <input.ndjson> <output.algr>
    get <file.algr> <key> [<key> ...]
    scan <file.algr> [--from <key>] [--limit <n>]
    verify <file.algr>
    recover <input.algr> <output.algr>
    merge <output.algr> <input1.algr> [<input2.algr> ...]
    info <file.algr>

This skeleton only parses arguments and dispatches; every handler raises
NotImplementedError. Replace the handlers with a complete implementation.
"""

import argparse
import sys


def cmd_build(args):
    raise NotImplementedError("build is not implemented yet")


def cmd_get(args):
    raise NotImplementedError("get is not implemented yet")


def cmd_scan(args):
    raise NotImplementedError("scan is not implemented yet")


def cmd_verify(args):
    raise NotImplementedError("verify is not implemented yet")


def cmd_recover(args):
    raise NotImplementedError("recover is not implemented yet")


def cmd_merge(args):
    raise NotImplementedError("merge is not implemented yet")


def cmd_info(args):
    raise NotImplementedError("info is not implemented yet")


def make_parser():
    parser = argparse.ArgumentParser(prog="ledger.py", add_help=True)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("build")
    p.add_argument("input")
    p.add_argument("output")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("get")
    p.add_argument("file")
    p.add_argument("keys", nargs="+")
    p.set_defaults(func=cmd_get)

    p = sub.add_parser("scan")
    p.add_argument("file")
    p.add_argument("--from", dest="from_key", default=None)
    p.add_argument("--limit", dest="limit", default=None)
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("verify")
    p.add_argument("file")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("recover")
    p.add_argument("input")
    p.add_argument("output")
    p.set_defaults(func=cmd_recover)

    p = sub.add_parser("merge")
    p.add_argument("output")
    p.add_argument("inputs", nargs="+")
    p.set_defaults(func=cmd_merge)

    p = sub.add_parser("info")
    p.add_argument("file")
    p.set_defaults(func=cmd_info)

    return parser


def main(argv=None):
    parser = make_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
