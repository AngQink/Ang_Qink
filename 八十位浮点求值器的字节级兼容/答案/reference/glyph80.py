"""GLYPH-80 standalone behavioral reconstruction; standard library only."""
import sys
from types import SimpleNamespace
import math
import struct
from decimal import Decimal, localcontext
from math import isqrt
from decimal import Decimal as _TD, localcontext as _tcontext, ROUND_HALF_EVEN as _THE
import re

_s_SIGN = 1 << 79
_s_MANT = (1 << 64) - 1
_s_INTBIT = 1 << 63
_s_QUIET = 1 << 62
_s_BIAS = 16383
_s_MIN_POWER = -16445
_s_ZERO = 0
_s_NEGZERO = _s_SIGN
_s_ONE = _s_BIAS << 64 | _s_INTBIT
_s_INF = 32767 << 64 | _s_INTBIT
_s_NINF = _s_SIGN | _s_INF
_s_NAN = 32767 << 64 | _s_INTBIT | _s_QUIET
_s_NNAN = _s_SIGN | _s_NAN

def _s_signbit(x):
    return bool(x & _s_SIGN)

def _s_neg(x):
    return x ^ _s_SIGN

def _s_isnan(x):
    return x >> 64 & 32767 == 32767 and x & _s_MANT != _s_INTBIT

def _s_isinf(x):
    return x >> 64 & 32767 == 32767 and x & _s_MANT == _s_INTBIT

def _s_iszero(x):
    return not x & ~_s_SIGN

def _s_quiet(x):
    return x | _s_QUIET

def _s__nan(a, b=None):
    if b is None or not _s_isnan(b):
        return _s_quiet(a)
    if not _s_isnan(a):
        return _s_quiet(b)
    aq, bq = (bool(a & _s_QUIET), bool(b & _s_QUIET))
    if aq != bq:
        return _s_quiet(a if aq else b)
    ma, mb = ((a | _s_QUIET) & _s_MANT, (b | _s_QUIET) & _s_MANT)
    if ma != mb:
        return _s_quiet(a if ma > mb else b)
    return _s_quiet(min(a, b))

def _s__round_shift(value, shift):
    if shift <= 0:
        return value << -shift
    if shift > value.bit_length() + 1:
        return 0
    q, r = divmod(value, 1 << shift)
    half = 1 << shift - 1
    return q + int(r > half or (r == half and q & 1))

def _s__scaled(sign, mantissa, power):
    if not mantissa:
        return _s_SIGN if sign else 0
    top = power + mantissa.bit_length() - 1
    if top > 16383:
        return _s_NINF if sign else _s_INF
    quantum = max(top - 63, _s_MIN_POWER)
    m = _s__round_shift(mantissa, quantum - power)
    if not m:
        return _s_SIGN if sign else 0
    if m >= 1 << 64:
        m >>= 1
        quantum += 1
    exponent = quantum + 63 + _s_BIAS if m >= _s_INTBIT else 0
    if exponent >= 32767:
        return _s_NINF if sign else _s_INF
    return (_s_SIGN if sign else 0) | exponent << 64 | m

def _s__finite(x):
    exp = x >> 64 & 32767
    return (x & _s_MANT, (exp if exp else 1) - _s_BIAS - 63)

def _s_from_int(n):
    return _s__scaled(n < 0, abs(n), 0)

def _s_from_ratio(n, d=1, negative_zero=False):
    if d < 0:
        n, d = (-n, -d)
    if not d:
        if not n:
            return _s_NNAN
        return _s_NINF if n < 0 else _s_INF
    sign = n < 0
    n = abs(n)
    if not n:
        return _s_SIGN if negative_zero else 0
    exponent = n.bit_length() - d.bit_length()
    if n < d << exponent if exponent >= 0 else n << -exponent < d:
        exponent -= 1
    if exponent > 16383:
        return _s_NINF if sign else _s_INF
    quantum = max(exponent - 63, _s_MIN_POWER)
    if quantum >= 0:
        q, r = divmod(n, d << quantum)
        divisor = d << quantum
    else:
        q, r = divmod(n << -quantum, d)
        divisor = d
    if r * 2 > divisor or (r * 2 == divisor and q & 1):
        q += 1
    return _s__scaled(sign, q, quantum)

def _s_from_double(value):
    bits = struct.unpack('<Q', struct.pack('<d', value))[0]
    sign = _s_SIGN if bits >> 63 else 0
    exponent = bits >> 52 & 2047
    frac = bits & (1 << 52) - 1
    if exponent == 2047:
        return sign | (32767 << 64 | _s_INTBIT | frac << 11 | _s_QUIET if frac else _s_INF)
    if exponent:
        return sign | exponent - 1023 + _s_BIAS << 64 | (1 << 52 | frac) << 11
    return sign | _s__scaled(False, frac, -1074)

def _s__normal_seed(value):
    m, e = math.frexp(value)
    return (m * 2, e - 1)
_s__TENS = tuple((float('1e' + str(i)) for i in range(16)))
_s__BIG = tuple((float('1e' + str(16 << i)) for i in range(4)))
_s__TINY = tuple((float('1e-' + str(16 << i)) for i in range(4)))

