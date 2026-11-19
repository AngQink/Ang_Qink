# 带权环形词的旋转与反射轨道计数 / Rotation and Reflection Orbit Counts for Weighted Circular Words

Maintain color adjacency and weights, and count the number of valid cyclic words, rotation and color-swapping mirror equivalence classes, as well as exact periods and fixed words.

## Local Self-Test

Implement `mirror.py` in the current directory. The code provided with the problem is used for handling input and output, while the solving logic is left for implementation.

```sh
python -B -m unittest discover -s public_tests -v
```

This problem includes 16 public test scenarios. You can also refer to the [sample input](samples/demo.ndjson) and [expected output](samples/demo.expected.ndjson).

## 1. Objects

Color indices range from `0` to `C-1`. Given an undirected adjacency matrix `E` (self-loops allowed), color weights `w`, and a fixed involution `tau` on the colors.

- `tau[tau[a]] = a`; fixed points are allowed, as are swaps of two colors.
- `E[a][b] = E[b][a] = E[tau[a]][tau[b]]`.
- `w[a] = w[tau[a]]`.

A positionally labeled word of length `n >= 1` is an ordered tuple `x = (x[0],...,x[n-1])`. A valid word must satisfy both of the following conditions:

1. For all `i`, `E[x[i]][x[(i+1) mod n]] = true`, including adjacency between the last and first elements.
2. `sum(w[x[i]]) mod Q = residue`. This sums over the entire word of length `n`, not over a single periodic block.

Color choices at different positions constitute distinct positionally labeled words; colors of the same type are indistinguishable. For length 1, the color must have a self-loop; for length 2, the checks in both directions correspond to the same boolean adjacency condition and do not generate additional edge selection schemes.

## 2. Two Equivalence Relations and Exact Period

All index calculations are performed modulo `n`. Define:

```text
R_k(x)[i] = x[(i+k) mod n]
F_k(x)[i] = tau[x[(k-i) mod n]]
```

`F_k` replaces colors one by one while reversing positions; it is not a simple reversal. The above invariants guarantee that these transformations still map valid words to valid words.

- **necklace**: Only rotations are allowed, meaning two words are equal, or one is some `R_k` of the other.
- **bracelet**: Rotations and the above color-swapping mirrors are allowed, meaning one is some `R_k` or `F_k` of the other.
- The **exact period** of a word is the smallest positive integer `p` such that `R_p(x)=x`; `p` must divide `n`. Exact period considers only rotations and does not treat mirror symmetry as a period.

Lengths 1 and 2 also use the original definition, without changing the convention; different transformations may act identically on all words, but the equivalence class definitions remain unchanged.

## 3. Protocol and Resources

Input and output are UTF-8 NDJSON, with one object per line. Input is guaranteed to be valid. Each command immediately replies with one line and flushes; it cannot wait for EOF. stdout contains only protocol responses, using LF; stderr is empty; exit with code 0 on EOF. Blank input lines may be ignored.

The order of response fields and spacing are unrestricted; the set of fields, types, values, and array order must be exact. Integers cannot be replaced by floats, booleans, or strings. Duplicate JSON fields are rejected.

- The baseline environment is Windows / CPython 3.14.2. Write the solution in `mirror.py`, using only the Python standard library.
- `1 <= C <= 8`, `1 <= Q <= 8`, `0 <= w[a] < Q`.
- The counting modulus `2 <= mod <= 2^63-1`, **not guaranteed to be prime, nor guaranteed to be coprime with `n`**.
- For each query `1 <= n <= 2^63-1`, the number of its positive divisors is at most 32.
- Each process handles at most 5000 commands, of which at most 32 are `orbit` queries.
- Each process has a 60-second time limit and a peak working set of 512 MiB; each online response waits at most 5 seconds. Process timing includes startup and all computation/input-output.
- For each query, `rotations` and `mirrors` contain at most 32 items each. `k` is a JSON integer in `0..2^2048-1`; it may be repeated, unordered, or exceed `n`.

Except for standard library imports and this file, do not read other files, create persistent files, connect to the network, spawn subprocesses, use ctypes, or call external EXEs/DLLs. General caching is allowed.

## 4. init

The first and only first command:

