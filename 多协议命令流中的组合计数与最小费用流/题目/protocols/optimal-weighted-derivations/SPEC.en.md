# 动态加权文法的最优推导 / Optimal Derivations in a Dynamic Weighted Grammar

This page defines the subprotocol. See the [combined specification](../../README.md) for its entry point, command prefixes, limits, and tests.

## 1. Derivation trees and optimality

Maintain a context-free grammar with nonnegative integer costs. Nonterminals are numbered 0 through N-1. Terminals are the single characters a, b, c, and d. Every production has a unique unsigned 32-bit integer ID. Identical productions with different IDs are different choices.

A derivation tree uses one production per node, labeled with its ID. The children follow the order of nonterminals on the right-hand side. Terminal and empty-string productions are leaves. The yield is the string of terminal characters read left to right. The exact cost is the sum of all node costs and can exceed 64 bits.

For the requested word and start nonterminal:

1. Report infeasibility if no finite derivation tree yields the word.
2. Otherwise find the minimum cost W and count all trees of cost W.
3. Report an infinite number of optimal trees separately, without applying a modulus to infinity.
4. For the canonical witness, first minimize node count among the minimum-cost trees, then minimize the preorder sequence of production IDs lexicographically.

All minimum-cost trees contribute to the overall count, regardless of size. Different expansion schedules of the same tree do not add choices. The left and right subtrees are selected independently. Preorder visits the root, left subtree, then right subtree, comparing IDs as integers, so 9 precedes 10. There is a finite canonical witness even if infinitely many trees attain minimum cost.

## 2. Protocol and bounds

Use UTF-8 NDJSON, one JSON object per line. All inputs are valid. Emit and flush a response immediately for each command. Standard output contains only responses with LF line endings. Leave stderr empty and exit with status 0 at EOF. Field order and whitespace may vary. All fields, types, and values must match. Floats, strings, and Booleans are not JSON integers for this protocol.

- `1 <= N <= 64`. There are at most 256 productions in total, at most 64 with two nonterminals on the right. Both bounds include disabled productions.
- IDs are distinct integers from 0 through 2^32-1, independent of array order.
- Costs are integers from 0 through 2^63-1. Structure, IDs, and the modulus are fixed. Costs and enabled flags can change.
- A query word contains only a, b, c, and d, with length 0 through 24. Use `""` for the empty string.
- 5000 commands per process at most. At most 32 parse commands.
- Snapshot slots range from 0 through 31. A loaded slot is guaranteed to have been saved.
- Each `parse` request contains at most 32 entries in `at`, all JSON integers from 0 through 2^2048-1. Duplicates, out-of-order indices, and indices past the witness end are valid.
- `2 <= mod <= 2^63-1`, including composite moduli.
- Each scenario has a 60-second limit and a 512 MiB peak working-set limit. Each interactive response is due within 5 seconds. Timing includes interpreter startup, JSON I/O, and computation.

The environment is Windows with CPython 3.14.2. Implement one file, `ink.py`, using the Python standard library. Apart from importing that library and reading its own file, the program cannot read files, write persistent files, access the network, launch subprocesses, or use `ctypes` or system DLLs. General-purpose caching and any internal representation are allowed.

## 3. init

Initialization is the first command and occurs exactly once.

```json
{"op":"init","nonterminals":1,"mod":6,"rules":[
 {"id":0,"lhs":0,"rhs":[0],"cost":0,"enabled":true},
 {"id":7,"lhs":0,"rhs":["a"],"cost":3,"enabled":true}
]}
```

The right-hand side has one of these four forms:

| rhs | Meaning |
| --- | --- |
| `[]` | lhs derives the empty string |
| `["a"]`, or b, c, or d | lhs derives a terminal character. The production is a leaf. |
| `[B]`, integer B | lhs derives one nonterminal |
| `[B,C]`, integers B and C | lhs derives two ordered nonterminals |

All nonterminal indices are valid. `enabled` is a JSON Boolean. Disabled productions cannot appear in any tree. Initialization clears the snapshots and replies `{"ok":true}`.

## 4. Updates and snapshots

Each command below replies `{"ok":true}`.

| Command | Meaning |
| --- | --- |
| `{"op":"weight","id":r,"cost":w}` | Set the production cost, retaining the new value even for a disabled production. |
| `{"op":"enable","id":r,"value":true}` | Set the production's enabled state. |
| `{"op":"save","slot":s}` | Save all costs and enabled states, overwriting the slot. |
| `{"op":"load","slot":s}` | Restore the snapshot. Subsequent changes do not modify the snapshot. |

Structure, modulus, and nonterminal count are unchanged. Queries do not change the grammar or the snapshots.

## 5. parse

```json
{"op":"parse","start":0,"word":"a","at":[0,1,100]}
```

`start` is a valid nonterminal. If it cannot derive `word`, the only response is `{"possible":false}`. Otherwise the response is exactly:

```text
{"possible":true,
 "cost":W,
 "infinite":I,
 "ways":K,
 "witness":{"nodes":M,"sha256":H,"at":[...]}}
```

- W is the minimum cost, an exact JSON integer.
- I is a JSON Boolean indicating infinitely many optimal trees.
- If I is true, K is null. Otherwise, K is the number of optimal trees reduced to its nonnegative residue modulo `mod`. A finite K=0 is consistent with feasibility.
- M is the exact number of nodes of the canonical witness. A terminal or empty-string production counts as 1 node.
- H is the witness SHA-256 digest defined below, as 64 lowercase hexadecimal characters.
- `witness.at` follows the length and order of the request's `at`. An entry at index `at[j]` gives the production ID at that position in the witness preorder. Indices start at 0, with the root at 0. An index at least M yields null.

The witness may be extremely large. Its whole tree and preorder need not be expanded. Identical subtrees can share storage, with separate occurrences still counted in M and in preorder positions.

## 6. Witness hash

Encode each tree node as:

```text
b"DERIVE1"
+ id.to_bytes(4, 'little', signed=False)
+ bytes([arity])
+ the children's 32-byte raw SHA-256 digests in left-to-right order
```

Compute the SHA-256 digest of these bytes. Render the root digest in lowercase hexadecimal. The `DERIVE1` tag is 7 ASCII bytes without a NUL or newline. Arity counts nonterminal children. It is 0 for an empty-string or terminal production, 1 for one nonterminal, and 2 for two. Append the 32 raw bytes of each child digest, not the 64 hexadecimal characters. Cost, enabled state, positions, lhs, and terminal literals are not encoded. The production ID is fixed and unique.

## 7. Examples

- Rule `S -> S` costs 0, and `S -> "a"` costs 3. For word `"a"`, the minimum cost is 3. Infinitely many trees are optimal, while the witness uses only the terminal production and has M=1.
- Change the loop cost to 1. The minimum stays 3, but only 1 tree is optimal.
- Two productions `S -> "a"` with different IDs both cost 0. There are 2 optimal trees. With mod=2, ways=0. The canonical witness uses the smaller ID.
- Let `S -> A A` and `A -> ε` both cost 0. The empty-word witness has 3 nodes, not 0. If A has two distinct empty-string productions, there are 2*2=4 optimal trees.
- A cycle elsewhere in the grammar has no effect on infinity unless it can participate in a minimum-cost derivation of the requested word.
- Infinitely many minimum-cost trees can coexist with a finite canonical witness whose node count is very large.
