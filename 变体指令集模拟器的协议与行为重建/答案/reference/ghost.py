"""Instance ISA constants, recovered from the supplied executable."""
OPCODE=(28, 17, 21, 6, 18, 22, 5, 27, 15, 10, 14, 255, 25, 1, 3, 9, 2, 20, 255, 24, 19, 255, 0, 8, 7, 4, 23, 13, 26, 11, 16, 12)
BASE=(5, 1, 2, 6, 7, 5, 6, 4, 2, 3, 1, 1, 3, 5, 7, 6, 7, 2, 5, 6, 3, 3, 3, 2, 1, 4, 5, 4, 4)
MEM_EXTRA=(0, 3, 4, 4, 2, 4, 3, 0, 0, 0, 3, 3, 1, 2, 0, 3, 3, 1, 0, 4, 4, 3, 1, 1, 1, 3, 1, 4, 0)
TAKEN_EXTRA=(2, 1, 3, 3, 1, 0, 4, 1, 4, 4, 1, 3, 4, 3, 3, 2, 0, 4, 2, 0, 0, 3, 3, 2, 1, 0, 1, 1, 0)
POLICY=((5, 2, 3, 7), (4, 2, 1, 3), (0, 9, 4, 9), (0, 9, 5, 0), (7, 3, 3, 10), (7, 6, 2, 7), (3, 7, 0, 4), (0, 4, 5, 6), (2, 8, 10, 5), (0, 0, 0, 7), (10, 0, 2, 1), (6, 1, 10, 0), (3, 8, 9, 2), (9, 6, 0, 10), (7, 8, 3, 2), (3, 5, 6, 1), (7, 1, 0, 1), (8, 6, 10, 10), (3, 3, 10, 5), (1, 1, 6, 9), (10, 3, 6, 9), (1, 3, 2, 10), (9, 1, 8, 7), (9, 3, 2, 6), (0, 2, 6, 8), (0, 3, 0, 8), (5, 1, 5, 5), (7, 9, 6, 6), (10, 2, 6, 4))

"""Exact integer VM for the supplied GHOST-ISA II instance."""

MASK=(1<<64)-1
MOD=1<<64
SIGN=1<<63


def signed(x):return x-MOD if x&SIGN else x


def execute(code,memory,regs,budget):
    pc=cycles=0;flags=[0]*4;length=len(code)
    while pc>=0 and pc+3<length:
        if cycles>budget:return 0,'limit',pc,cycles,regs
        w=int.from_bytes(code[pc:pc+4],'little');op=OPCODE[w&31]
        cycles=(cycles+1)&MASK
        if op==255:return 1,'bad_opcode',pc,cycles,regs
        cycles=(cycles+BASE[op]-1)&MASK
        if cycles>budget:return 1,'limit',pc,cycles,regs
        dst=w>>28;ai=(w>>10)&15;bi=(w>>6)&15
        a=regs[ai] if ai else 0;b=regs[bi] if bi else 0
        imm=(w>>14)&16383
        if imm&8192:imm-=16384
        carry=overflow=0;access=taken=False
        if op==0:
            total=a+b;r=total&MASK;carry=int(total>MASK);overflow=((a^r)&(b^r))>>63
        elif op==1:
            r=(a-b)&MASK;carry=int(a<b);overflow=((a^b)&(a^r))>>63
        elif op==2:r=(a*b)&MASK;carry=r>>63
        elif op==3:r=a^b
        elif op==4:r=a&b
        elif op==5:r=a|b
        elif op in (6,7,8):
            k=b&63
            if op==6:r=(a<<k)&MASK;carry=(a>>(64-k))&1 if k else 0
            elif op==7:r=a>>k;carry=(a>>(k-1))&1 if k else 0
            else:r=(signed(a)>>k)&MASK;carry=(a>>(k-1))&1 if k else 0
        elif op in (9,10):
            k=b&63
            if op==9:r=((a<<k)|(a>>((64-k)&63)))&MASK;carry=r&1
            else:r=((a>>k)|(a<<((64-k)&63)))&MASK;carry=r>>63
        elif op==11:r=int.from_bytes(a.to_bytes(8,'little'),'big')
        elif op==12:r=a.bit_count()
        elif op==13:r=64-a.bit_length()
        elif op==14:r=a^MASK
        elif op==15:r=(-a)&MASK;carry=int(a!=0)
        elif 16<=op<=21:
            width=8 if op in (16,17) else 4 if op in (18,19) else 1
            address=signed((a+imm)&MASK)
            # Reproduce the native signed-end overflow as an exit status,
            # without making a native out-of-bounds memory access.
            if address>=0 and address+width>=SIGN:raise SystemExit(0xc0000005)
            if address<0 or address+width>65536:return 1,'mem_oob',pc,cycles,regs
            if op&1:
                memory[address:address+width]=(b&((1<<(8*width))-1)).to_bytes(width,'little');r=b
            else:r=int.from_bytes(memory[address:address+width],'little')
            access=True
        elif op in (22,23,25,26):
            if op==23:target=(imm&16383)*4
            elif op==26:
                sp=regs[7]
                if sp>65528:return 1,'stack_oob',pc,cycles,regs
                target=int.from_bytes(memory[sp:sp+8],'little');regs[7]=(sp+8)&MASK
            else:
                if op==25:
                    sp=(regs[7]-8)&MASK
                    if sp>65528:return 1,'stack_oob',pc,cycles,regs
                    memory[sp:sp+8]=((pc+4)&MASK).to_bytes(8,'little');regs[7]=sp
                target=(pc+4+imm*4)&MASK
            target=signed(target)
            if target>=0 and target+3>=SIGN:raise SystemExit(0xc0000005)
            if target<0 or target+3>=length:return 1,'bad_pc',pc,cycles,regs
            pc=target;continue
        elif op==24:
            r=0
            if flags[0]==0:
                target=signed((pc+4+4*imm)&MASK)
                if target<0 or target+3>=length:return 1,'bad_pc',pc,cycles,regs
                pc=target;taken=True
        elif op==27:return 1,None,(pc+4)&MASK,cycles,regs
        else:pc+=4;continue
        if dst:regs[dst]=r
        s=r>>63;choices=(0,int(r==0),int(r!=0),s,s^1,carry,carry^1,overflow,overflow^1,1,0)
        for i,selector in enumerate(POLICY[op]):
            if selector:flags[i]=choices[selector] if selector<=9 else 0
        cycles=(cycles+(MEM_EXTRA[op] if access else 0)+(TAKEN_EXTRA[op] if taken else 0)+(2 if op==2 else 0))&MASK
        pc+=4
    return 0,'bad_pc',pc,cycles,regs

