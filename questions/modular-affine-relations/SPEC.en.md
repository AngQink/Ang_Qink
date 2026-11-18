# 模环上仿射关系的构造与计数 / Construction and Counting of Affine Relations over Modular Rings

## 1. State and set semantics

Fix a modulus m. A relation of width d is a set `S ⊆ {0,1,...,m-1}^d`. Its coordinates are the visible ports. Construction, composition, and queries operate on sets. Different intermediate assignments that yield the same visible tuple count once.

Relations may be empty. All constructors are expressed through linear congruences modulo m, affine maps, intersections, joins, and projections. The modulus may be composite, including a large composite or a prime power. Nonzero residues need not be units.

Slots are numbered 0 through 255 and hold values. Overwriting a slot does not affect values previously copied to or computed in another slot. Every command reads its sources from the state at the start of the command. In particular, `dst` may equal `src`, `left`, or `right`.

## 2. Protocol and limits

Use UTF-8 NDJSON with one JSON object per line. All inputs are valid. For each command, emit and flush a response immediately. The next command can depend on the current response, so the program cannot wait for EOF.

- `init` occurs exactly once, as the first command. Source slots are already assigned.
- Slot numbers are 0 through 255. Stored widths are 0 through 16.
- A process uses one modulus, `2 <= m <= 2^127-1`.
- Matrix entries, biases, and right-hand sides are JSON integers in `[-2^127, 2^127-1]`.
- Each `a` has at most 32 rows, with the column count specified by the command. Use `[]` for zero rows and `[[], ...]` for rows of width zero.
- `join` allows at most 16 ties. Ties may repeat, and a port can be tied to multiple ports on the other side.
- `keep` has length 0 through 16. Its indices are valid and may repeat. Output coordinates follow the given order.
- At most 6000 commands per process, including initialization and queries.
- Each scenario has a budget of 30 seconds and 512 MiB peak working set. Each interactive response has a five-second bound (5 seconds). Timing includes interpreter startup, JSON I/O, and computation.

Standard output contains only response lines, each ending in LF, including the last. Leave stderr empty and exit with status 0 at EOF. Field order and whitespace may vary. Field sets, types, and values must be correct. A float, string, or Boolean cannot stand in for a JSON integer.

The test environment is Windows with CPython 3.14.2. Implement a single file, `circuit.py`, using the standard library. Apart from normal imports and reading the program itself, it must not read files, write persistent files, use the network, spawn subprocesses, or use `ctypes` or a system DLL. General-purpose caching and any internal representation are permitted.

## 3. Initialization

```json
{"op":"init","mod":12}
```

Set the modulus and leave all slots unassigned. Reply `{"ok":true}`.

## 4. Constructing and updating slot values

All constructors below reply `{"ok":true}`, including when they produce the empty set. Ports have equal standing, with no implicit direction, nonzero condition, invertibility, or uniqueness guarantee.

### make: simultaneous congruences

```text
{"op":"make","dst":h,"dim":d,"a":[...],"b":[...]}
```

Use an r-by-d matrix a and an r-entry vector b. Store all d-tuples that satisfy `a*x ≡ b (mod m)`. No equations means the full space. Inconsistent equations give the empty set.

### map: affine image

```text
{"op":"map","src":s,"dst":h,"a":[...],"b":[...]}
```

For a source of width d, use an e-by-d matrix a and an e-entry vector b. Store `{(a*x+b) mod m : x ∈ src}`, a relation of width e. Deduplicate results. The matrix may be singular or have zero or repeated rows.

### pin: restriction

```text
{"op":"pin","src":s,"dst":h,"a":[...],"b":[...]}
```

For a source of width d, use an r-by-d matrix a and an r-entry vector b. Keep the original tuples satisfying `a*x ≡ b (mod m)`. The output width is still d.

### meet: intersection

```json
{"op":"meet","left":1,"right":2,"dst":3}
```

The two source widths are equal. Store their set intersection.

### join: independent choices, equality constraints, and projection

```text
{"op":"join","left":l,"right":r,"dst":h,
 "ties":[[i,j],...],"keep":[k0,k1,...]}
```

Let the source widths be p and q. Independently choose `x ∈ left` and `y ∈ right`. Each tie `[i,j]` requires `x[i]=y[j]` as canonical residues. Concatenate x and y to form a tuple z of length p+q, then keep `(z[k0],z[k1],...)` and deduplicate. The left indices are 0 through p-1, followed by q right indices. Hidden coordinates are existentially quantified.

The choices remain independent when both sources name the same slot. Only explicit ties relate their coordinates.

### copy: copy a value

```json
{"op":"copy","src":1,"dst":2}
```

Copy the current value of `src` to `dst`. A later overwrite of `src` leaves the copy intact.

## 5. Queries

Queries leave all slot values unchanged.

### ask: cardinality and first tuple

```json
{"op":"ask","src":1}
```

The entire response is:

```text
{"dim":d,"count":C,"first":F}
```

- C is the exact number of distinct tuples, without reduction modulo m.
- For a nonempty relation, F is the lexicographically least tuple, a d-entry JSON integer array with entries from 0 through m-1. Compare coordinate 0 first, then coordinate 1, and so on.
- For the empty set, give `C=0` and `F=null`, retaining its width d.

### probe: temporary restriction and projection

```text
{"op":"probe","src":s,"a":[...],"b":[...],"keep":[...]}
```

Restrict the source as with `pin`, project to `keep`, and deduplicate. Return the `ask` response for that temporary relation. Each index addresses the original source coordinates and may appear in any order or more than once. Width is the length of `keep`. No slot is created or overwritten.

### has: membership

```json
{"op":"has","src":1,"point":[2,1]}
```

The vector `point` has the source width and entries from 0 through m-1. Return `{"contains":true}` or `{"contains":false}`.

## 6. Examples

- Modulo 12, `6*x=6` has the 6 solutions 1, 3, 5, 7, 9, and 11. Mapping each to `y=6*x` gives just `{(6)}`.
- Modulo 6, `2*x+3*y=1` has 6 solutions. The lexicographically least is `[2,1]`. Another valid tuple such as `[2,3]` is not an acceptable witness.
- The full zero-dimensional relation is `{()}`, with `{"dim":0,"count":1,"first":[]}`. Projecting a nonempty relation to no coordinates gives this relation. The empty relation still has `count=0` and `first=null` after projection.
- A repeated self-join, projection, and overwrite can describe an unrolled network of enormous size. Each step keeps only the current visible relation. Hidden assignments add no multiplicity.

## Public tests

Complete `circuit.py` in this directory and run:

```text
python -B -m unittest discover -s public_tests -v
```

See [samples](samples/) for paired inputs and outputs.
