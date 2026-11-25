"""Standalone behavioral reconstruction of the supplied GLYPH executable."""
import math
import struct
import sys
from decimal import Decimal, localcontext

MASK = (1 << 64) - 1
SIGN = 1 << 63
MAX_INT = SIGN - 1


def wrap(value):
    value &= MASK
    return value - (1 << 64) if value & SIGN else value



_POS = (
 (0xa0000000000000000000,0x4002),
 (0xc8000000000000000000,0x4005),
 (0xfa000000000000000000,0x4008),
 (0x9c400000000000000000,0x400c),
 (0xc3500000000000000000,0x400f),
 (0xf4240000000000000000,0x4012),
 (0x98968000000000000000,0x4016),
 (0xbebc2000000000000000,0x4019),
 (0x8e1bc9bf040000000000,0x4034),
 (0xd3c21bcecceda1000000,0x404e),
 (0x9dc5ada82b70b59ef020,0x4069),
 (0xeb194f8e1ae525fd5dd0,0x4083),
 (0xaf298d050e4395d79671,0x409e),
 (0x82818f1281ed44a0bff9,0x40b9),
 (0xc2781f49ffcfa6d53cbf,0x40d3),
 (0x93ba47c980e98ce0c66f,0x41a8),
 (0xe070f78d3927556b85bc,0x427c),
 (0xaa7eebfb9df9de8eddbc,0x4351),
 (0x81842f29f2cce376e6a1,0x4426),
 (0xc4c5e310aef8aa171028,0x44fa),
 (0x957a4ae1ebf7f3d4a7eb,0x45cf),
)
_NEG = (
 (0xcccccccccccccccdcccd,0x3ffb),
 (0xa3d70a3d70a3d70a3d71,0x3ff8),
 (0x83126e978d4fdf3b645a,0x3ff5),
 (0xd1b71758e219652cd3c3,0x3ff1),
 (0xa7c5ac471b4784230fd0,0x3fee),
 (0x8637bd05af6c69b6a640,0x3feb),
 (0xd6bf94d5e57a42bc3d33,0x3fe7),
 (0xabcc77118461cefdfdc2,0x3fe4),
 (0xe69594bec44de15b4c2f,0x3fc9),
 (0x9abe14cd44753b53c492,0x3faf),
 (0xcfb11ead453994ba67de,0x3f94),
 (0x8b61313bbabce2c62324,0x3f7a),
 (0xbb127c53b17ec1595561,0x3f5f),
 (0xfb158592be068d2feed7,0x3f44),
 (0xa87fea27a539e9a53f24,0x3f2a),
 (0xddd0467c64bce4a1ac7d,0x3e55),
 (0x91ff83775423cc067b63,0x3d81),
 (0xc0314325637a193afa91,0x3cac),
 (0xfd00b897478238d18921,0x3bd7),
 (0xa686e3e8b11b085888dc,0x3b03),
 (0xdb377599b607424584c6,0x3a2e),
)

def _multiply(ma,ea,mb,eb):
    """CRT's deliberately truncated 16-bit convolution, then RNE to 80 bits."""
    a=[(ma>>(16*i))&0xffff for i in range(5)]
    b=[(mb>>(16*i))&0xffff for i in range(5)]
    product=sum(a[i]*b[j]<<(16*(i+j-4))
                for i in range(5) for j in range(4-i,5))
    exponent=ea+eb-0x3ffe
    shift=96-product.bit_length()
    product<<=shift
    exponent-=shift
    mantissa=product>>16
    guard=product&0xffff
    if guard>0x8000 or guard==0x8000 and mantissa&1:
        mantissa+=1
        if mantissa==1<<80:
            mantissa>>=1;exponent+=1
    return mantissa,exponent

def _table_operand(pair):
    mantissa,exponent=pair
    if mantissa&0xffff>0x7fff:
        mask=0xffffffff<<16
        mantissa=(mantissa&~mask)|((((mantissa>>16)-1)&0xffffffff)<<16)
    return mantissa,exponent

