# 二次相位函数的约束求和 / Constrained Quadratic Phase Sums

Implement a program for online command processing that maintains a quadratic phase function on binary variables and computes exact complex summation results under given linear constraints. The program must support function updates, snapshots, point values, and overlap queries between snapshots.

The entry point is `phase.py`. The test environment is Windows with CPython 3.14.2, using only the Python standard library.

## 1. Mathematical Objects

Fix $n$ binary variables $x[0], \dots, x[n-1]$, where each term is 0 or 1. The current function is:

`q(x) = c + sum(l[u]*x[u]) + 2*sum(x[u]*x[v] : {u,v} is an edge)  (mod 4)`.

$c$ and each $l[u]$ are in the range 0..3, and the edges form an undirected graph without self-loops or multi-edges.
The function value $q(x)$ is represented by 0..3. Let $i$ be the imaginary unit, with $i^0=1$, $i^1=i$, $i^2=-1$, $i^3=-i$.

The query sums over every distinct valid $x$ exactly once, under given binary linear conditions:

`Z = sum(i^q(x) : A*x = b over GF(2))`.

$Z$ is the **sum of complex numbers**. Contributions from different $x$ may cancel out; the existence of valid $x$ does not imply that $Z$ is non-zero.
There is no probabilistic sampling, floating-point error tolerance, absolute value operation, or normalization factor.

## 2. Protocol and Constraints

Input and output are UTF-8 NDJSON, with one JSON object per line. All inputs are guaranteed to be valid.
For every command read, a response must be immediately output and flushed; waiting for EOF is not allowed. stdout writes only responses, ending with LF; stderr is empty, and the exit code on EOF is 0.
The order of fields and separating spaces are unrestricted. The set of fields, values, and types must be accurate. Integers do not accept floats, strings, or boolean substitutes.

- The first and only the first command is `init`; `0 <= n <= 512`, fixed per process.
- The initial `constant` and entries of `linear` are integers from 0 to 3; `edges` is a valid simple graph, with each edge appearing exactly once, in arbitrary endpoint order.
- `delta` is a signed 64-bit integer; updates are performed modulo 4, with negative values handled correctly via modulo.
- `u`, `v`, `dst`, `src` are valid variable indices. The two indices for `cz` and `xor` are guaranteed to be distinct; `swap` allows identical indices.
- Snapshot slots range from 0 to 63; snapshots referenced by `load` and `overlap` are guaranteed to have been saved.
- Each `a` is an array of at most 128 hexadecimal strings, each representing a non-negative integer from 0 to $2^n-1$; leading zeros and mixed case are allowed, without sign or `0x` prefix.
- The **$u$-th bit** of each `mask` corresponds to variable $x[u]$, and the row condition states that the XOR of all variables specified by the mask equals the corresponding term in `b`.
- `b` has the same length as `a`, with terms being integers 0 or 1; zero masks and duplicate/redundant conditions are valid.
- Each process has at most 20,000 commands; the total number of `ask` and `overlap` commands combined is at most 256.
- Each complete scenario allows 30 seconds and a peak working set of 512 MiB; for online interaction, each command waits at most 5 seconds.
- Execution time includes interpreter startup, JSON input/output, and computation, excluding the time required to prepare test inputs.

Implementation must be concentrated in `phase.py`. Except for standard library imports and this file, do not read other files, create persistent files, connect to the network, spawn subprocesses, use ctypes, or load DLLs.
General caching is allowed. The program must correctly handle all inputs satisfying the constraints; public tests are for self-testing only.

## 3. Initialization

```json
{"op":"init","n":2,"linear":[0,0],"edges":[[0,1]],"constant":0}
```

Establish q, clear snapshots. Responds with `{"ok":true}`.

## 4. Update the current function

The following commands respond with `{"ok":true}`.

| Command | Meaning |
|---|---|
| `{"op":"phase","u":u,"delta":d}` | q(x) increases by d*x[u], modulo 4 |
| `{"op":"global","delta":d}` | q(x) increases by a constant d, modulo 4; global phase must be preserved |
| `{"op":"cz","u":u,"v":v}` | q(x) increases by 2*x[u]*x[v], i.e., toggles this edge |
| `{"op":"flip","u":u}` | New function q'(x)=q(y), where y[u]=x[u] XOR 1, and y[j]=x[j] for all other j |
| `{"op":"xor","dst":u,"src":v}` | New function q'(x)=q(y), where y[u]=x[u] XOR x[v], and y[j]=x[j] for all other j |
| `{"op":"swap","u":u,"v":v}` | Swaps these two variables in the input of q |

flip/xor/swap are **input substitutions for the current function**; they do not change the coordinate numbering used in subsequent query conditions, nor do they change n.
The functions after substitution still have the form described in Section 1. All expressions read the function prior to the execution of the command.
Do not misunderstand xor as swapping variables, increasing function values, modifying a fixed input sample, or rewriting the constraint rows for subsequent inputs.

