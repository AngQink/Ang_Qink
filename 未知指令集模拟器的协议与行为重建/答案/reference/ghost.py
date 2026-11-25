"""Instance-specific numerical ISA constants extracted from supplied executable."""
OPCODE = (14, 28, 3, 23, 24, 10, 15, 8, 25, 18, 6, 26, 9, 21, 13, 255, 4, 11, 19, 1, 255, 0, 12, 20, 7, 255, 16, 5, 27, 2, 17, 22)
BASE_CYCLES = (3, 5, 5, 4, 6, 3, 2, 1, 6, 6, 2, 5, 3, 6, 4, 6, 7, 3, 7, 1, 4, 6, 6, 1, 3, 6, 3, 7, 2)
MEM_EXTRA = (3, 4, 3, 3, 4, 2, 1, 1, 3, 0, 4, 1, 0, 0, 0, 1, 0, 0, 3, 0, 0, 1, 4, 3, 4, 0, 3, 0, 1)
TAKEN_EXTRA = (3, 0, 4, 2, 3, 4, 0, 3, 1, 3, 3, 4, 2, 3, 0, 1, 1, 4, 1, 4, 0, 2, 1, 0, 0, 0, 3, 2, 2)
FLAG_POLICY = ((10, 3, 0, 0), (8, 8, 5, 1), (2, 4, 7, 5), (2, 8, 7, 5), (1, 7, 6, 0), (9, 3, 8, 3), (3, 10, 7, 5), (7, 5, 1, 9), (3, 1, 4, 7), (5, 7, 9, 4), (0, 3, 8, 10), (10, 3, 1, 10), (3, 3, 6, 0), (10, 6, 1, 6), (0, 9, 0, 3), (5, 5, 3, 5), (7, 3, 3, 6), (3, 0, 10, 10), (1, 9, 4, 0), (1, 9, 10, 3), (5, 5, 10, 1), (10, 1, 8, 6), (5, 7, 0, 8), (4, 0, 8, 4), (7, 2, 1, 0), (8, 0, 5, 6), (9, 7, 8, 1), (8, 10, 4, 0), (7, 2, 0, 5))


"""Pure Python execution kernel reconstructed from the supplied instance."""

MASK = (1 << 64) - 1
SIGN = 1 << 63
MOD = 1 << 64


def signed(value):
    return value - MOD if value & SIGN else value