"""TRIAD line protocol, reconstructed from the supplied executable.

Integration: inline this module into the final file, then call serve(execute).
execute(code, memory, regs, max_cycles) returns
(halted, trap, pc, cycles, regs), and mutates the 64 KiB memory in place.
"""

import sys

_PROTO_MASK64 = (1 << 64) - 1
_PROTO_RAM_SIZE = 65536
_PROTO_HASH_SEED = 0x5A5A2F89B11258A0
_PROTO_HASH_MULTIPLIER = 0x3F157F709C0C68EB


def memory_hash(memory):
    # Zero bytes only multiply the state; a trailing run can be skipped exactly.
    prefix = memory.rstrip(b'\0')
    value = _PROTO_HASH_SEED
    for byte in prefix:
        value = ((value ^ byte) * _PROTO_HASH_MULTIPLIER) & _PROTO_MASK64
    return (value * pow(_PROTO_HASH_MULTIPLIER,
                        _PROTO_RAM_SIZE - len(prefix), 1 << 64)) & _PROTO_MASK64


def _protocol_uint(text, base):
    """C strtoull semantics used for registers and cycle limits."""
    text = text.lstrip(b' \t\n\r\v\f')
    negative = text.startswith(b'-')
    if text[:1] in (b'-', b'+'):
        text = text[1:]
    if base == 16 and text[:2].lower() == b'0x':
        text = text[2:]
    value = 0
    overflow = False
    for character in text:
        if 48 <= character <= 57:
            digit = character - 48
        elif 65 <= character <= 90:
            digit = character - 55
        elif 97 <= character <= 122:
            digit = character - 87
        else:
            break
        if digit >= base:
            break
        value = value * base + digit
        if value > _PROTO_MASK64:
            overflow = True
            value = _PROTO_MASK64
    if overflow:
        return _PROTO_MASK64
    return (-value if negative else value) & _PROTO_MASK64


def _protocol_hex(text):
    # The executable consumes floor(length / 2) bytes and caps at 64 KiB.
    text = text[:min(len(text) // 2, _PROTO_RAM_SIZE) * 2]
    return bytes.fromhex(text.decode('ascii'))


def serve(execute, input_stream=None, output_stream=None):
    if input_stream is None:
        input_stream = sys.stdin.buffer
    if output_stream is None:
        output_stream = sys.stdout.buffer
    code = b''
    initial_memory = bytearray(_PROTO_RAM_SIZE)
    initial_regs = [0] * 16
    while True:
        line = input_stream.readline(999999)
        if not line:
            break
        line = line.split(b'\0', 1)[0].rstrip(b'\r\n')
        if not line:
            continue
        response = b'ERR'
        if line.startswith(b'INIT '):
            fields = [part for part in line[5:].split(b' ') if part]
            if len(fields) >= 3:
                code = _protocol_hex(fields[0])
                image = _protocol_hex(fields[1])
                initial_memory = bytearray(_PROTO_RAM_SIZE)
                initial_memory[:len(image)] = image
                for index, value in enumerate(fields[2].split(b',')[:16]):
                    initial_regs[index] = _protocol_uint(value, 16)
                response = b'OK'
        elif line.startswith(b'RUN '):
            max_cycles = _protocol_uint(line[4:], 10)
            memory = initial_memory.copy()
            regs = initial_regs.copy()
            halted, trap, pc, cycles, regs = execute(
                code, memory, regs, max_cycles)
            response = ('OK %d %s %d %d %s %016x' % (
                halted, trap or '-', pc, cycles,
                ','.join('%016x' % (value & _PROTO_MASK64) for value in regs),
                memory_hash(memory))).encode('ascii')
        output_stream.write(response + b'\r\n')
        output_stream.flush()


if __name__=='__main__':
    serve(execute)