def _digits(x):
    bits=struct.unpack('<Q',struct.pack('<d',x))[0]
    e=(bits>>52)&0x7ff
    fraction=bits&((1<<52)-1)
    if e:
        sig64=((1<<52)|fraction)<<11
        exponent=e-1023+0x3fff
    else:
        size=fraction.bit_length()
        sig64=fraction<<(64-size)
        exponent=size-1-1074+0x3fff
    hi=sig64>>32
    estimate=(((exponent>>8)+((hi>>24)*2))*0x4d
              +exponent*0x4d10-0x134312f4)&0xffffffff
    point=estimate>>16
    if point&0x8000:point-=0x10000
    mantissa=sig64<<16
    power=abs(point)
    table=_NEG if point>0 else _POS
    group=0
    while power:
        digit=power&7
        if digit:
            mt,et=_table_operand(table[group*7+digit-1])
            mantissa,exponent=_multiply(mantissa,exponent,mt,et)
        power>>=3;group+=1
    if exponent>0x3ffe:
        point+=1
        mantissa,exponent=_multiply(mantissa,exponent,0xcccccccccccccccccccc,0x3ffb)
    fixed=(mantissa<<8)>>(0x3ffe-exponent)
    mask=(1<<88)-1
    digits=[]
    for _ in range(18):
        fixed*=10
        digits.append(fixed>>88)
        fixed&=mask
    guard=digits.pop()
    if guard>=5:
        position=16
        while position>=0 and digits[position]==9:
            digits[position]=0;position-=1
        if position<0:
            digits=[1]+[0]*16;point+=1
        else:digits[position]+=1
    return ''.join(str(d) for d in digits).rstrip('0'),point

def format_float_legacy(x):
    if math.isnan(x):return 'nan'
    if math.isinf(x):return '-inf' if x<0 else 'inf'
    if not x:return '-0.0' if math.copysign(1.0,x)<0 else '0.0'
    sign='-' if x<0 else ''
    digits,point=_digits(abs(x))
    exponent=point-1
    if exponent<-4 or exponent>=17:
        result=digits[0]+('.'+digits[1:] if len(digits)>1 else '')
        result+='e'+('+' if exponent>=0 else '-')+str(abs(exponent)).zfill(3)
    elif point>=len(digits):
        result=digits+'0'*(point-len(digits))+'.0'
    elif point>0:result=digits[:point]+'.'+digits[point:]
    else:result='0.'+'0'*(-point)+digits
    return sign+result


def format_float(value):
    return format_float_legacy(value).encode('ascii')


def fp_div(left, right):
    if right != 0.0:
        return left / right
    if left == 0.0 or math.isnan(left):
        return math.nan
    sign = math.copysign(1.0, left) * math.copysign(1.0, right)
    return math.copysign(math.inf, sign)




def _negative(x):
    return math.copysign(1.0, x) < 0.0


def powi32(x, n):
    """Reproduce FUN_004061b0, for an int32 exponent and binary64 base."""
    if n == 0 or x == 1.0:
        return 1.0
    sign = _negative(x) and bool(n & 1)
    x = abs(x)
    if math.isnan(x):
        return math.nan
    if x == 0.0:
        y = 0.0 if n >= 0 else math.inf
    elif math.isinf(x):
        y = math.inf if n >= 0 else 0.0
    else:
        if n < 0:
            n = -n
            x = 1.0 / x
        y = x if n & 1 else 1.0
        n >>= 1
        while n:
            x *= x
            if n & 1:
                y *= x
            n >>= 1
    return -y if sign else y


def _round_binary(d, precision=64):
    """Round a finite Decimal to a binary significand, ties to even."""
    if not d:
        return d
    negative = d < 0
    if negative:
        d = -d
    n, q = d.as_integer_ratio()
    e = n.bit_length() - q.bit_length()
    if (n < (q << e)) if e >= 0 else ((n << -e) < q):
        e -= 1
    shift = precision - 1 - e
    if shift >= 0:
        n <<= shift
    else:
        q <<= -shift
    m, r = divmod(n, q)
    if r * 2 > q or (r * 2 == q and m & 1):
        m += 1
    # A dyadic can need over 1000 decimal places. Preserve it exactly so a
    # later binary64 conversion handles halfway cases and subnormals.
    with localcontext() as ctx:
        ctx.prec = max(ctx.prec, abs(shift) + precision + 8)
        out = Decimal(m) * (Decimal(2) ** -shift)
    return -out if negative else out


def pow_extended_approx(x, y):
    """Experimental x87 log2/product/exp2 model, for positive finite x."""
    with localcontext() as ctx:
        ctx.prec = 120
        ln2 = Decimal(2).ln()
        lg_exact = Decimal.from_float(x).ln() / ln2
        if abs(x - 1.0) <= 0.29:
            lg = _round_binary(lg_exact)
        else:
            lg = _round_binary(_round_binary(lg_exact, 68))
        with localcontext() as exact:
            exact.prec = 2400
            z = _round_binary(Decimal.from_float(y) * lg)
        if z > 1025:
            return math.inf
        if z < -1076:
            return 0.0
        integer = z.to_integral_value()
        fraction = z - integer
        # The target executes F2XM1, FADD 1, FSCALE. Both F2XM1's result
        # and the following addition are rounded to the x87 significand.
        em1 = _round_binary((fraction * ln2).exp() - 1)
        mantissa = _round_binary(1 + em1)
        with localcontext() as exact:
            exact.prec = 1200
            out = mantissa * (Decimal(2) ** int(integer))
        return float(out)


