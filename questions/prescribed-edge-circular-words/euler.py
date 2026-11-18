"""处理 NDJSON 输入和输出的答题骨架，题意见 README.md。"""
import json
import sys


def main():
    for line in sys.stdin.buffer:
        if not line.strip():continue
        c=json.loads(line)
        if c['op']=='count':
            result={'possible':False,'length':0,'words':0,'necklaces':0,'periods':[],
                    'fixed_rotations':[],'prefix_counts':[],'witness':None}
        else:result={'ok':True}
        sys.stdout.buffer.write(json.dumps(result,separators=(',',':')).encode()+b'\n')
        sys.stdout.buffer.flush()


if __name__=='__main__':main()
