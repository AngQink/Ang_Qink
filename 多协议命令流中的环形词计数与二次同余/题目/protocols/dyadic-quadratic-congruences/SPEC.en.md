# 模二的幂的二次同余计数 / Counting Solutions to Quadratic Congruences Modulo Powers of Two

This page defines the subprotocol. See the [combined specification](../../README.md) for its entry point, command prefixes, limits, and tests.

Maintain quadratic expressions modulo powers of 2, precisely counting under constraints on the lower bits of variables and finding canonical solutions.

## 1. Quadratic Form and Domain

With the number of variables $d$ and the number of bits $k$ fixed, all variables $x_i$ take integer values in the range $0..2^k-1$. Maintain the polynomial:

```text
F(x) = constant + sum(linear[i]*x_i)
       + sum(q[i][i]*x_i*x_i)
       + sum(q[i][j]*x_i*x_j, i<j)     (mod 2^k)
```

$q$ is an upper triangular coefficient matrix of size $d \times d$, with the lower triangular part guaranteed to be zero. Each cross-term is counted only once, without multiplying by 2. The diagonal terms are squared terms. The coefficients and constant can be negative, and all values are interpreted modulo $2^k$.

The query provides a target value, as well as lower-bit constraints $[r_i, a_i]$ for each variable:

```text
x_i mod 2^r_i = a_i
0 <= r_i <= k
0 <= a_i < 2^r_i
```

When $r_i=0$, $a_i$ can only be 0, indicating no locked position; when $r_i=k$, the variable is completely determined. The number of locked positions for each variable can differ. Find the number of distinct complete vectors that satisfy all lower-bit constraints and $F(x)=\text{target} \pmod{2^k}$.

The count is an **exact non-negative integer, not taken modulo**, and may far exceed 64 bits. Each complete vector is counted only once.

## 2. Order of Canonical Solutions

Construct a 0/1 sequence of length $d \times k$ for the vector $x$, in the order of "lower bits first, and within the same bit, smaller variable index first":

```text
bit0(x_0), bit0(x_1), ..., bit0(x_(d-1)),
bit1(x_0), bit1(x_1), ..., bit1(x_(d-1)),
...
bit(k-1)(x_0), ..., bit(k-1)(x_(d-1))
```

bit0 is the least significant bit. The canonical solution is the lexicographically smallest among all vectors satisfying the query, according to the sequence above with 0 < 1. Locked bits still appear in the sequence, but all candidates are identical on these bits.

This definition does not use the usual lexicographical order for integer vectors, nor does it compare all bits of x_0 before comparing x_1. The bit order is precisely defined by the loop order above.

## 3. Protocol, Environment, and Constraints

UTF-8 NDJSON, one valid JSON command per line; reply with one line and flush immediately after reading each command, without waiting for EOF. stdout contains only responses, with LF line endings, stderr is empty, and exit with code 0 on EOF. Blank input lines may be ignored.

Field order and whitespace are unrestricted; the response field set, exact types, values, and array order must match. Integers cannot be replaced by floats, strings, or booleans; duplicate JSON fields are not accepted.

- The benchmark environment is Windows / CPython 3.14.2. Write the solution in `veil.py`, using only the Python standard library.
- 1 <= d <= 16, 1 <= k <= 40, fixed per process.
- Initial coefficients and the value for quad/linear/constant updates are integers in the range -2^63..2^63-1; negative numbers and different representations differing by multiples of 2^k are allowed.
- Each process handles at most 5000 commands, of which at most 64 are solve commands, and at most 8 of those have witness=true (regardless of feasibility).
- Each process has a 60-second time limit and a peak working set of 512 MiB; each online response must be delivered within 5 seconds. Timing includes startup, computation, and I/O.

Except for this file and normal standard library imports, do not read other files, create persistent files, connect to the network, spawn subprocesses, use ctypes, or call external EXEs/DLLs. General caching is allowed.

## 4. init

The first and only first command:

```json
{"op":"init","variables":2,"bits":3,
 "q":[[1,1],[0,1]],"linear":[0,0],"constant":0}
```

