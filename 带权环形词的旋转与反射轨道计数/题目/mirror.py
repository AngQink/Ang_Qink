"""处理 NDJSON 输入和输出的答题骨架，题意见 README.md。"""
import json
import math
import sys


def main():
    for line in sys.stdin.buffer:
        if not line.strip():continue
        command=json.loads(line)
        if command['op']=='orbit':
            n=math.prod(p**e for p,e in command['factors'])
            reply={'length':n,'words':0,'necklaces':0,'bracelets':0,'periods':[],
                   'fixed':{'rotations':[],'mirrors':[]}}
        else:reply={'ok':True}
        sys.stdout.buffer.write(json.dumps(reply,separators=(',',':')).encode()+b'\n')
        sys.stdout.buffer.flush()


if __name__=='__main__':main()
