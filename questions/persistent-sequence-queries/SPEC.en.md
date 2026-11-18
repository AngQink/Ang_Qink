# 压缩持久化序列的区间查询 / Range Queries on Compressed Persistent Sequences

Implement `loom.py` as a streaming process that maintains branches of persistent integer sequences. References and repetitions can give a sequence up to 2^60 elements. Updates must preserve older versions. The limits rule out expanding the whole virtual sequence into an array. Any data structure that meets the contract is allowed.

## 1. Environment and protocol

The test environment is Windows with CPython 3.14.2. Use the Python standard library and a single file, `loom.py`. Apart from normal imports and reading that same file, the program cannot read other files, write persistent state, use the network, or launch subprocesses.

Input and output are UTF-8 NDJSON, one JSON object per LF-terminated line. Standard output contains only responses. Field order and whitespace do not affect judging. Emit and flush exactly one response immediately after each command. The next input may wait for this response. Exit normally with status 0 at EOF and leave stderr empty.

All JSON inputs, types, version references, ranges, and sizes conform to the specification. JSON numbers are integers, never Booleans. Preserve large integers exactly.

## 2. Values, versions, and coordinates

The modulus is `P = 1000000007` and the hash base is `B = 911382323`. Elements lie in `[0,P)`. Initial values and update coefficients are signed 64-bit integers. Reduce computed values to their nonnegative residues.

Version 0 exists at startup, is empty, and remains active. Each version-creating command assigns the next strictly increasing integer ID, starting at 1. IDs are never reused. Assign a new ID even if the result is empty, unchanged, or entirely references another version.

Old versions are immutable. A command can refer to the same version multiple times or splice a slice of a version into itself. All such references use values at command start. Dropping a handle does not invalidate data shared by other versions.

Indices are zero-based and ranges are half-open `[l,r)` with `0 <= l <= r <= n`. Empty ranges, the whole range, and the empty range at the end are valid. A point query guarantees `0 <= i < n`. Lengths and indices are exact integers without reduction modulo P.

## 3. Version-creating commands

Each command below returns `{"v":version_id,"n":result_length}` and preserves its input versions.

| Input | Result |
| --- | --- |
| `{"op":"new","values":[x0,x1,...]}` | A sequence of these values reduced modulo P. The list may be empty. |
| `{"op":"concat","left":u,"right":v}` | Version u followed by version v. The input versions may be the same. |
| `{"op":"repeat","v":v,"times":k}` | The concatenation of k copies of v. An empty v or k=0 yields an empty version. |
| `{"op":"slice","v":v,"l":l,"r":r}` | The subsequence `[l,r)` of v. |
| `{"op":"splice","v":v,"l":l,"r":r,"src":u,"sl":a,"sr":b}` | Replace `[l,r)` of v with `[a,b)` of u, preserving the order of the unaffected elements. The source and destination may be the same, with overlapping ranges. |
| `{"op":"reverse","v":v,"l":l,"r":r}` | Reverse only `[l,r)` of v. |
| `{"op":"edit","v":v,"l":l,"r":r,"a":a,"b":b,"c":c}` | Update the j-th element inside the range to `y[j]=(a*x[j]+b+c*j) mod P`. Other elements are unchanged. |

In an edit, j starts at 0 at the selected range's left endpoint. Later splices, copies, and reversals move the resulting values without reevaluating any older transform at the new coordinates.

For `[2,5,7]`, edit `[1,3)` with a=2, b=3, c=4 to get `[2,13,21]`. Reverse the whole result to get `[21,13,2]`. The original remains `[2,5,7]`.

For v=`[1,2,3,4]`, `splice(v,1,3,src=v,sl=0,sr=3)` gives `[1,1,2,3,4]`. The source is the complete pre-command version.

## 4. Queries and version removal

### `{"op":"at","v":v,"i":i}`

Return `{"value":element}`.

### `{"op":"query","v":v,"l":l,"r":r}`

Let x[0..m-1] be the selected subsequence. Return exactly these six fields:

```text
{"n":m,
 "sum":       sum(x[j]) mod P,
 "square":    sum(x[j]*x[j]) mod P,
 "moment":    sum(j*x[j]) mod P,
 "forward":   sum(x[j]*B^j) mod P,
 "backward":  sum(x[j]*B^(m-1-j)) mod P}
```

Each sum ranges over `j=0..m-1`, using coordinates relative to the queried subsequence. An empty range returns `{"n":0,"sum":0,"square":0,"moment":0,"forward":0,"backward":0}`. The hashes are defined by these formulas. Exact equality testing between segments is outside this query.

### `{"op":"drop","v":v}`

Drop the active version and return `{"ok":true}`. Do not allocate a new ID. Inputs never drop version 0, drop an ID twice, or refer to a dropped version again. Other versions remain valid even when their contents are identical. Unreferenced data may be reclaimed.

## 5. Input scale and resource limits

- At most 60,000 commands per process.
- A single `new` contains at most 4,096 elements. All `new` calls together contain at most 100,000 elements per process.
- At most 12,000 live versions, including version 0. More versions may be created over the lifetime.
- A version length cannot exceed 2^60. For `repeat`, `k∈[0,2^60]` and the result stays within that length bound.
- Peak working set is at most 512 MiB. Each scenario has a 20-second budget including startup, I/O, and command processing. A streamed response is due within 5 seconds.
- Stress inputs include many live branches, repeated references to a large segment, fragmentation from repeated splicing, interleaved reversals and position-dependent edits, deep histories, and many dropped versions.

Avoid scaling work with virtual sequence length and retaining inaccessible version history indefinitely. Handle shared nodes and coordinate changes correctly. Public tests give basic feedback.

## Public tests

Complete `loom.py` and run:

```text
python -B -m unittest discover -s public_tests -v
```

See [samples](samples/) for paired inputs and expected outputs.
