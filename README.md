# 14msv-solver

## このディレクトリについて

Alith GamesおよびArtless Gamesが開発したsteamゲーム、[14 minesweeper variants](https://store.steampowered.com/app/1865060/14/)を解く/ヒントを求めるプログラム

## 開発済みの機能

- 対応済みのマインスイーパの種類
  - セル別: V, M, L, X, X', K, LM, MX
  - セル全体: V, Q, T, D, B, A, QT
  - 上記の組み合わせ
- 盤面の状態を入力し、安全/地雷が確定するセルを表示する機能

## 開発予定の機能

- 今後対応予定のマインスイーパの種類
  - セル別: W, N, P, E, MN, NX, UW
  - セル全体: C, O, S, T', D', H, CD, CQ, CT, OQ, OT
  - [14 minesweeper variants 2 demo](https://store.steampowered.com/app/2631960/14_Minesweeper_Variants_2/)に登場する4種のバリアント
- 今後実装予定の機能
  - 盤面の状態を入力し、制約が最小となる条件のマスを表示する機能（ヒント機能）

## 定式化

python-MIPを使用して解を見つけているため、各セルのルールをMIP(混合整数計画問題)で定式化する必要がある。

- マインスイーパのサイズ: $N \in \{5, 6, 7, 8\}$
- セル位置: $i, j (1 \leq i, j \leq N)$
- セルの状態: $x_{i, j} \in \{0, 1\}$
  - 安全セル: $x_{i, j}=0$
  - 地雷セル: $x_{i, j}=1$
- 地雷総数を$M$とすると、以下の制約式が成り立つ。

$$
\sum_{i, j}x_{i, j} = M
$$

### V: vanilla

- セル$i, j$の数値を$\theta_{i, j}^V$とする。
- セル$i, j$の近傍$\Omega_{i, j}^V$を、$\Omega_{i, j}^V:=\{u \neq i, v \neq j | i-1 \leq u \leq i+1, j-1 \leq v \leq j+1\}$とする。

ルールVは以下の制約式で記述できる。

$$
\sum_{i, j \in \Omega_{i, j}^V}x_{i, j} = \theta_{i, j}^V
$$

### M: multiple

- セル$i, j$の数値を$\theta_{i, j}^M$とする。
- セル$i, j$の近傍$\Omega_{i, j}^M$を、$\Omega_{i, j}^M:=\Omega_{i, j}^V$とする。
- セル$i, j$の重み$c_M(i, j)$を以下のように定義する。

$$
c_M(i, j) = 
\begin{cases}
  2 & \text{if $i \cdot j \bmod 2 = 0$}\\
  1 & \text{if $i \cdot j \bmod 2 = 1$}
\end{cases}
$$

ルールMは以下の制約式で記述できる。

$$
\sum_{i, j \in \Omega_{i, j}^M}c_M(i, j) \cdot x_{i, j} = \theta_{i, j}^M
$$

### L: liar

- セル$i, j$の数値を$\theta_{i, j}^L$とする。
- セル$i, j$の近傍$\Omega_{i, j}^L$を、$\Omega_{i, j}^L:=\Omega_{i, j}^V$とする。
- 変数$z_{i, j}^L \in \{0, 1\}$を導入する。

ルールLは以下の制約式で記述できる。

$$
(2z_{i, j}^L-1) + \sum_{i, j \in \Omega_{i, j}^L}x_{i, j} = \theta_{i, j}^L
$$

### X: cross

- セル$i, j$の数値を$\theta_{i, j}^X$とする。
- セル$i, j$の近傍$\Omega_{i, j}^X$を、$\Omega_{i, j}^X:=\{u=i, v \neq j | j-2 \leq v \leq j+2\} \cup \{u \neq i, v = j | i-2 \leq u \leq i+2\}$とする。

ルールXは以下の制約式で記述できる。

$$
\sum_{i, j \in \Omega_{i, j}^X}x_{i, j} = \theta_{i, j}^X
$$


### X': mini cross

- セル$i, j$の数値を$\theta_{i, j}^{X'}$とする。
- セル$i, j$の近傍$\Omega_{i, j}^{X'}$を、$\Omega_{i, j}^{X'}:=\{u=i, v \neq j | j-1 \leq v \leq j+1\} \cup \{u \neq i, v = j | i-1 \leq u \leq i+1\}$とする。

ルールX'は以下の制約式で記述できる。

$$
\sum_{i, j \in \Omega_{i, j}^{X'}}x_{i, j} = \theta_{i, j}^{X'}
$$


### K: knight

- セル$i, j$の数値を$\theta_{i, j}^K$とする。
- セル$i, j$の近傍$\Omega_{i, j}^K$を、$\Omega_{i, j}^K:=\{u, v | u = i \plusmn 1, v = j \plusmn 2\} \cup \{u, v | u = i \plusmn 2, v = j \plusmn 1\}$とする。

ルールKは以下の制約式で記述できる。

$$
\sum_{i, j \in \Omega_{i, j}^K}x_{i, j} = \theta_{i, j}^K
$$


### LM: liar-multiple

- セル$i, j$の数値を$\theta_{i, j}^{LM}$とする。
- セル$i, j$の近傍$\Omega_{i, j}^{LM}$を、$\Omega_{i, j}^{LM}:=\Omega_{i, j}^V$とする。

ルールLMは以下の制約式で記述できる。

$$
(2z_{i, j}^L-1) + \sum_{i, j \in \Omega_{i, j}^{LM}}c_M(i, j) \cdot x_{i, j} = \theta_{i, j}^{LM}
$$


### MX: multiple-cross

- セル$i, j$の数値を$\theta_{i, j}^{MX}$とする。
- セル$i, j$の近傍$\Omega_{i, j}^{MX}$を、$\Omega_{i, j}^{MX}:=\Omega_{i, j}^X$とする。

ルールLMは以下の制約式で記述できる。

$$
\sum_{i, j \in \Omega_{i, j}^{MX}}c_M(i, j) \cdot x_{i, j} = \theta_{i, j}^{MX}
$$


### Q: quad

- セル$i, j$の近傍$\Omega_{i, j}^Q$を、$\Omega_{i, j}^Q:=\{u, v | i \leq u \leq i+1, j \leq v \leq j+1\}$とする。

ルールQは以下の制約式で記述できる。

$$
\sum_{u,v \in \Omega_{u, v}^Q}x_{u, v} \geq 1,\  \forall i,j \in \{1, \cdots N-1\}, 
$$


### 記述予定

- T, D, B, A, QT