variables are d, bits are k; q is a d×d upper triangular table, linear has length d. The lower triangular elements are 0. Initialize and clear the snapshot. Responds with `{"ok":true}`.

In this example, F(x)=x_0^2+x_0*x_1+x_1^2 (mod 8).

## 5. Modification and Snapshots

The following commands all respond with `{"ok":true}`:

```json
{"op":"quad","i":0,"j":1,"value":-3}
{"op":"linear","i":1,"value":7}
{"op":"constant","value":-1}
{"op":"save","slot":31}
{"op":"load","slot":31}
```

- quad: Set `q[i][j]` to `value`, ensuring `0 <= i <= j < d`. If `i == j`, modify the squared term; if `i < j`, modify a cross term.
- linear: Set `linear[i]` to `value`.
- constant: Modify the constant term.
- save: Copy and save all `q`, `linear`, and `constant` values, overwriting the old snapshot in the slot.
- load: Restore the snapshot. The slot ranges from 0 to 31 and must have been saved previously. Subsequent modifications, operations on other slots, or further loads do not alter the saved snapshot.

Queries and caching do not modify the polynomial or the snapshot. `d` and `k` remain unchanged. Coefficients are used in calculations modulo $2^k$; updates differing by multiples of $2^k$ have the same mathematical semantics.

## 6. solve

```json
{"op":"solve","target":1,"locks":[[0,0],[2,1]],"witness":true}
```

The target is an integer in the range $0 \dots 2^k-1$. The `locks` array has a length of exactly $d$, and the meaning of each item $[r_i, a_i]$ is described in Section 1; `witness` is a JSON boolean indicating whether a canonical solution is requested.

The response fields are exactly:

```text
{"possible":P,"count":N,"witness":null or {"values":[...],"sha256":H}}
```

- `possible` is a JSON boolean, equivalent to an exact `count > 0`.
- `count` is the exact number of complete solution vectors, a JSON integer; it is 0 if infeasible.
- When infeasible, `witness` is `null`.
- When feasible and `witness=false` is requested, `witness` is still returned as `null`; this does not indicate infeasibility.
- When feasible and `witness=true` is requested, the `values` and hash of the canonical solution from Section 2 are returned. The `values` array has length `d`, ordered by variable index, with each item being an integer in the range `0..2^k-1`. This is not a bit sequence, nor is it a transformed coordinate.

Even if there are many locked positions, counting must be based on **distinct original complete vectors**; different parameter representations of the same vector must not be counted multiple times.

## 7. Witness Hash

Compute the SHA256 hash of the following byte string, outputting 64 lowercase hexadecimal characters:

```text
b"DYAD1"                             # 5 ASCII bytes, no NUL or newline
+ bytes([d,k])                       # one byte each: variable count, then bit width
+ concat(x_i.to_bytes((k+7)//8,"little") for i=0..d-1)
```

Each variable uses the same fixed width of ceil(k/8) bytes, unsigned little-endian; when not a whole number of bytes, the unused high bits of the most significant byte are 0. Polynomials, lock information, count, delimiters, or decimal strings are not encoded.

## 8. Semantic Examples

1. d=1, k=4, F(x)=x^2, target=9, unlocked: solutions are 3, 5, 11, 13, count=4. Comparing from the least significant bit, the canonical solution is 5.
2. d=2, k=2, F=x_0+2*x_1, target=2, unlocked: count=4, canonical solution [2,0]. When comparing bit planes, bit 0 of x_1 comes before bit 1 of x_0.
3. d=2, k=3, F=x_0*x_1, target=0, unlocked: count=20, canonical solution [0,0].
4. d=2, k=3, F=x_0^2+x_0*x_1+x_1^2: target=2 has no solutions; target=1 has 12 solutions; target=0 has 4 solutions.
5. d=1, k=4, F=x^2+x: target=2 has 2 solutions, target=3 has no solutions.
6. For the zero polynomial with target=0, count=2^(sum(k-r_i)), and the canonical solution consists of the given a_i values, with all other bits set to 0.