def execute(code, memory, regs, max_cycles):
    pc = 0
    cycles = 0
    flags = [0, 0, 0, 0]
    length = len(code)
    while pc >= 0 and pc + 3 < length:
        # A surcharge can take a completed instruction beyond the budget.
        # This next-fetch limit is observably different from base-cost failure.
        if cycles > max_cycles:
            return 0, 'limit', pc, cycles, regs
        word = int.from_bytes(code[pc:pc+4], 'little')
        op = OPCODE[word & 31]
        cycles = (cycles + 1) & MASK
        if op == 255:
            return 1, 'bad_opcode', pc, cycles, regs
        cycles = (cycles + BASE_CYCLES[op] - 1) & MASK
        if cycles > max_cycles:
            return 1, 'limit', pc, cycles, regs
        imm = (word >> 6) & 0x3fff
        if imm & 0x2000:
            imm -= 0x4000
        dst = word >> 28
        ai = (word >> 24) & 15
        bi = (word >> 20) & 15
        a = regs[ai] if ai else 0
        b = regs[bi] if bi else 0
        carry = overflow = 0
        taken = False
        mem_op = False
        if op == 0:
            raw = a + b
            result = raw & MASK
            carry = int(raw > MASK)
            overflow = ((a ^ result) & (b ^ result)) >> 63
        elif op == 1:
            result = (a - b) & MASK
            carry = int(a < b)
            overflow = ((a ^ b) & (a ^ result)) >> 63
        elif op == 2:
            result = (a * b) & MASK
            carry = result >> 63
        elif op == 3:
            result = a ^ b
        elif op == 4:
            result = a & b
        elif op == 5:
            result = a | b
        elif op in (6, 7, 8):
            shift = b & 63
            if op == 6:
                result = (a << shift) & MASK
                carry = ((a >> (64-shift)) & 1) if shift else 0
            elif op == 7:
                result = a >> shift
                carry = ((a >> (shift-1)) & 1) if shift else 0
            else:
                result = (signed(a) >> shift) & MASK
                carry = ((a >> (shift-1)) & 1) if shift else 0
        elif op in (9, 10):
            shift = b & 63
            if op == 9:
                result = ((a << shift) | (a >> ((64-shift) & 63))) & MASK
                carry = result & 1
            else:
                result = ((a >> shift) | (a << ((64-shift) & 63))) & MASK
                carry = result >> 63
        elif op == 11:
            result = int.from_bytes(a.to_bytes(8, 'little'), 'big')
        elif op == 12:
            result = a.bit_count()
        elif op == 13:
            result = 64 - a.bit_length()
        elif op == 14:
            result = a ^ MASK
        elif op == 15:
            result = (-a) & MASK
            carry = int(a != 0)
        elif 16 <= op <= 21:
            width = 8 if op in (16, 17) else 4 if op in (18, 19) else 1
            address = signed((a + imm) & MASK)
            # The artifact compares a signed 64-bit end address. At the top
            # of the signed range that check wraps, then the native access
            # faults. Reproduce its exit status without any native access.
            if address >= 0 and address + width >= SIGN:
                raise SystemExit(0xc0000005)
            if address < 0 or address + width > 65536:
                return 1, 'mem_oob', pc, cycles, regs
            if op & 1:
                memory[address:address+width] = (b & ((1 << (8*width))-1)).to_bytes(width, 'little')
                result = b
            else:
                result = int.from_bytes(memory[address:address+width], 'little')
            mem_op = True
        elif op in (22, 23, 25, 26):
            if op == 23:
                target = (imm & 0x3fff) * 2
            elif op == 26:
                sp = regs[5]
                new_sp = (sp - 8) & MASK
                if new_sp > 65528:
                    return 1, 'stack_oob', pc, cycles, regs
                target = int.from_bytes(memory[new_sp:new_sp+8], 'little')
                regs[5] = new_sp
            else:
                if op == 25:
                    sp = regs[5]
                    if sp > 65528:
                        return 1, 'stack_oob', pc, cycles, regs
                    memory[sp:sp+8] = ((pc+4) & MASK).to_bytes(8, 'little')
                    regs[5] = sp+8
                target = (pc + 4 + 2*imm) & MASK
            target = signed(target)
            if target >= 0 and target + 3 >= SIGN:
                raise SystemExit(0xc0000005)
            if target < 0 or target + 3 >= length:
                return 1, 'bad_pc', pc, cycles, regs
            pc = target
            continue
        elif op == 24:
            result = 0
            if flags[0] == 1:
                target = signed((pc + 4 + 2*imm) & MASK)
                if target < 0 or target + 3 >= length:
                    return 1, 'bad_pc', pc, cycles, regs
                pc = target
                taken = True
        elif op == 27:
            return 1, None, (pc+4) & MASK, cycles, regs
        else:
            # Valid semantic 28 is a NOP: no register or flag policy applies.
            pc += 4
            continue
        if dst:
            regs[dst] = result
        sign = result >> 63
        values = (0, int(result == 0), int(result != 0), sign, sign ^ 1,
                  carry, carry ^ 1, overflow, overflow ^ 1, 1, 0)
        for i, policy in enumerate(FLAG_POLICY[op]):
            if policy:
                flags[i] = values[policy] if policy <= 9 else 0
        cycles = (cycles + (MEM_EXTRA[op] if mem_op else 0) +
                  (TAKEN_EXTRA[op] if taken else 0) + (3 if op == 2 else 0)) & MASK
        pc += 4
    return 0, 'bad_pc', pc, cycles, regs


"""Pure-standard-library outer protocol, intended for inlining in ghost.py.

execute(code, memory, regs, max_cycles) returns
(halted, trap, pc, cycles, regs). The mutable memory contains the final RAM.
"""
import sys

_U64_MASK = (1 << 64) - 1
_U64_MOD = 1 << 64
_RAM_SIZE = 65536
_HASH_SEED = 0xEFB2BE9C50963FF9
_HASH_MULT = 0x42B1F6B3E135822B
_C_SPACE = b" \t\n\r\v\f"