def _s__decimal_seed(digits, exponent):
    count = min(16, len(digits))
    head = digits[:count]
    value = float(int(head[:9])) * _s__TENS[count - 9] + float(int(head[9:])) if count > 9 else float(int(head))
    exponent += len(digits) - count
    negative = exponent < 0
    power = abs(exponent)
    small = power & 15
    if small:
        value = value / _s__TENS[small] if negative else value * _s__TENS[small]
    blocks = power >> 4
    external = 0
    if blocks:
        while blocks >= 16:
            value, e = _s__normal_seed(value)
            external += e
            value *= 1e-256 if negative else 1e+256
            blocks -= 16
        value, e = _s__normal_seed(value)
        external += e
        index = 0
        while blocks:
            if blocks & 1:
                value *= (_s__TINY if negative else _s__BIG)[index]
            blocks >>= 1
            index += 1
    return (value, external)

def _s__truncated_bigint(n):
    size = n.bit_length()
    mant = n >> size - 53 if size >= 53 else n << 53 - size
    return (mant / (1 << 52), size)

def _s_parse_literal(token):
    s = token.decode('ascii')
    mant, marker, exptext = s.lower().partition('e')
    explicit = 0
    if marker:
        negative = exptext.startswith('-')
        mag = exptext[1:] if exptext[:1] in '+-' else exptext
        mag = mag.lstrip('0')
        explicit = 19999 if len(mag) > 5 else min(int(mag or '0'), 19999)
        if negative:
            explicit = -explicit
    whole, point, frac = mant.partition('.')
    frac = frac.rstrip('0') if point else ''
    digits = (whole + frac).lstrip('0')
    if not digits:
        return _s_ZERO
    exponent = explicit - len(frac)
    canonical = digits + 'e' + str(exponent)
    value = float(canonical)
    bits = struct.unpack('<Q', struct.pack('<d', value))[0]
    field = bits >> 52 & 2047
    if 0 < field < 2047 and bits & (1 << 52) - 1 == (1 << 52) - 1:
        successor = math.nextafter(value, math.inf)
        if math.isfinite(successor):
            vn = int(digits) * 10 ** exponent if exponent >= 0 else int(digits)
            vd = 1 if exponent >= 0 else 10 ** (-exponent)
            xn, xd = value.as_integer_ratio()
            if vn * xd > xn * vd:
                seed, external = _s__decimal_seed(digits, exponent)
                sn, sd = seed.as_integer_ratio()
                if external >= 0:
                    sn <<= external
                else:
                    sd <<= -external
                un, ud = successor.as_integer_ratio()
                if sn * ud > un * sd:
                    value = successor
                elif sn * xd < xn * sd:
                    k = max(-exponent, 0)
                    scale5 = 5 ** k
                    dn = vn * sd - sn * vd
                    dd = vd * sd
                    hp = field - 1076
                    twopower = max(dd.bit_length(), -hp) + 2
                    delta = dn * scale5 * (1 << twopower) // dd
                    half = scale5 << twopower + hp
                    dm, de = _s__truncated_bigint(delta)
                    hm, he = _s__truncated_bigint(half)
                    if de >= he:
                        ratio = math.ldexp(dm, de - he) / hm
                    else:
                        ratio = dm / math.ldexp(hm, he - de)
                    units = ratio * 0.5
                    step = int(units) + int(units - int(units) >= 0.5)
                    up = field - 1075
                    if up >= 0:
                        stepn, stepd = (step << up, 1)
                    else:
                        stepn, stepd = (step, 1 << -up)
                    if (sn * stepd + stepn * sd) * ud >= un * sd * stepd:
                        value = struct.unpack('<d', struct.pack('<Q', bits - (52 << 52) & (1 << 64) - 1))[0]
    return _s_from_double(value)

def _s_to_decimal(x):
    if _s_isnan(x):
        return Decimal('-NaN' if _s_signbit(x) else 'NaN')
    if _s_isinf(x):
        return Decimal('-Infinity' if _s_signbit(x) else 'Infinity')
    if _s_iszero(x):
        return Decimal('-0' if _s_signbit(x) else '0')
    m, e = _s__finite(x)
    with localcontext() as ctx:
        ctx.prec = max(100, abs(e) + 100)
        value = Decimal(m) * Decimal(2) ** e
        return -value if _s_signbit(x) else value

def _s_from_decimal(value):
    value = Decimal(value)
    if value.is_nan():
        return _s_NNAN if value.is_signed() else _s_NAN
    if value.is_infinite():
        return _s_NINF if value.is_signed() else _s_INF
    if not value:
        return _s_NEGZERO if value.is_signed() else _s_ZERO
    if value.adjusted() > 5000:
        return _s_NINF if value.is_signed() else _s_INF
    if value.adjusted() < -5000:
        return _s_NEGZERO if value.is_signed() else _s_ZERO
    n, d = value.as_integer_ratio()
    return _s_from_ratio(n, d)

def _s_to_double(x):
    return float(_s_to_decimal(x))

def _s_add(a, b):
    if _s_isnan(a) or _s_isnan(b):
        return _s__nan(a, b)
    if _s_isinf(a):
        return _s_NNAN if _s_isinf(b) and _s_signbit(a) != _s_signbit(b) else a
    if _s_isinf(b):
        return b
    ma, ea = _s__finite(a)
    mb, eb = _s__finite(b)
    e = min(ea, eb)
    value = (-ma if _s_signbit(a) else ma) << ea - e
    value += (-mb if _s_signbit(b) else mb) << eb - e
    if not value:
        return _s_NEGZERO if _s_signbit(a) and _s_signbit(b) else _s_ZERO
    return _s__scaled(value < 0, abs(value), e)

def _s_sub(a, b):
    if _s_isnan(a) or _s_isnan(b):
        return _s__nan(a, b)
    return _s_add(a, _s_neg(b))

