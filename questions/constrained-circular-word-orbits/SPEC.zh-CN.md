# 带权环形词的旋转与反射轨道计数 / Rotation and Reflection Orbit Counts for Weighted Circular Words

维护颜色邻接与权重，统计合法环形词、旋转和换色镜像等价类，以及精确周期与不动词。

## 本地自测

在当前目录实现 `mirror.py`。随题提供的代码用于处理输入与输出，求解逻辑留待实现。

```sh
python -B -m unittest discover -s public_tests -v
```

本题包含 16 个公开测试场景。另可查看[样例输入](samples/demo.ndjson)及[预期输出](samples/demo.expected.ndjson)。

## 1. 对象

颜色编号为 `0..C-1`。给定无向允许邻接矩阵 `E`（允许自环），颜色权重 `w`，以及颜色上的固定对合 `tau`。

- `tau[tau[a]] = a`；允许不动点，允许交换两个颜色。
- `E[a][b] = E[b][a] = E[tau[a]][tau[b]]`。
- `w[a] = w[tau[a]]`。

长度 `n >= 1` 的带位置词是有序元组 `x = (x[0],...,x[n-1])`。合法词必须同时满足：

1. 对所有 `i`，`E[x[i]][x[(i+1) mod n]] = true`，包括首尾邻接。
2. `sum(w[x[i]]) mod Q = residue`。这是对完整长度n的词求和，不是对某个周期块求和。

不同位置上的颜色选择构成不同带位置词；同色不可再区分。长度1要求其颜色有自环；长度2的两个方向检查是同一布尔邻接条件，不另产生边选择方案。

## 2. 两种等价关系与精确周期

下标计算均取模n。定义：

```text
R_k(x)[i] = x[(i+k) mod n]
F_k(x)[i] = tau[x[(k-i) mod n]]
```

`F_k` 在反转位置的同时逐个替换颜色；不是普通反转。以上不变量保证这些变换仍将合法词映射到合法词。

- **necklace**：只允许旋转，即两个词相等，或一个是另一个的某个 `R_k`。
- **bracelet**：允许旋转与上述换色镜像，即一个是另一个的某个 `R_k` 或 `F_k`。
- 词的**精确周期**是使 `R_p(x)=x` 的最小正整数p；p一定整除n。精确周期只考察旋转，不把镜像不动性当成周期。

长度1、2也使用原定义，不更换约定；不同变换可能对所有词作用相同，但等价类定义保持不变。

## 3. 协议与资源

输入输出为UTF-8 NDJSON，每行一个对象。输入保证合法。每条命令立即回复一行并flush，不能等EOF。stdout只含协议响应，使用LF；stderr为空；EOF退出0。允许忽略空白输入行。

响应字段顺序、空格不限；字段集合、类型、值和数组顺序必须精确。整数不能用浮点数、布尔值、字符串替代。拒绝重复JSON字段。

- 基准环境为 Windows / CPython 3.14.2。将解法写在 `mirror.py` 中，仅使用 Python 标准库。
- `1 <= C <= 8`，`1 <= Q <= 8`，`0 <= w[a] < Q`。
- 计数模数 `2 <= mod <= 2^63-1`，**不保证为素数，也不保证与n互素**。
- 每次查询 `1 <= n <= 2^63-1`，其正因子数至多32。
- 每进程至多5000条命令，其中 `orbit` 至多32条。
- 每个进程60秒、峰值工作集512 MiB；在线每条响应至多等待5秒。进程计时包括启动和全部计算/输入输出。
- 每个查询的rotations、mirrors分别至多32项。k是 `0..2^2048-1` 的JSON整数；可重复、乱序、超出n。

除正常标准库导入及本文件外，不读取其他文件，不创建持久化文件，不联网，不启动子进程，不用ctypes或调用外部EXE/DLL。通用缓存允许。

## 4. init

第一条且仅第一条命令：

```json
{"op":"init","colors":2,"inventory_mod":3,"mod":12,
 "mirror":[1,0],"weights":[1,1],
 "edges":[[true,true],[true,true]]}
```

`inventory_mod`是Q，`mod`是计数模数，`mirror`是tau；上述不变量全部成立。响应 `{"ok":true}`。初始化清空所有快照。

C、Q、mod和tau在本进程固定。只有邻接与权重可以修改。

## 5. 更新、快照

以下命令都响应 `{"ok":true}`。

### edge

```json
{"op":"edge","u":0,"v":1,"value":false}
```

将下列位置**同时**设为value，其余位置不变：

```text
(u,v), (v,u), (tau[u],tau[v]), (tau[v],tau[u])
```

重复位置只设置一次。value为JSON布尔。u、v是有效颜色编号。自环也按同一规则处理。

### weight

```json
{"op":"weight","color":0,"value":2}
```

同时令 `w[color] = w[tau[color]] = value`；`0 <= value < Q`。其余权重不变。

### save / load

```json
{"op":"save","slot":31}
{"op":"load","slot":31}
```

slot为0..31。save复制保存**整个邻接矩阵及所有权重**，覆盖该槽旧快照。load恢复它们；输入保证该槽已保存。后续更新、其他槽和后续load均不改变已存快照。查询不修改状态。

## 6. orbit

```json
{"op":"orbit","factors":[[2,1],[3,1]],"residue":0,
 "rotations":[0,1,6],"mirrors":[0,1,7]}
```

`factors`给出n的完整质因数分解：每项 `[p,e]`，p为实际素数，严格递增，e为正整数，`n = product(p**e)`。n=1时factors为空数组。无须做整数分解或验证输入合法性。residue是0..Q-1。

响应字段恰为：

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

- W：当前合法带位置词数量，模mod。
- N：当前合法词按旋转划分的等价类数，模mod。
- B：当前合法词按旋转、换色镜像划分的等价类数，模mod。
- periods：包含n的**所有正因子**，严格递增，即使某行计数为零也保留。
- 每行只计**完整长度n的合法词中，精确周期恰为d**的词或等价类。不是精确周期整除d，也不是重新以长度d和原residue发起查询。
- fixed.rotations：与请求rotations同长同序，第j项为合法带位置词中满足 `R_k(x)=x` 的词数，模mod，其中k是请求的第j项。
- fixed.mirrors：同理，计满足 `F_k(x)=x` 的合法带位置词数，模mod。
- length、period是精确JSON整数；所有计数为0..mod-1的整数。无合法词时所有计数为零，仍返回完整结构。

**先在非负整数意义下计数等价类，再取模。** 取模后为零不代表不存在对象；不能将本应整除的整数计数改为在模环中强行做除法。

## 7. 小例子

1. C=2、Q=1、全邻接、tau=[0,1]、n=3、mod=100：8个词、4个necklace、4个bracelet；周期1有2个词/2类/2类，周期3有6个词/2类/2类。
2. 同上但tau=[1,0]：8个词、4个necklace、2个bracelet。每个F_k均无不动词；周期1有2个词/2类/1类，周期3有6个词/2类/1类。
3. C=1、Q=4、w=[1]、有自环、n=6：只有residue=2有1个合法词。它的精确周期为1，但长度1的单色词权重余数为1；periods中d=1行仍属于原长度6查询。
4. C=1且没有自环：任何正长度都没有合法词。
