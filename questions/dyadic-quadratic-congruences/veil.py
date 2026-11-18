"""处理 NDJSON 输入和输出的答题骨架，题意见 README.md。"""
import json
import sys


def main():
    for line in sys.stdin.buffer:
        if not line.strip():continue
        c=json.loads(line)
        if c['op']=='solve':raise NotImplementedError('Implement the exact modular solver')
        sys.stdout.buffer.write(b'{"ok":true}\n');sys.stdout.buffer.flush()


if __name__=='__main__':main()