def _s_mul(a, b):
    if _s_isnan(a) or _s_isnan(b):
        return _s__nan(a, b)
    sign = _s_signbit(a) ^ _s_signbit(b)
    if _s_isinf(a) or _s_isinf(b):
        if _s_iszero(a) or _s_iszero(b):
            return _s_NNAN
        return _s_NINF if sign else _s_INF
    ma, ea = _s__finite(a)
    mb, eb = _s__finite(b)
    return _s__scaled(sign, ma * mb, ea + eb)

def _s_div(a, b):
    if _s_isnan(a) or _s_isnan(b):
        return _s__nan(a, b)
    sign = _s_signbit(a) ^ _s_signbit(b)
    if _s_isinf(a):
        if _s_isinf(b):
            return _s_NNAN
        return _s_NINF if sign else _s_INF
    if _s_isinf(b):
        return _s_NEGZERO if sign else _s_ZERO
    if _s_iszero(b):
        if _s_iszero(a):
            return _s_NNAN
        return _s_NINF if sign else _s_INF
    if _s_iszero(a):
        return _s_NEGZERO if sign else _s_ZERO
    ma, ea = _s__finite(a)
    mb, eb = _s__finite(b)
    shift = ea - eb
    if shift >= 0:
        ma <<= shift
    else:
        mb <<= -shift
    return _s_from_ratio(-ma if sign else ma, mb)

def _s_as_ratio(x):
    m, e = _s__finite(x)
    if _s_signbit(x):
        m = -m
    return (m << e, 1) if e >= 0 else (m, 1 << -e)

sf=SimpleNamespace(BIAS=_s_BIAS,INF=_s_INF,INTBIT=_s_INTBIT,MANT=_s_MANT,MIN_POWER=_s_MIN_POWER,NAN=_s_NAN,NEGZERO=_s_NEGZERO,NINF=_s_NINF,NNAN=_s_NNAN,ONE=_s_ONE,QUIET=_s_QUIET,SIGN=_s_SIGN,ZERO=_s_ZERO,_BIG=_s__BIG,_TENS=_s__TENS,_TINY=_s__TINY,_decimal_seed=_s__decimal_seed,_finite=_s__finite,_nan=_s__nan,_normal_seed=_s__normal_seed,_round_shift=_s__round_shift,_scaled=_s__scaled,_truncated_bigint=_s__truncated_bigint,add=_s_add,as_ratio=_s_as_ratio,div=_s_div,from_decimal=_s_from_decimal,from_double=_s_from_double,from_int=_s_from_int,from_ratio=_s_from_ratio,isinf=_s_isinf,isnan=_s_isnan,iszero=_s_iszero,mul=_s_mul,neg=_s_neg,parse_literal=_s_parse_literal,quiet=_s_quiet,signbit=_s_signbit,sub=_s_sub,to_decimal=_s_to_decimal,to_double=_s_to_double)

_e__M = (1 << 64) - 1
_e__S = 1 << 79
_e__ABS = _e__S - 1
_e_ZERO = 0
_e_ONE = 302222231531620438900736
_e_HALF = 302203784787546729349120
_e_INF = 604453686435277732577280
_e_NAN = 604458298121296159965184
_e_LN2_80 = 302207347724155077228972
_e_L2E_80 = 302226314672681428447420
_e_EXP_A = 301898018925377515092512
_e_EXP_B = 302226314607632603676672
_e_EXP_HI = 302465602141187010951596
_e_EXP_LO = 906928510387672906263344
_e__LN2_DEC = Decimal('0.693147180559945309417232121458176568075500134360255254120680009493393621969694715605863326996418687542001481020570685733685520235758130557032670751635')
_e__LOG_C68 = Decimal('2.8853900817779268147210934569724116727229557000100612640380859375')
_e__SQRT2_DEC = Decimal('1.4142135623730950488016887242096980785696718753769480731766797379907324784621070388503875343276415727350138462309122970249248360558507372126441214971')
_e__LOG_CO = tuple(map(Decimal, ('0.333333333333333331843732066042065457844563660020728075369495802838335830467966627605836177416118471644542490274293243295', '0.200000000000000734439784892796936864712551497338256132952060783533319416831269540577551773042356158052954973192837209033', '0.142857142857025399396625262040660957125936720585372538451012561291211299586342328623757240106663529990139144908690789848', '0.111111111118206909940961756344749958689462697700796716136774890266444442281482151317643567274530195244312388267490251005', '0.090909091047465000926716289233340497584541043036801172154816994381599126948086787336483150708374356362159043373351997167', '0.076923023205087254869361895898667639345602549422165162437124153485590172566072743390446833134681999156178249927632726893', '0.066670940297492366673798501794165825217594423026748379324813302851115771124634136213357698865926191787783504601329461584', '0.058635617026839970235368220440852335286933530215179393705901360571364347755142817502783110772820265263251942482797463872', '0.057541358084505288212169544147949481907126376218307157012014847846262720961604471827963448347122701063211146223194461773', '-0.023526203685803536947912314503775451064560932914000777690163519095749726153230710969624058515402891828944721822177730631', '0.485125029873910372497989327268871076677634938063747051193178573804913353099022187759740947102166232753695088069298557518')))

def _e__ratio(x):
    e = x >> 64 & 32767
    m = x & _e__M
    k = (e or 1) - 16383 - 63
    n, d = (m << k, 1) if k >= 0 else (m, 1 << -k)
    return (-n if x & _e__S else n, d)