def sqrt_extended(x):
    """Emulate x87 FSQRT then an 80-to-64-bit store, including ties."""
    with localcontext() as ctx:
        ctx.prec = 120
        return float(_round_binary(Decimal.from_float(x).sqrt()))


def mingw_pow(x, y, extended=True):
    """Return glyph's floating power; caller handles int64 integer powers.

    `extended=False` selects math.pow in place of the Decimal x87 model.
    """
    x, y = float(x), float(y)
    if y == 0.0 or x == 1.0:
        return 1.0
    if math.isnan(x) or math.isnan(y):
        return math.nan
    ax = abs(x)
    if math.isinf(y):
        if ax == 1.0:
            return 1.0
        return math.inf if ((ax > 1.0) == (y > 0.0)) else 0.0
    integer = y.is_integer()
    odd = integer and bool(int(y) & 1)
    sign = _negative(x) and odd
    if ax == 0.0:
        out = 0.0 if y > 0.0 else math.inf
        return -out if sign else out
    if math.isinf(ax):
        out = math.inf if y > 0.0 else 0.0
        return -out if sign else out
    if integer and -2147483648.0 <= y <= 2147483647.0:
        return powi32(x, int(y))
    if x < 0 and not integer:
        return math.nan
    if y == 0.5:
        return sqrt_extended(x)
    if extended:
        out = pow_extended_approx(ax, y)
    else:
        try:
            out = math.pow(ax, y)
        except OverflowError:
            out = math.inf
    return -out if sign else out


fp_pow = mingw_pow


_TENS=(1.0,1e1,1e2,1e3,1e4,1e5,1e6,1e7,1e8,1e9,1e10,1e11,1e12,1e13,1e14,1e15)
_BIG_POWERS=(1e16,1e32,1e64,1e128)
_TINY_POWERS=(1e-16,1e-32,1e-64,1e-128)

def _normalized(value):
    mantissa,exponent=math.frexp(value)
    return mantissa*2.0,exponent-1

def _initial_candidate(digits,exponent):
    count=min(16,len(digits))
    head=digits[:count]
    if count>9:
        value=float(int(head[:9]))*_TENS[count-9]+float(int(head[9:]))
    else:value=float(int(head))
    exponent+=len(digits)-count
    negative=exponent<0
    power=abs(exponent)
    small=power&15
    if small:
        value=value/_TENS[small] if negative else value*_TENS[small]
    blocks=power>>4
    binary_exponent=0
    if blocks:
        while blocks>=16:
            value,shift=_normalized(value)
            binary_exponent+=shift
            value*=1e-256 if negative else 1e256
            blocks-=16
        value,shift=_normalized(value)
        binary_exponent+=shift
        index=0
        while blocks:
            if blocks&1:
                value*=(_TINY_POWERS if negative else _BIG_POWERS)[index]
            index+=1;blocks>>=1
    return value,binary_exponent

def _seed_above(value,external_exponent,other):
    vm,ve=math.frexp(value)
    om,oe=math.frexp(other)
    ve+=external_exponent
    return ve>oe or ve==oe and vm>om

def _bigint_normalized(value):
    """b2d: truncate, rather than round, to the leading 53 bits."""
    bits=value.bit_length()
    kept=min(bits,53)
    leading=value>>(bits-kept)
    return math.ldexp(float(leading),1-kept),bits-1

def _crosses_power2(digits,exponent,value,seed,external_exponent,ieee_exponent):
    """Reconstruct strtodg's first big-ratio correction before normalization.

    The common 5**k factor must be retained: cancelling it would change b2d
    truncation and would miss the legacy roundstep at a near-midpoint.
    """
    seed_num,seed_den=seed.as_integer_ratio()
    seed_exp=external_exponent-(seed_den.bit_length()-1)
    gap_exp=ieee_exponent-1023-52
    common_exp=min(exponent,seed_exp,gap_exp-1)
    five=5**max(-exponent,0)
    target=int(digits)*5**max(exponent,0)<<(exponent-common_exp)
    start=seed_num*five<<(seed_exp-common_exp)
    half=five<<(gap_exp-1-common_exp)
    prior=((1<<53)-1)*five<<(gap_exp-common_exp)
    power=(1<<53)*five<<(gap_exp-common_exp)
    if not (start<prior<target<prior+half):return False
    numerator,ne=_bigint_normalized(target-start)
    denominator,de=_bigint_normalized(half)
    if ne>de:numerator=math.ldexp(numerator,ne-de)
    else:denominator=math.ldexp(denominator,de-ne)
    units=(numerator/denominator)*.5
    step=int(units)
    if units-step>=.5:step+=1
    return start+step*(half*2)>=power