## 5. Snapshots

```json
{"op":"save","slot":3}
{"op":"load","slot":3}
```

save saves the current function's value, overwriting the previous snapshot in that slot; load replaces the current function with the value from the specified snapshot.
Subsequent updates do not alter existing snapshots. Updates after a load also do not alter the snapshot. Both save and load respond with `{"ok":true}`.

## 6. ask: Restricted phase sum

```json
{"op":"ask","a":["3"],"b":[1]}
```

First, find the set $S$ that satisfies the linear conditions.

If $S$ is empty, output only `{"possible":false}`, with no other fields.

If $S$ is non-empty, the response is exactly:

```text
{"possible":true,"free":r,"first":s,"amplitude":T}
```

- r is the affine dimension of S, so S has exactly $2^r$ distinct inputs.
- s is the lexicographically smallest length-n binary string in S. **The 0th element of the string is x[0]**, followed by x[1], and so on; when comparing, '0' is less than '1', meaning the mask is not minimized as an integer.
- T encodes Z. If Z=0, T is exactly `{"zero":true}`.
- If Z is non-zero, T is exactly `{"zero":false,"power":k,"phase":p}`, which means:

`Z = 2^(k/2) * exp(i*pi*p/4)`.

k is an integer from 0 to 2*r, and p is an integer from 0 to 7. **power is twice the binary magnitude exponent**, allowing for odd values; phase is measured in units of one-eighth of a full circle.
All non-zero sums in this problem have this form, and the encoding is unique. You must not return only |Z|, the real part of Z, the probability, or internal implementation counters.

The constraints guarantee a solution, and even when Z=0, you must still return possible=true, free, first, and zero=true.
When n=0 and there are no contradictory conditions, S contains only the empty input: free=0, first="", and Z=i^c.

## 7. overlap: Unnormalized overlap between snapshots

```json
{"op":"overlap","left":0,"right":1,"a":[],"b":[]}
```

Query only the snapshot, without modifying the current function or snapshot. The response format is the same as `ask`, but the summation term is:

`Z = sum(i^(q_left(x)-q_right(x)) : A*x=b over GF(2))`.

The direction of subtraction must be correct. Swapping left and right should conjugate the non-zero result.
When the same snapshot overlaps with itself, each term is 1; if the condition is feasible, Z=2^r, corresponding to power=2*r, phase=0.
There are no normalization factors such as 2^(-n); the value of the current function does not participate in this query.

## 8. value: Point Value

```json
{"op":"value","bits":"01"}
```

bits exactly $n$ 0/1 characters, the $u$-th item is $x[u]$. The response `{"phase":v}` contains $v$, which is the current value of $q(x)$ in the range 0..3.
Here, phase represents the exponent of $i$, in units of quarter turns; it differs from the phase in amplitude, which is in units of eighth turns.

## 9. Examples

1. $n=1$, $q(x)=x$, unconditional: $Z=1+i$, free=1, first="0", amplitude is `{"zero":false,"power":1,"phase":1}`.
2. $n=1$, $q(x)=2*x$, unconditional: two inputs contribute 1 and -1, possible=true, free=1, first="0", amplitude is `{"zero":true}`.
3. $n=2$, $q(x)=2*x[0]*x[1]$, unconditional: four contributions are 1, 1, 1, -1, $Z=2$, corresponding to power=2, phase=0, rather than power=4.
4. $n=2$, conditional mask="3", rhs=1 means $x[0]$ XOR $x[1]=1$, the lexicographically smallest string is "01", not "10".

## 10. Complete Example

Input:

```json
{"op":"init","n":1,"linear":[1],"edges":[],"constant":0}
{"op":"ask","a":[],"b":[]}
{"op":"save","slot":0}
{"op":"phase","u":0,"delta":1}
{"op":"ask","a":[],"b":[]}
{"op":"overlap","left":0,"right":0,"a":[],"b":[]}
{"op":"ask","a":["0"],"b":[1]}
```

Output:

```json
{"ok":true}
{"possible":true,"free":1,"first":"0","amplitude":{"zero":false,"power":1,"phase":1}}
{"ok":true}
{"ok":true}
{"possible":true,"free":1,"first":"0","amplitude":{"zero":true}}
{"possible":true,"free":1,"first":"0","amplitude":{"zero":false,"power":2,"phase":0}}
{"possible":false}
```

## 11. Public Testing

You only need to complete `phase.py`; the program reads commands line by line from standard input and writes responses line by line to standard output. Each command must be responded to immediately upon receipt, with the output buffer flushed.

Run the following command in this problem's directory.

```text
python -B -m unittest discover -s public_tests -v
```

Attached are 13 public tests covering basic behaviors such as examples, cancellation, global phase, variable substitution, snapshots, lexicographic order of constraint solutions, and online responses. The program must still satisfy all data ranges and resource constraints specified in the main text.