def parse_ull(text, base):
    """The executable's strtoull-like parser (base 10 or 16)."""
    i = 0
    size = len(text)
    while i < size and text[i] in _C_SPACE:
        i += 1
    negative = i < size and text[i] == 45
    if i < size and text[i] in (43, 45):
        i += 1
    if base == 16 and text[i:i + 2].lower() == b"0x":
        i += 2
    value = 0
    while i < size:
        c = text[i]
        if 48 <= c <= 57:
            digit = c - 48
        elif 65 <= c <= 90:
            digit = c - 55
        elif 97 <= c <= 122:
            digit = c - 87
        else:
            break
        if digit >= base:
            break
        value = value * base + digit
        if value > _U64_MASK:
            return _U64_MASK
        i += 1
    return (-value if negative else value) & _U64_MASK


def parse_hex_image(token):
    """strlen/2 complete byte pairs; at most the first 64 KiB."""
    count = min(len(token) // 2, _RAM_SIZE)
    short = token[:count * 2]
    try:
        decoded = bytes.fromhex(short.decode("ascii"))
        if len(decoded) == count:
            return decoded
    except (ValueError, UnicodeDecodeError):
        pass
    # For noncanonical tokens preserve sscanf(pointer, "%2x", &value).
    result = bytearray(count)
    for index in range(count):
        offset = index * 2
        while offset < len(token) and token[offset] in _C_SPACE:
            offset += 1
        result[index] = parse_ull(token[offset:offset + 2], 16) & 255
    return bytes(result)


def memory_hash(memory):
    """Custom 64-bit xor/multiply hash of all 65536 RAM bytes."""
    body = memory.rstrip(b"\0")
    value = _HASH_SEED
    for byte in body:
        value = ((value ^ byte) * _HASH_MULT) & _U64_MASK
    return (value * pow(_HASH_MULT, len(memory) - len(body), _U64_MOD)) & _U64_MASK


def _input_lines(stream):
    """Windows C text input, fgets(buf, 1000000, stdin), as bytes."""
    pending = b""
    while True:
        line = pending + stream.readline(999999 - len(pending))
        pending = b""
        if not line:
            return
        marker = line.find(b"\x1a")
        if marker >= 0:
            if marker:
                yield line[:marker]
            return
        if line.endswith(b"\r\n"):
            line = line[:-2] + b"\n"
        elif line.endswith(b"\r"):
            extra = stream.read(1)
            if extra == b"\n":
                line = line[:-1] + b"\n"
            else:
                pending = extra
        yield line


def format_result(result, memhash):
    halted, trap, pc, cycles, regs = result
    pc &= _U64_MASK
    if pc & (1 << 63):
        pc -= _U64_MOD
    registers = ",".join(f"{reg & _U64_MASK:016x}" for reg in regs)
    trap = trap or "-"
    return (f"OK {int(halted)} {trap} {pc} {cycles & _U64_MASK} "
            f"{registers} {memhash:016x}\r\n").encode("ascii")


def serve(execute, stdin=None, stdout=None):
    """Process and flush each request; streams are binary file-like objects."""
    if stdin is None:
        stdin = sys.stdin.buffer
    if stdout is None:
        stdout = sys.stdout.buffer
    code = b""
    initial_memory = bytearray(_RAM_SIZE)
    initial_regs = [0] * 16
    initial_hash = memory_hash(initial_memory)
    for raw_line in _input_lines(stdin):
        line = raw_line.split(b"\0", 1)[0].rstrip(b"\r\n")
        if not line:
            continue
        if line.startswith(b"INIT "):
            fields = [part for part in line[5:].split(b" ") if part]
            if len(fields) < 3:
                response = b"ERR\r\n"
            else:
                code = parse_hex_image(fields[0])
                image = parse_hex_image(fields[1])
                initial_memory = bytearray(_RAM_SIZE)
                initial_memory[:len(image)] = image
                # This deliberately leaves unprovided register slots unchanged.
                for index, token in enumerate(fields[2].split(b",")[:16]):
                    initial_regs[index] = parse_ull(token, 16)
                initial_hash = memory_hash(initial_memory)
                response = b"OK\r\n"
        elif line.startswith(b"RUN "):
            max_cycles = parse_ull(line[4:], 10)
            memory = initial_memory.copy()
            regs = initial_regs.copy()
            result = execute(code, memory, regs, max_cycles)
            memhash = initial_hash if memory == initial_memory else memory_hash(memory)
            response = format_result(result, memhash)
        else:
            response = b"ERR\r\n"
        stdout.write(response)
        stdout.flush()


if __name__ == '__main__':
    serve(execute)