```json
{"op":"init","colors":2,"inventory_mod":3,"mod":12,
 "mirror":[1,0],"weights":[1,1],
 "edges":[[true,true],[true,true]]}
```

`inventory_mod` is Q, `mod` is the counting modulus, and `mirror` is tau; all the aforementioned invariants hold. Response: `{"ok":true}`. Initialize by clearing all snapshots.

C, Q, mod, and tau are fixed within this process. Only adjacency and weights can be modified.

## 5. Updates and Snapshots

All the following commands respond with `{"ok":true}`.

### edge

```json
{"op":"edge","u":0,"v":1,"value":false}
```

Set the following positions **simultaneously** to value, leaving other positions unchanged:

```text
(u,v), (v,u), (tau[u],tau[v]), (tau[v],tau[u])
```

The duplicate position is set only once. The value is a JSON boolean. u and v are valid color numbers. Self-loops are also handled according to the same rule.

### weight

```json
{"op":"weight","color":0,"value":2}
```

Also set `w[color] = w[tau[color]] = value`; `0 <= value < Q`. The remaining weights remain unchanged.

### save / load

```json
{"op":"save","slot":31}
{"op":"load","slot":31}
```

The slot ranges from 0 to 31. `save` copies and saves the **entire adjacency matrix and all weights**, overwriting the old snapshot in that slot. `load` restores them; it is guaranteed that the slot has been saved. Subsequent updates, other slots, and subsequent `load` operations do not alter the stored snapshot. Queries do not modify the state.

## 6. orbit

```json
{"op":"orbit","factors":[[2,1],[3,1]],"residue":0,
 "rotations":[0,1,6],"mirrors":[0,1,7]}
```

`factors` provides the complete prime factorization of $n$: each item `[p,e]` has $p$ as the actual prime, strictly increasing, and $e$ as a positive integer, with $n = \prod (p^e)$. When $n=1$, `factors` is an empty array. No integer factorization or input validation is required. `residue` is in the range 0..Q-1.

The response fields are exactly:

```text
{
  "length": n,
  "words": W,
  "necklaces": N,
  "bracelets": B,
  "periods": [
    {"period": d, "words": W_d, "necklaces": N_d, "bracelets": B_d},
    ...
  ],
  "fixed": {"rotations": [...], "mirrors": [...]}
}
```

- W: The number of valid position-labeled words, modulo mod.
- N: The number of equivalence classes of valid words under rotation, modulo mod.
- B: The number of equivalence classes of valid words under rotation and color-swapping reflection, modulo mod.
- periods: All positive divisors of n, strictly increasing. Rows are retained even if the count for that row is zero.
- Each row counts only words or equivalence classes with an exact period of exactly d among valid words of full length n. It does not count words whose exact period divides d, nor does it initiate a new query with length d and the original residue.
- fixed.rotations: Has the same length and order as the requested rotations. The j-th item is the number of valid position-labeled words satisfying `R_k(x)=x`, modulo mod, where k is the j-th item in the request.
- fixed.mirrors: Similarly, counts the number of valid position-labeled words satisfying `F_k(x)=x`, modulo mod.
- length and period are exact JSON integers; all counts are integers in the range 0..mod-1. If there are no valid words, all counts are zero, but the complete structure is still returned.

**Count equivalence classes in the sense of non-negative integers first, then take the modulo.** A result of zero after taking the modulo does not imply that no objects exist; one must not force division in the modular ring by altering integer counts that should be divisible.

## 7. Small Examples

1. C=2, Q=1, fully connected, tau=[0,1], n=3, mod=100: 8 words, 4 necklaces, 4 bracelets; for period 1, there are 2 words/2 classes/2 classes, and for period 3, there are 6 words/2 classes/2 classes.
2. Same as above but tau=[1,0]: 8 words, 4 necklaces, 2 bracelets. Each F_k has no fixed words; for period 1, there are 2 words/2 classes/1 class, and for period 3, there are 6 words/2 classes/1 class.
3. C=1, Q=4, w=[1], with self-loops, n=6: Only residue=2 has 1 valid word. Its exact period is 1, but the weight residue of the length-1 monochromatic word is 1; the row for d=1 in periods still belongs to the original query of length 6.
4. C=1 and no self-loops: There are no valid words of any positive length.
