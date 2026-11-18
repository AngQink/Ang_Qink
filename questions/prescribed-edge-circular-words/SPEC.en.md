# 固定有向边重数的环形词计数 / Counting Circular Words with Prescribed Directed Edge Multiplicities

Count valid circular words, rotation classes, and prefix completions for prescribed directed edge multiplicities. Queries can also inspect the canonical word.

## Local testing

Implement `euler.py` and run:

```sh
python -B -m unittest discover -s public_tests -v
```

The package contains 16 public test scenarios. See the [sample input](samples/demo.ndjson) and [expected output](samples/demo.expected.ndjson).

## 1. Edge inventory and circular words

Vertices, also called colors, are numbered from 0 through V-1. Let M be a V-by-V nonnegative integer matrix and let `N=sum(M[u][v])`. An indexed word is a tuple `x=(x[0],...,x[N-1])`. It is valid when exactly M[u][v] positions satisfy:

```text
x[i] = u and x[(i+1) mod N] = v
```

Include the edge from the last position back to the first. Edges are directed, and loops are allowed. Parallel copies of an edge are indistinguishable. Distinct vertex sequences, without assignments of edge IDs, are distinct words.

Each vertex has equal in-degree and out-degree. Connectivity is not guaranteed, and isolated vertices are allowed. Queries have `1<=N<=200000`. A word of length 1 uses a loop.

## 2. Rotations, exact periods, and the canonical word

`R_k(x)[i]=x[(i+k) mod N]`. A necklace is a rotation class. Reflections and recolorings do not enter this equivalence.

The exact period is the smallest positive p such that `R_p(x)=x`. If the word repeats a smaller block r times, `p=N/r` and r divides every matrix entry.

Let G be the gcd of all entries, including zeros, equivalently the gcd of nonzero entries. For a query `G>=1`. Include a row in `periods` exactly for each `p=N/r` where r is a positive divisor of G. List the rows in strictly increasing p, including zero counts.

The canonical word is the lexicographically least valid indexed word, comparing integer vertex IDs. All starting positions participate.

## 3. Environment, protocol, and limits

Use UTF-8 NDJSON, with one valid command per line. Reply and flush immediately after each command. Standard output contains only LF-terminated protocol responses. Leave stderr empty and exit with status 0 at EOF. Blank input lines may be ignored.

Response fields, exact types, values, and array orders must match. Field order and whitespace can vary. No duplicate JSON fields. Integers cannot be represented as floats, strings, or Booleans.

- The benchmark environment is Windows with CPython 3.14.2. Implement `euler.py` with the standard library.
- `1<=V<=16`. Entries are nonnegative integers. After initialization or an update, `0<=N<=200000`. A `count` query has `N>=1`.
- At most 5000 commands per process and at most 64 `count` commands.
- `rotations` and `at` each contain at most 32 integers from 0 through 2^2048-1. Values may repeat, be out of order, or be out of range for a particular index query.
- `prefixes` contains at most 16 arrays of valid vertex IDs, each with length 0 through 32. A prefix may repeat, be empty, exceed N, or have no valid completion.
- At query time G has at most 64 positive divisors. Its complete prime factorization is supplied.
- The process budget is 60 seconds and 512 MiB peak working set. Each interactive response has a five-second bound (5 seconds). Timing includes startup, computation, and I/O.

Apart from the program and normal standard-library imports, do not read files, write persistent files, use the network, spawn subprocesses, or load external code through ctypes or an EXE/DLL. General-purpose caching is allowed.

## 4. init

`init` occurs exactly once as the first command.

```json
{"op":"init","vertices":2,"mod_factors":[[2,3],[3,2]],"edges":[[1,1],[1,1]]}
```

`vertices` is V and `edges` is M in vertex order. The sum of each row equals its corresponding column sum. The initial N may be 0.

`mod_factors` is the full prime factorization of the counting modulus m. Each pair `[p,a]` gives a prime p and a positive exponent a. Primes are strictly increasing and `m=product(p**a)`. The input guarantees:

```text
2 <= m <= 2^63-1
each p**a <= 65536
```

There is no need to factor or validate the input. The modulus may share factors with N, exact periods, and factorial terms. V and m remain constant. Initialization clears all snapshots and returns `{"ok":true}`.