def parse_float_legacy(token:bytes)->float:
    source=token.decode('ascii')
    negative=source.startswith('-')
    unsigned=source[1:] if source[:1] in '+-' else source
    mantissa,marker,exptext=unsigned.lower().partition('e')
    explicit=0
    if marker:
        expnegative=exptext.startswith('-')
        magnitude=exptext[1:] if exptext[:1] in '+-' else exptext
        magnitude=magnitude.lstrip('0')
        if len(magnitude)>5:explicit=19999
        elif magnitude:explicit=min(int(magnitude),19999)
        if expnegative:explicit=-explicit
    whole,point,fraction=mantissa.partition('.')
    # strtodg delays fractional zeros until the next nonzero digit and drops
    # terminal fractional zeros, while retaining terminal integer zeros.
    fraction=fraction.rstrip('0') if point else ''
    digits=(whole+fraction).lstrip('0')
    if not digits:return -0.0 if negative else 0.0
    exponent=explicit-len(fraction)
    canonical=digits+'e'+str(exponent)
    value=float(canonical)
    bits=struct.unpack('<Q',struct.pack('<d',value))[0]
    ieee_exponent=(bits>>52)&0x7ff
    if (0<ieee_exponent<0x7ff and bits&((1<<52)-1)==(1<<52)-1):
        successor=math.nextafter(value,math.inf)
        if math.isfinite(successor) and Decimal(canonical)>Decimal.from_float(value):
            seed,binary_exponent=_initial_candidate(digits,exponent)
            if _seed_above(seed,binary_exponent,successor):value=successor
            elif _crosses_power2(digits,exponent,value,seed,binary_exponent,ieee_exponent):
                # The legacy wrapper packs its already-wrong exponent directly
                # into the IEEE word; it does not perform gradual underflow.
                packed=(bits-(52<<52))&((1<<64)-1)
                value=struct.unpack('<d',struct.pack('<Q',packed))[0]
    return -value if negative else value


class GlyphError(Exception):
    def __init__(self, message, position):
        self.message = message if isinstance(message, bytes) else message.encode('ascii')
        self.position = position


def first_identifier(byte):
    return 65 <= byte <= 90 or 97 <= byte <= 122 or byte == 95


def rest_identifier(byte):
    return first_identifier(byte) or 48 <= byte <= 57