def _e__trunc(x):
    n, d = _e__ratio(x)
    return -(abs(n) // d) if n < 0 else n // d

def _e__cmp(a, b):
    if sf.iszero(a) and sf.iszero(b):
        return 0
    sa, sb = (bool(a & _e__S), bool(b & _e__S))
    if sa != sb:
        return -1 if sa else 1
    a &= _e__ABS
    b &= _e__ABS
    return (b > a) - (b < a) if sa else (a > b) - (a < b)

def _e__dec(x):
    n, d = _e__ratio(x)
    return Decimal(n) / Decimal(d)

def _e__fromdec(x):
    if x.is_nan():
        return _e_NAN | (_e__S if x.is_signed() else 0)
    if x.is_infinite():
        return _e_INF | (_e__S if x.is_signed() else 0)
    if not x:
        return _e__S if x.is_signed() else 0
    n, d = x.as_integer_ratio()
    return sf.from_ratio(n, d)

def _e__roundp(d, p=68):
    sign = d.is_signed()
    n, q = abs(d).as_integer_ratio()
    if not n:
        return d
    e = n.bit_length() - q.bit_length()
    if n << max(-e, 0) < q << max(e, 0):
        e -= 1
    sh = p - 1 - e
    if sh >= 0:
        n <<= sh
    else:
        q <<= -sh
    m, r = divmod(n, q)
    if 2 * r > q or (2 * r == q and m & 1):
        m += 1
    z = Decimal(m) * Decimal(2) ** (-sh)
    return -z if sign else z

def _e_scale(x, n):
    if sf.isnan(x) or sf.isinf(x) or sf.iszero(x):
        return x
    if n > 40000:
        return _e_INF | x & _e__S
    if n < -40000:
        return x & _e__S
    a, b = _e__ratio(x)
    if n >= 0:
        a <<= n
    else:
        b <<= -n
    return sf.from_ratio(a, b)

def _e_sqrt80(x):
    if sf.isnan(x):
        return x
    if sf.iszero(x):
        return x
    if x & _e__S:
        return _e_NAN | _e__S
    if sf.isinf(x):
        return x
    m = x & _e__M
    k = (x >> 64 & 32767 or 1) - 16383 - 63
    if k & 1:
        m <<= 1
        k -= 1
    t = 63 - (m.bit_length() - 1) // 2
    z = m << 2 * t
    q = isqrt(z)
    if 4 * z > (2 * q + 1) ** 2:
        q += 1
    k = k // 2 - t
    return sf.from_ratio(q << k, 1) if k >= 0 else sf.from_ratio(q, 1 << -k)

def _e_f2xm1(x):
    if sf.isnan(x):
        return x
    if sf.iszero(x):
        return x
    with localcontext() as ctx:
        ctx.prec = 110
        d = _e__dec(x)
        if abs(d) < Decimal('1e-35'):
            z = d * _e__LN2_DEC
            z = z + z * z / 2
        else:
            z = (d * _e__LN2_DEC).exp() - 1
        return _e__fromdec(z)

def _e_fyl2x(x, y=_e_ONE, plus1=False):
    if sf.isnan(x):
        return x
    if sf.isnan(y):
        return y
    with localcontext() as ctx:
        ctx.prec = 200
        if plus1:
            d = _e__dec(x)
            n = 0
            t = _e__roundp(d / (d + 2))
        else:
            mant = x & _e__M
            exp = x >> 64 & 32767
            n = (exp or 1) - 16383
            shift = 64 - mant.bit_length()
            mant <<= shift
            n -= shift
            m = Decimal(mant) / Decimal(2) ** 63
            if m > _e__SQRT2_DEC:
                m /= 2
                n += 1
            t = _e__roundp((m - 1) / (m + 1))
        a = _e__roundp(t * _e__LOG_C68)
        u = _e__roundp(t * t)
        p = _e__LOG_CO[-1]
        for c in _e__LOG_CO[-2::-1]:
            p = _e__roundp(c + _e__roundp(u * p))
        b = _e__roundp(_e__roundp(_e__roundp(t * u) * p) * _e__LOG_C68)
        z = _e__roundp(_e__roundp(Decimal(n) + a) + b)
        return _e__fromdec(z * _e__dec(y))

def _e_exp80(x):
    if sf.isnan(x):
        return x
    if sf.isinf(x):
        return _e_ZERO if x & _e__S else _e_INF
    if sf.iszero(x):
        return _e_ONE
    if _e__cmp(x, _e_EXP_HI) > 0:
        return _e_INF
    if _e__cmp(x, _e_EXP_LO) < 0:
        return _e_ZERO
    n = _e__trunc(sf.mul(_e_L2E_80, x))
    i = _e__trunc(x)
    ir = sf.from_int(i)
    a = sf.sub(sf.mul(ir, _e_EXP_B), sf.from_int(n))
    b = sf.mul(sf.sub(x, ir), _e_EXP_B)
    a = sf.add(a, b)
    a = sf.add(a, sf.mul(_e_EXP_A, x))
    return _e_scale(sf.add(_e_ONE, _e_f2xm1(a)), n)

def _e_exp2_80(x):
    if sf.isnan(x):
        return x
    if sf.isinf(x):
        return _e_ZERO if x & _e__S else _e_INF
    n = _e__trunc(x)
    frac = sf.sub(x, sf.from_int(n))
    return _e_scale(sf.add(_e_ONE, _e_f2xm1(frac)), n)

def _e_log80(x):
    if sf.iszero(x):
        return _e_INF | _e__S
    if sf.isnan(x) or x & _e__S:
        return _e_NAN
    if sf.isinf(x):
        return _e_INF
    a = sf.sub(x, _e_ONE)
    if _e__cmp(a & _e__ABS, sf.from_double(0.29)) <= 0:
        return _e_fyl2x(a, _e_LN2_80, True)
    return _e_fyl2x(x, _e_LN2_80)

def _e_log2_80(x):
    if sf.isnan(x) or sf.isinf(x):
        return x
    if sf.iszero(x):
        return _e_INF | _e__S
    a = sf.sub(x, _e_ONE)
    if _e__cmp(a & _e__ABS, sf.from_double(0.29)) <= 0:
        return _e_fyl2x(a, _e_ONE, True)
    return _e_fyl2x(x, _e_ONE)

def _e__powi(x, n):
    if n == 0 or x == _e_ONE:
        return _e_ONE
    if sf.isnan(x):
        return _e_NAN | x & _e__S
    odd = n & 1
    s = x & _e__S if odd else 0
    if sf.iszero(x):
        return (_e_INF if n < 0 else _e_ZERO) | s
    if sf.isinf(x):
        return (_e_ZERO if n < 0 else _e_INF) | s
    a = x & _e__ABS
    if n < 0:
        n = -n
        a = sf.div(_e_ONE, a)
    if n == 1:
        return a | s
    r = a if n & 1 else _e_ONE
    n >>= 1
    while n:
        a = sf.mul(a, a)
        if n & 1:
            r = sf.mul(r, a)
        n >>= 1
    return r | s

def _e_pow80(x, y):
    if sf.iszero(y) or x == _e_ONE:
        return _e_ONE
    if sf.isnan(x) or sf.isnan(y):
        return _e_NAN | x & _e__S
    ax = x & _e__ABS
    if sf.isinf(y):
        if ax == _e_ONE:
            return _e_ONE
        above = _e__cmp(ax, _e_ONE) > 0
        return _e_INF if above != bool(y & _e__S) else _e_ZERO
    yi = _e__trunc(y)
    integral = sf.from_int(yi) == y or sf.iszero(y)
    odd = integral and bool(yi & 1)
    if sf.iszero(x):
        return (_e_INF if y & _e__S else _e_ZERO) | (x & _e__S if odd else 0)
    if sf.isinf(x):
        return (_e_ZERO if y & _e__S else _e_INF) | (x & _e__S if odd else 0)
    if integral and -2147483648 <= yi <= 2147483647:
        return _e__powi(x, yi)
    if x & _e__S and (not integral):
        return _e_NAN | _e__S
    if y == _e_HALF:
        return _e_sqrt80(x)
    r = _e_exp2_80(sf.mul(y, _e_log2_80(ax)))
    return sf.neg(r) if x & _e__S and odd else r

_f__F2_LN2 = Decimal('0.693147180559945309417232121458176568075500134360255254120680009493393621969694715605863326996418687542001481020570685733685520235758130557032670751635')

def _f_f2xm1_model(raw):
    if sf.isnan(raw):
        return sf.quiet(raw)
    if sf.iszero(raw):
        return raw
    if sf.isinf(raw):
        return sf.neg(sf.ONE) if raw & sf.SIGN else raw
    magnitude = raw & sf.SIGN - 1
    if magnitude > sf.ONE:
        return raw
    if raw == sf.ONE:
        return sf.ONE
    if raw == sf.neg(sf.ONE):
        return sf.BIAS - 1 << 64 | sf.INTBIT | sf.SIGN
    with localcontext() as ctx:
        ctx.prec = 120
        n, d = sf.as_ratio(raw)
        z = Decimal(n) / Decimal(d) * _f__F2_LN2
        if abs(z) < Decimal('1e-35'):
            value = z + z * z / 2 + z * z * z / 6
        else:
            value = z.exp() - 1
        return sf.from_decimal(value)

_a_ATAN_SIGN = 1 << 79
_a_ATAN_MANT = (1 << 64) - 1
_a_ATAN_PIO64 = 302227496198499738370613
_a_ATAN_PI66 = Decimal('3.1415926535897932384585988507819109827323700301349163055419921875')
_a_ATAN_CO = tuple(map(Decimal, ('9.791843002689999686527499989097123034298419952392578125E-21', '-2.08442646781683504908500026431283913552761077880859375E-20', '2.0077006657592766369901937650865875184535980224609375E-20', '-2.15509154417406312287397440741187892854213714599609375E-20', '1.93657755103487427827957390036317519843578338623046875E-20', '-2.024547054405594348480690314318053424358367919921875E-20', '1.857668533678526745500647621156531386077404022216796875E-20', '-1.900659495255185016393539854107075370848178863525390625E-20', '1.67748427189700011208373098270385526120662689208984375E-20', '-1.739697914733663586250855814796523191034793853759765625E-20', '1.5216558519294098861251995913335122168064117431640625E-20', '-1.491848391753197999864966050154180265963077545166015625E-20', '1.248208208212957526228592541883699595928192138671875E-20', '-1.2482255741449040098434153378548217006027698516845703125E-20', '9.5634265196381129658931286030565388500690460205078125E-21', '-9.464562785496276331453913144287071190774440765380859375E-21', '6.632719148782227625016361116649932228028774261474609375E-21', '-4.841066296152206349656665906877606175839900970458984375E-21', '1.86477973786668242694997132957723806612193584442138671875E-21', '-1.441447252911421360310750827693482278846204280853271484375E-21', '3.2086261686551180959126039482498526922427117824554443359375E-22', '-4.356664577731824729289744624338709400035440921783447265625E-22', '7.48668559420736265223872418772543824161402881145477294921875E-23', '-1.70869390800509435117404688497799725155346095561981201171875E-22', '4.764554077387128335797916722782474607811309397220611572265625E-23')))

def _a__at_dec(x):
    m = x & _a_ATAN_MANT
    e = x >> 64 & 32767 or 1
    return Decimal(m) * Decimal(2) ** (e - 16383 - 63)

def _a__at_round(value, p=68):
    negative = value.is_signed()
    n, d = abs(value).as_integer_ratio()
    if not n:
        return value
    e = n.bit_length() - d.bit_length()
    if n << max(-e, 0) < d << max(e, 0):
        e -= 1
    shift = p - 1 - e
    if shift >= 0:
        n <<= shift
    else:
        d <<= -shift
    q, r = divmod(n, d)
    if 2 * r > d or (2 * r == d and q & 1):
        q += 1
    result = Decimal(q) * Decimal(2) ** (-shift)
    return -result if negative else result

def _a__at_math(x):
    for _ in range(4):
        x = x / (1 + (1 + x * x).sqrt())
    z = -x * x
    term = total = x
    for k in range(1, 150):
        term *= z
        add = term / (2 * k + 1)
        total += add
        if abs(add) < Decimal('1e-210'):
            break
    return total * 16

def _a__at_bias(x):
    z = 2 * x * x - 1
    b1 = b2 = Decimal(0)
    for c in _a_ATAN_CO[:0:-1]:
        b0 = c + 2 * z * b1 - b2
        b2, b1 = (b1, b0)
    return _a_ATAN_CO[0] + z * b1 - b2

def _a__at_core(x):
    if x < Decimal(2) ** (-34):
        return x
    u = _a__at_round(x * x)
    s = u.sqrt()
    p = (_a__at_math(s) - s) / (s * u)
    correction = _a__at_round(_a__at_round(x * u) * (p + _a__at_bias(x)))
    return x + correction

def _a_atan80(x):
    if sf.isnan(x):
        return x | 1 << 62
    if sf.iszero(x):
        return x
    sign = x & _a_ATAN_SIGN
    if sf.isinf(x):
        return _a_ATAN_PIO64 | sign
    with localcontext() as ctx:
        ctx.prec = 200
        value = _a__at_dec(x & ~_a_ATAN_SIGN)
        if value < Decimal(2) ** (-34):
            return x
        if value > 1:
            inverse = _a__at_round(1 / value)
            angle = _a__at_round(_a__at_core(inverse))
            result = _a_ATAN_PI66 / 2 - angle
        else:
            result = _a__at_core(value)
        n, d = result.as_integer_ratio()
        return sf.from_ratio(n, d) | sign

_t__T_SIGN = 1 << 79
_t__T_MASK = (1 << 64) - 1
_t__T_ONE = 302222231531620438900736
_t__T_PI2 = 302227496198499738370613
_t__T_QNAN = 604458298121296159965184
_t__T_INDEF = 1208921207928610747318272
_t__T_PI = _TD('3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196')
_t__T_PI66 = _TD('3.1415926535897932384585988507819109827323700301349163055419921875')
_t__T_SCO = tuple(map(_TD, ['-0.1666666666666666664026747314390763943237061539548449218273162841796875', '0.008333333333333322504500775044161408460881406331151784646256904428203900655110677083333333333333333333333333333333333333333333333333', '-0.0001984126984125479676230068387680728958930824974814750959691111116655289180695064484126984126984126984126984126984126984126984126984', '0.000002755731921406288166641541767840964547205513523941370638044685703526518752755731922398589065255731922398589065255731922398589065256', '-2.505210488122599405306595301948554618352819895344310082795051536786359377505210838544171877505210838544171877505210838544171877505E-8', '1.605836307300008373113027438760116832085193172698976983245766444229036459939237717015494793272571050348828126605904383682161459939E-10', '-7.578535214173431366950652443598899032817943925353505732599498181224578380663036747692832348917005001661086317170973255629340285425E-13']))
_t__T_CCO = tuple(map(_TD, ['-0.5', '0.04166666666666666664085305045848368237473839370092291526740761279749373594919840494791666666666666666666666666666666666666666666667', '-0.00138888888888888807003635210720971163503937015022673978884830561602856224878452630292191129745858288322693836985577731682139562619762503932285866801685', '0.0000248015873015772143734258750502258557179552047639512584395321238903154553312762951831552088422059965224262206071205625408001390374551627059671709029015', '-2.75573192177774333349192732619371839999535366833280302810168169650335354846399078353758627712147852483539271500074471573462143201930984296058661682549E-7', '2.08767548916012000142139536026500846787113253803466138603431733357392769770148975969978452629782223150037478671250377288634740415073810291996695591155E-9', '-1.14703510099189601637587427059224904418727150579891290195766251981077250447143776541104590263518106626499410354479134556632282333745739403073957482320E-11', '4.74062786022872015270345777413250585129857407317175483631763182620908304554369463276771446268858265727740619356205516482794300878711602376010114055790E-14']))

def _t__t_ratio(x):
    m = x & _t__T_MASK
    e = x >> 64 & 32767
    k = max(e, 1) - 16446
    if k >= 0:
        return (m << k, 1)
    return (m, 1 << -k)

def _t__t_reduce_huge(x):
    """The assembly's FPREM1 loop with divisor 2*FLDPI (64-bit pi)."""
    n, d = _t__t_ratio(x)
    a = n << 61
    b = d * 14488038916154245685
    q, rem = divmod(a, b)
    if rem * 2 > b or (rem * 2 == b and q & 1):
        rem -= b
    return sf.from_ratio(rem, d << 61)

def _t__t_dec(x):
    n, d = _t__t_ratio(x)
    v = _TD(n) / _TD(d)
    return -v if x & _t__T_SIGN else v

def _t__t_sincos(x):
    q = (x / (_t__T_PI66 / 2)).to_integral_value(rounding=_THE)
    r = x - q * (_t__T_PI66 / 2)
    rr = r * r
    s = st = r
    co = ct = _TD(1)
    for k in range(1, 100):
        st *= -rr / _TD(2 * k * (2 * k + 1))
        ct *= -rr / _TD((2 * k - 1) * (2 * k))
        s += st
        co += ct
        if abs(st) < _TD('1e-140') and abs(ct) < _TD('1e-140'):
            break
    return ((s, co), (co, -s), (-s, -co), (-co, s))[int(q) & 3]

def _t__t_rn68(value):
    if not value:
        return value
    n, d = value.as_integer_ratio()
    negative = n < 0
    n = abs(n)
    exponent = n.bit_length() - d.bit_length()
    if exponent >= 0:
        if n < d << exponent:
            exponent -= 1
    elif n << -exponent < d:
        exponent -= 1
    shift = 67 - exponent
    if shift >= 0:
        a, b = (n << shift, d)
    else:
        a, b = (n, d << -shift)
    q, rem = divmod(a, b)
    if rem * 2 > b or (rem * 2 == b and q & 1):
        q += 1
    result = _TD(q) * _TD(2) ** (-shift)
    return -result if negative else result

def _t__t_hw_sincos(x):
    q = (x / (_t__T_PI66 / 2)).to_integral_value(rounding=_THE)
    r = x - q * (_t__T_PI66 / 2)
    z = _t__t_rn68(r * r)
    p = _t__T_SCO[-1]
    for k in _t__T_SCO[-2::-1]:
        p = _t__t_rn68(k + _t__t_rn68(z * p))
    sine = r + _t__t_rn68(_t__t_rn68(r * z) * p)
    p = _t__T_CCO[-1]
    for k in _t__T_CCO[-2::-1]:
        p = _t__t_rn68(k + _t__t_rn68(z * p))
    cosine = 1 + _t__t_rn68(z * p)
    return ((sine, cosine), (cosine, -sine), (-sine, -cosine), (-cosine, sine))[int(q) & 3]

def _t__t_atan(x):
    inv = x > 1
    if inv:
        x = 1 / x
    for k in range(4):
        x = x / (1 + (1 + x * x).sqrt())
    xx = -x * x
    t = a = x
    for k in range(1, 150):
        t *= xx
        step = t / (2 * k + 1)
        a += step
        if abs(step) < _TD('1e-140'):
            break
    a *= 16
    return _t__T_PI / 2 - a if inv else a

def _t__t_eval(fn, x):
    sign = x & _t__T_SIGN
    ax = x & ~_t__T_SIGN
    e = ax >> 64 & 32767
    m = ax & _t__T_MASK
    if e == 32767:
        if m != 9223372036854775808:
            return x | 4611686018427387904
        if fn == 'atan':
            return _t__T_PI2 | sign
        return _t__T_QNAN if fn in ('sin', 'cos') else _t__T_INDEF
    if not m:
        return _t__T_ONE if fn == 'cos' else x
    if e < 16350:
        return _t__T_ONE if fn == 'cos' else x
    with _tcontext() as ctx:
        ctx.prec = 150
        ctx.Emax = 999999
        ctx.Emin = -999999
        if fn == 'atan':
            result = sf.from_decimal(_t__t_atan(_t__t_dec(ax)))
        else:
            reduced = _t__t_reduce_huge(ax) if e >= 16446 else ax
            s, c = _t__t_sincos(_t__t_dec(reduced)) if fn == 'tan' else _t__t_hw_sincos(_t__t_dec(reduced))
            value = s if fn == 'sin' else c if fn == 'cos' else s / c
            result = sf.from_decimal(value)
    return result ^ sign if fn != 'cos' else result

def _t_sin80(x):
    return _t__t_eval('sin', x)

def _t_cos80(x):
    return _t__t_eval('cos', x)

def _t_tan80(x):
    return _t__t_eval('tan', x)

def _t_atan80(x):
    return _t__t_eval('atan', x)
_t_sin = _t_sin80
_t_cos = _t_cos80
_t_tan = _t_tan80
_t_atan = _t_atan80

_p__NUMBER = re.compile(b'(?:[0-9]+(?:\\.[0-9]*)?|\\.[0-9]+)(?:[eE][+-]?[0-9]+)?')
_p__IDENT = re.compile(b'[A-Za-z_][A-Za-z_0-9]*')

class _p_ParseError(Exception):

    def __init__(self, output):
        self.output = output

class _p__Parser:

    def __init__(self, line, lineno, variables, functions):
        self.s = line
        self.n = len(line)
        self.p = 0
        self.lineno = lineno
        self.variables = variables
        self.functions = functions

    def fail(self, message, pos=None, name=None):
        if pos is None:
            pos = self.p
        msg = b'error line %d: ' % self.lineno + message
        if name is not None:
            msg += b" '" + name + b"'"
        raise _p_ParseError(msg + b' at column %d\r\n' % (pos + 1))

    def unexpected(self):
        self.fail(b"unexpected character '" + self.s[self.p:self.p + 1] + b"'")

    def ws(self):
        while self.p < self.n and self.s[self.p] in (9, 32):
            self.p += 1

    def atom(self):
        self.ws()
        if self.p >= self.n:
            self.fail(b'expected expression', self.n)
        ch = self.s[self.p]
        if ch == 45:
            self.p += 1
            return sf.neg(self.atom())
        if ch == 40:
            self.p += 1
            result = self.expr()
            self.ws()
            if self.p >= self.n or self.s[self.p] != 41:
                self.fail(b"expected ')'")
            self.p += 1
        elif 48 <= ch <= 57 or ch == 46:
            start = self.p
            match = _p__NUMBER.match(self.s, self.p)
            if match is None:
                self.unexpected()
            self.p = match.end()
            if self.p - start > 511:
                self.fail(b'number too long', start)
            result = sf.parse_literal(self.s[start:self.p])
        else:
            start = self.p
            match = _p__IDENT.match(self.s, self.p)
            if match is None:
                self.unexpected()
            self.p = match.end()
            name = match.group()
            if len(name) > 31:
                self.fail(b'identifier too long', start)
            self.ws()
            if self.p < self.n and self.s[self.p] == 40:
                self.p += 1
                self.ws()
                args = []
                if self.p < self.n and self.s[self.p] == 41:
                    self.p += 1
                else:
                    while True:
                        args.append(self.expr())
                        self.ws()
                        if self.p >= self.n:
                            self.fail(b"expected ',' or ')'")
                        ch = self.s[self.p]
                        if ch == 41:
                            self.p += 1
                            break
                        if ch != 44:
                            self.fail(b"expected ',' or ')'")
                        self.p += 1
                        if len(args) >= 2:
                            self.fail(b'too many arguments')
                key = name.decode('ascii')
                arity = 2 if key == 'pow' else 1
                if len(args) != arity:
                    self.fail(b'wrong argument count for', start, name)
                if key not in self.functions:
                    self.fail(b'unknown function', start, name)
                result = self.functions[key][1](*args)
            else:
                if name not in self.variables:
                    self.fail(b'undefined variable', start, name)
                result = self.variables[name]
        self.ws()
        if self.p < self.n and self.s[self.p] == 94:
            self.p += 1
            right = self.atom()
            result = self.functions['pow'][1](result, right)
        return result

    def term(self):
        result = self.atom()
        while True:
            self.ws()
            if self.p >= self.n or self.s[self.p] not in (42, 47):
                return result
            ch = self.s[self.p]
            self.p += 1
            right = self.atom()
            result = sf.mul(result, right) if ch == 42 else sf.div(result, right)

    def expr(self):
        result = self.term()
        while True:
            self.ws()
            if self.p >= self.n or self.s[self.p] not in (43, 45):
                return result
            ch = self.s[self.p]
            self.p += 1
            right = self.term()
            result = sf.add(result, right) if ch == 43 else sf.sub(result, right)

    def statement(self):
        self.ws()
        if self.p == self.n:
            return None
        start = self.p
        name = None
        match = _p__IDENT.match(self.s, self.p)
        if match:
            self.p = match.end()
            self.ws()
            if self.p < self.n and self.s[self.p] == 61:
                name = match.group()
                if len(name) > 31:
                    self.fail(b'identifier too long', start)
                self.p += 1
            else:
                self.p = start
        value = self.expr()
        self.ws()
        if self.p < self.n:
            if name is None and self.s[self.p] in (41, 44, 61):
                self.fail(b'unexpected token')
            self.fail(b'trailing input')
        if name is not None:
            if name not in self.variables and len(self.variables) >= 64:
                self.fail(b'too many variables', start)
            self.variables[name] = value
            return None
        return value

def _p_run(data, functions):
    """Return (stdout_bytes, stderr_bytes, exitcode) for raw stdin bytes."""
    data = data.split(b'\x1a', 1)[0].replace(b'\r\n', b'\n')
    lines = data.split(b'\n')
    output = bytearray()
    variables = {}
    try:
        for lineno, line in enumerate(lines, 1):
            if lineno < len(lines) and line.endswith(b'\r'):
                line = line[:-1]
            line = line.split(b'#', 1)[0]
            value = _p__Parser(line, lineno, variables, functions).statement()
            if value is not None:
                output.extend(value.to_bytes(10, 'little').hex().encode('ascii'))
                output.extend(b'\r\n')
    except _p_ParseError as error:
        return (bytes(output), error.output, 2)
    return (bytes(output), b'', 0)


_e_f2xm1=_f_f2xm1_model
FUNCTIONS={
 'sqrt':(1,_e_sqrt80),'exp':(1,_e_exp80),'log':(1,_e_log80),'pow':(2,_e_pow80),
 'sin':(1,_t_sin80),'cos':(1,_t_cos80),'tan':(1,_t_tan80),'atan':(1,_a_atan80),
}
def main():
    sys.setrecursionlimit(100000)
    out,err,status=_p_run(sys.stdin.buffer.read(),FUNCTIONS)
    sys.stdout.buffer.write(out);sys.stdout.buffer.flush()
    sys.stderr.buffer.write(err);sys.stderr.buffer.flush()
    return status
if __name__=='__main__':
    raise SystemExit(main())