## 5. Updates and snapshots

### cycle

```json
{"op":"cycle","vertices":[0,1,0],"delta":2}
```

`vertices` has length 1 through 32, and entries may repeat. Add `delta` for each step of the closed walk, including the last-to-first edge:

```text
M[vertices[i]][vertices[(i+1) mod L]] += delta
```

`delta` is an integer from -200000 through 200000, possibly 0. Count each occurrence of a repeated edge. A length-1 walk changes one loop. The update preserves degree balance, and all entries remain nonnegative with `N<=200000`. Updates may leave N at 0 if no query follows.

For example, `[0,1,0]` adjusts `0->1`, `1->0`, and `0->0` once each. `[0,0]` adjusts `0->0` twice. Reply `{"ok":true}`.

### save / load

```json
{"op":"save","slot":31}
{"op":"load","slot":31}
```

Slots range from 0 through 31. Save a copy of the whole matrix, overwriting the prior value. Load restores a previously saved value. Updates, other slots, and later loads leave saved snapshots intact. Queries do not change state. Both commands return `{"ok":true}`.

## 6. count

```json
{"op":"count","gcd_factors":[],"rotations":[0,1,4],
 "prefixes":[[],[0],[0,0],[0,0,1,1]],"at":[0,1,2,3,4]}
```

`gcd_factors` is the complete prime factorization of G, in the format of `mod_factors`. G=1 uses an empty list. G is distinct from the counting modulus m.

The response has exactly these fields:

```text
{
 "possible":P,
 "length":N,
 "words":W,
 "necklaces":K,
 "periods":[{"period":p,"words":W_p,"necklaces":K_p},...],
 "fixed_rotations":[...],
 "prefix_counts":[...],
 "witness":null or {"sha256":H,"at":[...]}
}
```

- `possible` is a JSON Boolean indicating whether a valid word exists. A count congruent to 0 modulo m does not imply infeasibility.
- `length` is the exact integer N.
- `words` and `necklaces` count all indexed words and rotation classes, respectively, modulo m.
- `periods` lists all candidate periods from Section 2. Each row counts only words and classes of exact period p, modulo m.
- `fixed_rotations` matches `rotations` in length and order. Its element for k counts valid words fixed by `R_k`, modulo m.
- `prefix_counts` matches `prefixes`. Each element counts length-N indexed words whose initial entries exactly match that prefix, modulo m. The empty prefix has count `words` and a prefix longer than N has count 0. Consume edges already used by the prefix, and count only completions closing back to the first vertex. Parallel copies remain indistinguishable.
- If infeasible, return every field and period row with all counts 0 and `witness=null`.
- Otherwise `witness` contains the canonical word's hash and answers to the index queries. Its `at` array follows the request order. Index 0 is the first vertex, and indices at least N yield null.

Define all counts over nonnegative integers before applying the modulus. Return integers in 0 through m-1. Integer division must remain valid when the denominator is a nonunit modulo m.

## 7. Witness hash

Hash the following bytes with SHA-256 and render the digest as 64 lowercase hexadecimal characters.

```text
b"EULER1"                      # 6 ASCII bytes, no NUL or newline
+ N.to_bytes(8, "little")      # unsigned little-endian
+ bytes(the N vertex IDs in the canonical word)   # one byte per ID, from 0 to 15
```

Do not encode edge copies, the modulus, snapshot data, separators, or decimal strings. Do not append the first vertex as a closing position.

## 8. Examples

1. `M=[[1,1],[1,1]]` gives 0011, 0110, 1100, and 1001. There are 4 words and 1 necklace, with only period 4 listed. The canonical word is 0011. Prefix counts for `[]`, `[0]`, `[0,0]`, and `[0,0,1,1]` are 4, 2, 1, and 1.
2. `M=[[0,2],[2,0]]` gives 0101 and 1010, both of exact period 2. With m=2, `words=0`, `possible=true`, and `necklaces=1`.
3. `M=[[2,0],[0,2]]` balances both vertices, but the two disconnected loop inventories cannot form one word. `possible=false`.
4. One copy each of `0->1`, `1->0`, `1->2`, and `2->1` gives canonical word 0121. Prefix `[0,1,0]` has no completion despite using valid edges locally.