class Parser:
    def __init__(self, data, variables):
        self.data = data
        self.size = len(data)
        self.pos = 0
        self.variables = variables

    def spaces(self):
        while self.pos < self.size and self.data[self.pos] in (32, 9):
            self.pos += 1

    def primary(self):
        self.spaces()
        start = self.pos
        if start == self.size:
            raise GlyphError('expected expression', self.size)
        data = self.data
        byte = data[start]
        if byte == 40:
            self.pos += 1
            value = self.expression()
            self.spaces()
            if self.pos == self.size or data[self.pos] != 41:
                raise GlyphError("expected ')'", self.pos)
            self.pos += 1
            return value
        if 48 <= byte <= 57 or byte == 46:
            end = start
            while end < self.size and 48 <= data[end] <= 57:
                end += 1
            is_float = False
            if end < self.size and data[end] == 46:
                if end == start and (end+1 == self.size or not 48 <= data[end+1] <= 57):
                    raise GlyphError(b"unexpected character '.'", start)
                is_float = True
                end += 1
                while end < self.size and 48 <= data[end] <= 57:
                    end += 1
            if end < self.size and data[end] in (69, 101):
                exp = end + 1
                if exp < self.size and data[exp] in (43, 45):
                    exp += 1
                if exp < self.size and 48 <= data[exp] <= 57:
                    is_float = True
                    end = exp + 1
                    while end < self.size and 48 <= data[end] <= 57:
                        end += 1
            if end-start >= 512:
                raise GlyphError('integer literal out of range', start)
            self.pos = end
            token = data[start:end]
            if is_float:
                return parse_float_legacy(token)
            value = int(token)
            if value > MAX_INT:
                raise GlyphError('integer literal out of range', start)
            return value
        if first_identifier(byte):
            end = start+1
            while end < self.size and rest_identifier(data[end]):
                end += 1
            self.pos = end
            if end-start > 31:
                raise GlyphError('identifier too long', start)
            name = data[start:end]
            if name not in self.variables:
                raise GlyphError(b"undefined variable '"+name+b"'", start)
            return self.variables[name]
        raise GlyphError(b"unexpected character '"+bytes([byte])+b"'", start)

    def power(self):
        self.spaces()
        if self.pos < self.size and self.data[self.pos] == 45:
            self.pos += 1
            value = self.power()
            return wrap(-value) if type(value) is int else -value
        value = self.primary()
        self.spaces()
        if self.pos < self.size and self.data[self.pos] == 94:
            self.pos += 1
            exponent = self.power()
            if type(value) is int and type(exponent) is int and exponent >= 0:
                return wrap(pow(value & MASK, exponent, 1 << 64))
            return fp_pow(float(value), float(exponent))
        return value

    def term(self):
        value = self.power()
        while True:
            self.spaces()
            if self.pos == self.size or self.data[self.pos] not in (42, 47, 37):
                return value
            op, start = self.data[self.pos], self.pos
            self.pos += 1
            right = self.power()
            integers = type(value) is int and type(right) is int
            if op == 37:
                if not integers:
                    raise GlyphError('modulo requires integer operands', start)
                if right == 0:
                    raise GlyphError('division by zero', start)
                quotient = abs(value)//abs(right)
                if (value < 0) != (right < 0):
                    quotient = -quotient
                value -= quotient * right
            elif op == 42:
                value = wrap(value*right) if integers else float(value)*float(right)
            elif integers:
                if right == 0:
                    raise GlyphError('division by zero', start)
                quotient = abs(value)//abs(right)
                value = wrap(-quotient if (value < 0) != (right < 0) else quotient)
            else:
                value = fp_div(float(value), float(right))

    def expression(self):
        value = self.term()
        while True:
            self.spaces()
            if self.pos == self.size or self.data[self.pos] not in (43, 45):
                return value
            op = self.data[self.pos]
            self.pos += 1
            right = self.term()
            integers = type(value) is int and type(right) is int
            if integers:
                value = wrap(value+right if op == 43 else value-right)
            elif op == 43:
                value = float(value)+float(right)
            else:
                value = float(value)-float(right)


def run(data):
    data = data.split(b'\x1a', 1)[0].replace(b'\r\n', b'\n')
    lines = data.split(b'\n')
    variables = {}
    output = bytearray()
    for line_number, line in enumerate(lines, 1):
        if line_number < len(lines) and line.endswith(b'\r'):
            line = line[:-1]
        line = line.split(b'#', 1)[0]
        parser = Parser(line, variables)
        parser.spaces()
        if parser.pos == parser.size:
            continue
        start = parser.pos
        name = None
        if first_identifier(line[start]):
            end = start+1
            while end < len(line) and rest_identifier(line[end]):
                end += 1
            look = end
            while look < len(line) and line[look] in (32, 9):
                look += 1
            if look < len(line) and line[look] == 61:
                name = line[start:end]
                parser.pos = look+1
        try:
            if name is not None and len(name) > 31:
                raise GlyphError('identifier too long', start)
            value = parser.expression()
            parser.spaces()
            if parser.pos < len(line):
                message = 'unexpected token' if name is None and line[parser.pos] in (41, 44, 61) else 'trailing input'
                raise GlyphError(message, parser.pos)
            if name is not None:
                if name not in variables and len(variables) >= 128:
                    raise GlyphError('too many variables', start)
                variables[name] = value
            elif type(value) is int:
                output.extend(str(value).encode('ascii')+b'\r\n')
            else:
                output.extend(format_float(value)+b'\r\n')
        except GlyphError as error:
            stderr = (b'error line '+str(line_number).encode()+b': '+error.message
                      +b' at column '+str(error.position+1).encode()+b'\r\n')
            return bytes(output), stderr, 2
    return bytes(output), b'', 0


def main():
    sys.setrecursionlimit(100000)
    out, err, status = run(sys.stdin.buffer.read())
    sys.stdout.buffer.write(out)
    sys.stdout.buffer.flush()
    sys.stderr.buffer.write(err)
    sys.stderr.buffer.flush()
    return status


if __name__ == '__main__':
    raise SystemExit(main())
