# 动态森林的最大权独立集 / Maximum-Weight Independent Sets in Dynamic Forests

Implement a single file `forest.py`. Maintain an undirected forest with vertex weights, supporting online edge additions, edge deletions, and weight updates, and accurately answer queries for the maximum weight independent set of connected components, the number of optimal solutions, and the results after forcing the states of two vertices.

The algorithm and data structures are up to you. It must simultaneously satisfy semantics, online response capabilities, and resource constraints.

## 1. Runtime Environment

The test environment is Windows and CPython 3.14.2. The implementation must be concentrated in `forest.py`, using only the Python standard library. Except for normal imports of standard libraries and reading this program, no other files may be read, persistent files created, network connections established, or subprocesses launched.

Input and output are UTF-8 NDJSON, with one JSON object per line. `stdout` only outputs protocol responses, with line endings as LF. For each command read, a response must be immediately output and flushed; do not wait for EOF. Input may continue to be generated only after the previous response has been received. Exit normally on EOF with return code 0; `stderr` should be empty.

All inputs are guaranteed to be valid and satisfy the constraints below; error handling for invalid JSON, illegal operations, or out-of-bounds access is not required. The order of fields and spacing in output objects are unrestricted; the field set, types, and values must be accurate; integers must be output as JSON integers, and booleans as JSON booleans.

## 2. Mathematical Definitions

- Vertices are `0..n-1`. Each vertex $u$ has an integer weight $w[u]$.
- The graph is always an undirected forest with no self-loops and no multi-edges, and may be disconnected.
- An independent set is a subset of vertices $S$ such that no edge has both endpoints in $S$. The empty set is valid, with weight 0.
- The weight of a set is the sum of the weights of its vertices. There may be multiple maximum weight independent sets; **the number of solutions counts distinct vertex subsets**, not traversal orders or selection processes.
- All queries consider only the specified connected component; other components do not contribute to weights or solution counts.
- Weight sums use exact integers; floating-point approximations are not allowed, nor are weights taken modulo any number. Vertex weights are signed 64-bit integers (inclusive of endpoints), and the sum of answers may exceed 64 bits.
- The number of solutions is taken modulo $m$, which is given at initialization. $m$ can be composite. **ways=0 is merely the modular result of the count and does not imply infeasibility.** Feasibility is indicated by the explicit `possible` field.
- Queries do not alter the abstract graph, vertex weights, or the mathematical results of other queries.

## 3. Initialization

The first and only first command is:

```json
{"op":"init","weights":[w0,w1,...],"edges":[[u,v],...],"mod":m}
```

n equals the length of weights, ensuring `1 <= n <= 100000`; edges form a valid forest, each undirected edge appears only once, and the order of endpoints is arbitrary. m is an integer satisfying `2 <= m <= 2147483647`, and it is not guaranteed to be prime.

Response: `{"ok":true}`.

## 4. Modifications

The following operations uniformly respond with `{"ok":true}`:

| Command | Semantics and Guarantees |
|---|---|
| `{"op":"set","u":u,"w":w}` | Replace the weight of u with w; it is allowed to be the same as the original weight |
| `{"op":"link","u":u,"v":v}` | Add an undirected edge (u,v); it is guaranteed that u and v are in different connected components |
| `{"op":"cut","u":u,"v":v}` | Delete the undirected edge (u,v); it is guaranteed that this edge exists; the order of endpoints is arbitrary |

The set of vertices and m remain fixed within a single process. There is no implicit root, nor are there any unspecified reset operations.

## 5. Single-Vertex Conditional Query

Command: `{"op":"ask","u":u}`.

Let C be the connected component containing u. The response must be exactly:

```text
{"n":|C|,
 "best":{"weight":W,"ways":K},
 "out":{"weight":W0,"ways":K0},
 "in":{"weight":W1,"ways":K1}}
```

- best: The maximum weight independent set in C without additional constraints, along with the number of such sets modulo $m$.
- out: The optimal weight sum and the number of sets when vertex $u$ is forced to be excluded from the independent set.
- in: The optimal weight sum and the number of sets when vertex $u$ is forced to be included in the independent set.

These three problems are always feasible in a forest. The weight for `in` may be negative. If the optimal weights for `out` and `in` are identical, the `ways` for `best` should be the sum of the `ways` for both, modulo $m$, because these two classes of vertex subsets are distinct.

## 6. Dual Vertex Condition Query

Command: `{"op":"pair","u":u,"v":v,"su":s,"sv":t}`, where $s$ and $t$ are either 0 or 1. 0 indicates that the vertex is forced to be unselected, and 1 indicates that the vertex is forced to be selected.

1. If $u$ and $v$ are not connected, respond only with `{"connected":false}` without merging the two components for solving.
2. If they are connected but the conditions cannot be satisfied simultaneously, respond only with `{"connected":true,"possible":false}`.
3. Otherwise, respond with `{"connected":true,"possible":true,"weight":W,"ways":K}`.

$W$ and $K$ represent the optimal weight sum and the number of sets modulo $m$ for the **entire connected component** under the two forced conditions, not just for the path between $u$ and $v$. Branches outside the path must also be taken into account.

It is allowed that $u=v$: if $s=t$, this is equivalent to a single forced condition; if $s \neq t$, it is infeasible. It is also infeasible if two adjacent vertices are both forced to be selected. Even if $K=0$, a feasible answer must output `possible=true`.

## 7. Example

Three-point star: edges are $(0,1)$ and $(0,2)$, all weights are 0, and $m=4$. The independent sets are: the empty set, $\{0\}$, $\{1\}$, $\{2\}$, and $\{1,2\}$.

The response to `ask 0` is:

```json
{"n":3,"best":{"weight":0,"ways":1},"out":{"weight":0,"ways":0},"in":{"weight":0,"ways":1}}
```

`pair(0,0,0,0)` is feasible, response:

```json
{"connected":true,"possible":true,"weight":0,"ways":0}
```

Since there are 4 optimal sets that do not select 0, their count modulo 4 is 0. This zero cannot be interpreted as "non-existent."

Changing vertex 0 to have a weight of -7 allows it to be selected individually while remaining feasible, with an optimal weight of -7 and ways=1.

## 8. Scale and Resources

- Each independent process can execute at most 60,000 commands (including init); $n$ is at most 100,000, with an initial number of edges at most $n-1$.
- The new weight for each set falls within `[-2^63, 2^63-1]`.
- The peak working set limit for each process is **512 MiB**. Each scenario has a time limit of **60 seconds**, including interpreter startup, JSON input/output, and command processing.
- Online interactive checking waits for a response after each command, with a maximum wait time of 5 seconds; it is not allowed to read the entire future script and solve offline.
- The data includes long paths, high-degree vertices, randomly numbered trees, frequent switching of query vertices, non-unit and zero counts, frequent weight changes/edge cuts/reconnections, and combinations of these properties.

You may cache, share, or reorganize internal structures, but you must not let the query order affect the results, nor treat irreversible modular arithmetic as ordinary real-number division. Traversing the entire large component for each query or permanently retaining all solution counts as arbitrary-precision integers may fail to meet resource constraints; the implementation choice is up to you.

## Public Testing

After completing `forest.py` in this problem directory, run the following command.

```text
python -B -m unittest discover -s public_tests -v
```

Sample inputs and corresponding outputs are located in [samples](samples/).
