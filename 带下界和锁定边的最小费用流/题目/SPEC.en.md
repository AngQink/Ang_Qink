# 带下界和锁定边的最小费用流 / Minimum-Cost Flow with Lower Bounds and Fixed Edges

Maintain a directed network to compute the minimum cost flow with flow lower and upper bounds and temporary locks, and query the feasible range for each edge in the optimal flow.

## Local Self-Test

Implement `tide.py` in the current directory. The code provided with the problem handles input and output; the solving logic is left for implementation.

```sh
python -B -m unittest discover -s public_tests -v
```

This problem contains 16 public test scenarios. You can also refer to the [sample input](samples/demo.ndjson) and [expected output](samples/demo.expected.ndjson).

## 1. Objects

Maintain a directed multigraph. Vertices are numbered from 0 to n-1. Each edge has a unique numeric id, fixed endpoints u and v, and variable lower bound lo, upper bound hi, and unit cost cost. Self-loops and multiple edges between the same endpoints are allowed. Each edge is assigned an integer flow f.

Each vertex has an integer balance. A feasible flow must simultaneously satisfy:

- Each edge satisfies lo ≤ f ≤ hi.
- For each vertex, the sum of flows on all outgoing edges minus the sum of flows on all incoming edges equals the balance. Self-loops are counted once on both sides, contributing zero net flow. A positive balance represents net outflow.
- If a query temporarily locks the flow of a certain edge, the locked value must also be satisfied.

The total cost is the sum of cost × f for all edges, including self-loops. Negative costs are allowed. If feasible, first minimize the total cost, then sort the flows in **ascending order of edge id**, and among all minimum-cost flows, select the one with the lexicographically smallest flow vector. Each lock is valid only for the current query.

## 2. Environment and Constraints

The benchmark environment is Windows / CPython 3.14.2. Write the solution in `tide.py`, using only the Python standard library. The program reads commands from standard input and writes responses to standard output. Except for importing standard libraries, the program does not read or write files, does not connect to the network, does not spawn subprocesses, and does not call external native code. General caching is allowed.

- $1 \le n \le 24$, $0 \le \text{number of edges} \le 96$. IDs are integers in the range $0..2^{32}-1$, distinct. Endpoint IDs are valid.
- $0 \le lo \le hi \le 2^{63}-1$. Costs are in the range $-(2^{63}-1)..2^{63}-1$. Each balance is in the range $-2^{70}..2^{70}$. The sum of balances may be non-zero.
- Each process handles at most 5000 commands, of which at most 48 are `solve`. Each `solve` handles at most 16 temporary locks and 16 interval queries.
- Each scenario starts a new process. Each process has a 60-second time limit and a peak working set of 512 MiB. In online scenarios, each reply is limited to 5 seconds.
- UTF-8 NDJSON. Each line is a valid JSON object. Reply immediately and flush after reading each line; do not wait for EOF. stdout contains only replies, with LF line endings, stderr is empty, and exit code is 0 on EOF. Blank input lines may be ignored.
- The order of fields in response objects and whitespace are arbitrary. The set of fields, types, values, and array order must match. Integers must not be converted to strings, floats, or booleans. Duplicate JSON fields are rejected. All operations are mathematically exact; costs and intermediate values may exceed 64 bits.

## 3. Commands

The first and only first command is `init`.

```json
{"op":"init","vertices":2,"balance":[3,-3],"edges":[{"id":9,"u":0,"v":1,"lo":0,"hi":4,"cost":2},{"id":3,"u":0,"v":1,"lo":0,"hi":2,"cost":2}]}
```

init sets the fixed number of vertices, edge IDs, and endpoints. The initial order of edges is arbitrary. Subsequently, the lo, hi, cost of each edge, and the balance of each node can be modified. Any valid combination of balances and edge parameters is allowed, including completely infeasible states.

```json
{"op":"patch","edges":[[9,0,4,-1]],"balance":[[0,2],[1,-2]]}
{"op":"save","slot":31}
{"op":"load","slot":31}
```

- The `edges` entry in `patch` is `[id, lo, hi, cost]`, which completely replaces the three variable parameters of that edge. The `balance` entry is `[vertex_id, new_balance]`. The target in each list is unique, and the list can be empty. Parameters not listed retain their current values. The entire command is treated as a single update.
- `save` copies all variable parameters to the specified slot, overwriting the old value. `load` restores the specified slot. Slot numbers range from 0 to 31, and `load` guarantees that the slot has been saved. Subsequent updates, other slots, and repeated `load` operations do not alter the saved snapshot.

`init`, `patch`, `save`, and `load` all return exactly `{"ok": true}`.

## 4. Queries

```json
{"op":"solve","pins":[[9,2]],"inspect":[3,9,3]}
```

- `pins` is a list of [edge id, flow]. The id must exist, and each id can appear at most once. The locked value is in the range 0..2^63−1 and may exceed the current upper/lower bounds of the edge. In such cases, this operation is directly infeasible. The order of items in `pins` is arbitrary.
- `inspect` is a list of edge ids, where each item exists and may be repeated. Both lists can be empty.
- `solve` does not modify parameters or snapshots; subsequent queries must independently interpret their respective `pins`.

When infeasible, only return:

```json
{"possible":false}
```

Return when feasible:

```json
{"possible":true,"cost":6,"flow":[[3,1],[9,2]],"ranges":[[1,1],[2,2],[1,1]]}
```

The previous example uses initial parameters and has not yet executed a patch. `cost` is the minimum total cost. `flow` contains the [id, flow] for each edge, sorted in **ascending order of numeric id**, representing the aforementioned canonical optimal solution. `ranges` and `inspect` are in the same order item by item. Each item [min_flow, max_flow] is calculated individually for the specified edge, with the extreme values taken over **all minimum cost flows under the current locked conditions**. Other edges, including those with smaller ids, may vary to achieve these extremes. The extreme value of one edge does not need to be realized simultaneously with that of another edge. All values are exact integers.

In the initial graph, solving without pins and querying [3,9] yields the canonical flow [[3,0],[9,3]], with the two intervals being [0,2] and [1,3], respectively. Locking id 9 to 0 results in infeasibility. After locking, the cost should be minimized again, even if the minimum cost is higher than the optimal value without locks.

Negative cost cycles can reduce the cost when all balances are zero. Self-loops also participate in objective and lexicographical comparisons. Even if the original costs of any two edges are different, they may still be part of the same optimal flow change. For example, the total costs of two different paths may be identical.
