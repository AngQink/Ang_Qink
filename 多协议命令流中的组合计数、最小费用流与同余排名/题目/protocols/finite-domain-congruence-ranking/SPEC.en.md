# 有限整数域上线性同余组的计数与排名 / Counting and Ranking Linear Congruence Solutions over Finite Integer Domains

This page defines the subprotocol. See the [combined specification](../../README.md) for its entry point, command prefixes, limits, and tests.

Maintain linear congruence constraints with multiple moduli. Count solutions exactly and compute lexicographic ranks and unrankings.

## 1. Mathematical Objects

A fixed integer $M$. Maintain $n$ variables, each with its own domain:

```text
0 <= x[i] < domains[i]
```

Each `domains[i]` divides `M`. Maintain at most 32 linear congruence rows. Each row has a unique numeric `id`, a fixed modulus `m`, a coefficient `a`, a right-hand side `rhs`, and an enabled status. `m` divides `M` and can be 1. An enabled row requires:

```text
sum(a[i] * x[i]) == rhs (mod m)
```

Coefficients and right-hand sides can both be negative. For all rows, including disabled and updated rows, the input guarantees that **m divides a[i] × domains[i]**. Therefore, adding a variable's value by its own period preserves each constraint. Domains are not necessarily prime powers, and row moduli may differ from one another.

## 2. Execution and Constraints

The benchmark environment is Windows / CPython 3.14.2. Write the solution in `prism.py`, using only the Python standard library. The program reads commands from standard input and writes responses to standard output. Except for importing standard library modules, the program does not read or write files, does not connect to the network, does not spawn subprocesses, and does not call external native code. General caching is allowed.

- 1 ≤ n ≤ 32, 0 ≤ number of rows ≤ 32.
- 2 ≤ M ≤ 2^63−1. M is provided via complete prime factorization `mod_factors`, where each entry is `[p,e]`, p is a prime, strictly increasing, and e is a positive integer.
- 1 ≤ domains[i] ≤ M, 1 ≤ m ≤ M, id is an integer in 0..2^32−1.
- a[i] and rhs are integers in the range −2^63..2^63−1. Counting and intermediate calculations use exact integers, which may far exceed 64 bits.
- Each process handles at most 5000 commands, of which at most 64 are `query` commands. Each `query` involves at most 12 `at` operations and 12 `probes`.
- A new process runs for each scenario. Each process has a 60-second time limit and a peak working set of 512 MiB. In online scenarios, each response is limited to 5 seconds.
- UTF-8 NDJSON, with one valid JSON object per line. Respond immediately and flush after reading each line; do not wait for EOF. stdout contains only responses, with LF line endings, stderr is empty, and exit code is 0 on EOF. Blank input lines may be ignored.
- Field order and whitespace within objects are unrestricted. The set of fields, types, values, and array order must match. Integers must not be replaced by booleans, floats, or strings. Duplicate JSON fields are rejected.

## 3. Initialization, Update, and Snapshot

The first and only first command is:

```json
{"op":"init","mod_factors":[[2,2],[3,1]],"domains":[6,4],"rows":[{"id":7,"mod":6,"a":[1,3],"rhs":2,"enabled":true}]}
```

n is equal to the length of domains. All a have n items. init fixes M, the domains of each variable, the row id and row modulus, and clears the snapshot.

```json
{"op":"row","id":7,"a":[-5,3],"rhs":8}
{"op":"rhs","id":7,"rhs":-4}
{"op":"enable","id":7,"value":false}
{"op":"save","slot":31}
{"op":"load","slot":31}
```

- `row` atomically replaces all coefficients and the RHS of that row, preserving the enabled status.
- `rhs` replaces only the right-hand side of that row. `enable` replaces only the enabled status. Disabled rows can be updated.
- `save` saves the coefficients, RHS, and enabled status of all rows, overwriting the existing slot. `load` restores the specified saved value. Slot numbers range from 0 to 31; `load` guarantees that the slot has been saved. Subsequent updates, operations on other slots, or another `load` will not alter the stored snapshot.
- `init`, `row`, `rhs`, `enable`, `save`, and `load` all return exactly `{"ok":true}`.

## 4. Queries

```json
{"op":"query","prefix":[2],"at":[0,1,2,0],"probes":[[1,3],[2,1],[5,0],[2,2]]}
```

First, take all **complete vectors** that satisfy the currently enabled rows and whose prefix is exactly `prefix`. The prefix length ranges from 0 to n, with each value within the domain at that position. An empty prefix imposes no restriction. Sort the resulting vectors in lexicographical ascending order by **variable order** and then by **integer magnitude**.

- `count` is the exact size of this solution set.
- `at` corresponds to the order of the requested `at` values. Each item is a zero-based index corresponding to a complete vector. Out-of-bounds indices are `null`. Requested indices are integers in the range 0..2^2048−1, which may be repeated or unordered.
- `probes` corresponds to the order of the requested `probes`. Each input vector has length n, with all values within their respective domains, and **may or may not satisfy the prefix or equations**. `before` is the number of elements strictly less than the vector in the selected solution set. `member` indicates whether the vector is in the selected solution set. Equal elements are not counted in `before`.
- `at` and `probes` may be empty. If infeasible, `count` is 0, all `at` items are `null`, and all `probes` items are `{"before":0,"member":false}`. All fields must still be returned.
- The query does not modify any rows or snapshots.

Using the initial parameters above, the solution set for the empty prefix is sequentially [2,0], [2,2], [5,1], [5,3]. The query above should reply:

```json
{"count":2,"at":[[2,0],[2,2],null,[2,0]],"probes":[{"before":0,"member":false},{"before":1,"member":false},{"before":2,"member":false},{"before":1,"member":true}]}
```

The definition remains consistent even when the moduli share common factors, the constraint rows are linearly dependent, or certain variable domains have size 1. When there are no constraints and the prefix is empty, count equals the product of the sizes of all domains.
