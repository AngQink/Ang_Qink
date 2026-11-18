# 最小费用有向根树的计数与排名 / Counting and Ranking Minimum-Cost Arborescences

Query the exact count of minimum-cost arborescences, rank and unrank them lexicographically, and count the optima containing a given edge.

## Local Self-Test

Implement `anchor.py` in the current directory. The code provided with the problem handles input and output; the solving logic is left for implementation.

```sh
python -B -m unittest discover -s public_tests -v
```

This problem includes 16 public test scenarios. You can also view the [sample input](samples/demo.ndjson) and [expected output](samples/demo.expected.ndjson).

## 1. Directed Rooted Tree

Maintain a directed multigraph. Vertices are numbered from 0 to n−1. Each edge has a unique numeric id, a fixed source u, a destination v, a mutable integer cost, and a mutable enabled status. Parallel edges and self-loops are allowed. Two edges with identical endpoints and costs are still distinct choices.

Each query specifies a root `root`. A valid rooted tree must satisfy:

- The root has no incoming edges, and every other vertex selects exactly one enabled incoming edge.
- Every vertex is reachable from the root by following the selected edges in their forward direction. Therefore, self-loops and cycles detached from the root cannot be selected.
- Every edge specified in the query's `pins` must be selected.

The cost of a tree is the sum of the costs of the selected edges. Negative costs are allowed. The optimal tree is the one with the minimum cost among all valid trees satisfying the current `pins`.

A tree vector lists the ids of the selected edges in **increasing order of their destination vertex numbers**, skipping the root. For example, if the root is 1 and n=4, the ids of edges with destinations 0, 2, and 3 are listed in that order. The optimal tree is sorted by the **lexicographical order** of the integer ids in the vector, with positions starting from 0. Different sets of selected edges correspond to different vectors.

## 2. Environment and Constraints

The benchmark environment is Windows / CPython 3.14.2. Write the solution in `anchor.py`, using only the Python standard library. The program reads commands from standard input and writes responses to standard output. Except for importing standard libraries, the program does not read or write files, does not connect to the network, does not spawn subprocesses, and does not call external native code. General-purpose caching is allowed.

- $1 \le n \le 18$, $0 \le \text{number of edges} \le 80$. id is an integer in $0..2^{32}-1$, **all edge ids are unique**. Endpoints are valid.
- cost is an integer in $-2^{63}..2^{63}-1$, and the total cost may exceed 64 bits; output using exact integers.
- Each process handles at most 5000 commands, of which at most 32 are queries. A single query has at most 12 pins, 4 at, 4 probes, and 12 uses.
- Each scenario starts a new process. Each process has a 60-second time limit and a peak working set of 512 MiB. In online scenarios, the reply to each command is limited to 5 seconds.
- UTF-8 NDJSON. One valid JSON object per line. Reply immediately and flush after reading each line. stdout contains only replies, with LF line endings, stderr is empty, and exit 0 on EOF. Blank input lines may be ignored.
- The order of object fields and JSON whitespace are unrestricted. The set of fields, types, values, and array order must match. Integers must not be represented as booleans, floats, or strings. Duplicate JSON fields are rejected.

## 3. Initialization, Updates, and Snapshots

The first and only first message is init. The enabled status is a boolean. The initial order of edges is arbitrary; the number of vertices, edge ids, and endpoints remain unchanged thereafter.

```json
{"op":"init","vertices":3,"edges":[{"id":9,"u":0,"v":1,"cost":5,"enabled":true},{"id":2,"u":0,"v":1,"cost":5,"enabled":true},{"id":3,"u":0,"v":2,"cost":2,"enabled":true},{"id":8,"u":1,"v":2,"cost":2,"enabled":true}]}
```

```json
{"op":"cost","id":9,"cost":-9}
{"op":"enable","id":2,"value":false}
{"op":"save","slot":31}
{"op":"load","slot":31}
```

- cost replaces the cost of this edge without changing its enabled status. enable replaces the enabled status without changing the cost. Both modification IDs exist. Disabled edges can also have their costs modified.
- save copies and saves the costs and enabled statuses of all edges, overwriting the old slot. load restores the state of that slot. Slot numbers range from 0 to 31; load guarantees that the slot has been saved. Subsequent modifications and further loads do not alter the saved snapshot.

These commands all return exactly {"ok":true}.

## 4. Query

```json
{"op":"query","root":0,"pins":[],"at":[0,2,4],"probes":[[2,4],[9,8],[7,7]],"uses":[2,3,99]}
```

- `root` is a valid vertex. The `id`s in `pins` exist and appear exactly once in this list, in any order. If disabled edges, self-loops, edges ending at the root, or multiple edges with the same endpoint are specified, a feasible tree cannot be formed. `pins` is valid only for this query.
- `at` corresponds to the `at` in the request in the same order. Each item is an integer in the range 0..2^2048−1, querying the **complete tree vector** at the corresponding position; out-of-bounds returns `null`. Indices may be unordered or duplicated.
- `probes` corresponds to the `probes` in the request in the same order. Each item is an integer vector of length n−1, with elements in the range 0..2^32−1. Elements may be duplicated, may not exist in the graph, and may form a non-tree, a non-optimal tree, or violate `pins`. `before` is the **number of optimal trees** whose tree vector is strictly less than the probe, and `member` indicates whether the probe is the optimal tree vector for this query.
- `uses` corresponds to the `uses` in the request in the same order. Each item is an `id` in the range 0..2^32−1. Items may be duplicated or may not exist in the graph. The result is the number of trees selected in the optimal trees for this query that include the specified edge.
- All counts are exact non-negative integers. The four request lists may be empty. If infeasible, `possible=false`, `cost=null`, `count=0`, all `at` items are `null`, all `probes` items are `{"before":0,"member":false}`, and all `uses` items are `0`. All fields are still returned.
- The query does not modify the graph or snapshot. When n=1 and `pins` is empty, an empty tree with zero cost exists.

Taking the initial graph and query from the above example, the optimal vectors are [2,3], [2,8], [9,3], and [9,8] in sequence. The response is:

```json
{"possible":true,"cost":7,"count":4,"at":[[2,3],[9,3],null],"probes":[{"before":1,"member":false},{"before":3,"member":true},{"before":2,"member":false}],"uses":[2,2,0]}
```

If pins=[9], the optimal vectors are only [9,3] and [9,8], and the cost remains 7. If pins=[2,9], both edges point to the same vertex, making the query infeasible. Negative weight cycles are not counted by the integral tree. The locally cheapest combination of incoming edges may not have a path from the root.
