"""处理 NDJSON 输入和输出的答题骨架，题意见 README.md。"""
import json
import sys


def main():
    for raw in sys.stdin.buffer:
        if not raw.strip():
            continue
        command = json.loads(raw)
        if command['op'] == 'query':
            raise NotImplementedError('Implement optimum and rank queries')
        sys.stdout.buffer.write(b'{"ok":true}\n')
        sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
