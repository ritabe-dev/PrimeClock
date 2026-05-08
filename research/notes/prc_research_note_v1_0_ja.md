# Prime Reciprocal Covering v1.0

**English title:** Prime Reciprocal Covering: finite-N arc covering structure from prime reciprocal phases

**Abstract.** Prime Reciprocal Covering (PRC) is a finite-`N` experimental
framework that places prime-indexed arcs on the unit circle at phases
`{N/p}` with width `1/p`. This note consolidates the current v0.3--v0.9
experiments. The main object is the uncovered measure `A(N)=|T \ U_N|`, not
only the complete-covering event `A(N)=0`. The current evidence suggests that
the residual uncovered set produced by PRC is more fragmented than a
branch-uniform random placement preserving the same arc widths. No new theorem
about the distribution of primes is claimed.

## 1. PrimeClock から PRC へ

出発点は PrimeClock だった。素数秒に新しい周期針が生まれ、素数 `p` の
針は `p` 秒で一周する。その針の中心位相は、時刻を整数 `N` と見ると

```text
{N/p}
```

で表せる。

Prime Reciprocal Projection (PRP) は、この中心位相だけを見る点配置だった。
一方、Prime Reciprocal Covering (PRC) は、点だけではなく針の幅も残す。
つまり、各素数 `p` が円周上に幅 `1/p` の小さな弧を置くと考える。

このノートの中心問いは次である。

```text
PRCの未被覆量 A(N) と残差gap構造は、
同じarc量を持つランダム被覆と比べて何が違うのか。
```

ここで重要なのは、`A(N)=0` になる数だけを集めることではない。完全被覆は
目立つイベントだが、研究対象の本体は、被覆がどのように進み、未被覆集合が
どのように残るかである。

## 2. 定義

円周を

```text
T = R/Z
```

とする。整数 `N >= 2` と素数 `p <= N` に対して、

```text
c_p(N) = {N/p}
r_p    = 1/(2p)
I_p(N) = [c_p(N)-r_p, c_p(N)+r_p] on T
```

を定義する。`I_p(N)` は、中心 `{N/p}`、幅 `1/p` の円弧である。

全体の被覆集合は

```text
U_N = union_{p<=N, p prime} I_p(N)
```

であり、主指標は未被覆量

```text
A(N) = |T \ U_N|
```

である。`A(N)` は2次元の面積ではなく、単位円周上の1次元測度である。
完全被覆イベントは

```text
C0(N) = 1[A(N)=0]
```

と書く。ただし、浮動小数点の `A(N)=0` だけから exact な `C0(N)` とは
言わない。exact complete covering は rational interval arithmetic で
認定する。

また、分枝

```text
B_k(N) = {p prime : floor(N/p)=k}
```

を使う。累積分枝は

```text
U_{<=K}(N) = union of arcs from branches 1..K
A_{<=K}(N) = |T \ U_{<=K}(N)|
```

である。PRCでは、`A(N)` だけでなく、`K` を増やしたときに未被覆集合が
どのように減るかを見る。

## 3. 観察1: `A(N)` が主指標である

初期のPRC実験では、`A(N)` が単調に小さくなるわけではないことが見えた。
これは失敗ではなく、PRCが単なる「素数が増えるほど空白が減る」過程では
ないことを示している。

独立ランダム弧の粗い基準は

```text
random_arc_baseline_A(N) = exp(-sum_{p<=N} 1/p)
```

である。これはPRCの定理ではなく、同じ幅の弧をランダムに置いたときの
未被覆量のスケールを見るための比較対象である。

PRCでは、`A(N)` がこの基準より大きいことも小さいこともある。したがって、
complete値だけを追うよりも、

```text
A(N), G(N), component_count, gap quantiles
```

を一緒に見る方がよい。`C0(N)` は極端事例として重要だが、研究の中心は
`A(N)` と未被覆集合の形である。

## 4. 観察2: branch 1 は prime-gap layer である

branch 1 は

```text
floor(N/p)=1
```

つまり

```text
N/2 < p <= N
```

にある素数から成る。この層では、隣り合う素数 `p_i < p_j` の中心間隔は

```text
N*(p_j-p_i)/(p_i*p_j)
```

になる。そこから両端の弧半径を引くと、branch 1 だけで露出するgapの
近似は

```text
max(0, N*(p_j-p_i)/(p_i*p_j) - 1/(2p_i) - 1/(2p_j))
```

である。

したがって、branch 1 は素数間隔をそのまま円周へ写したものではない。
より正確には、

```text
branch 1 は transformed prime-gap layer である。
```

この層が大きなgapの候補を作り、lower branches がそのgapをどれだけ
埋め戻すかを見るのが PRC の自然な読み方である。

## 5. 観察3: lower branches は単純な早期fill-inではない

v0.3 では `A_{<=K}(N)` を使って、分枝を `1..K` まで足したときに
未被覆量がどう減るかを見た。

v0.4 では、exact complete-covering values と matched controls を比較した。
もし complete values が単に「早い段階でよく埋まる数」なら、`K=1000`
までの fill-in depth や residual が controls と大きく違うはずである。

しかし、v0.4の結果はそう単純ではなかった。complete rows は、少なくとも
この cohort では、単純な早期fill-in cases には見えなかった。

その後、v0.5--v0.8では `K=1000` 後の残差gap構造を調べた。ここで
`residual_gap_count` は、complete と controls を分ける候補診断として
出てきた。v0.6/v0.7 では、complete rows が matched controls より
残差component数が少ない傾向が見えた。

ただし、これは主張ではなく探索である。v0.8 で seed clustering と control
reuse を監査した結果、`local_mod6_control` では示唆的だが、hard controls
全体で確認的な結論にはならなかった。

ここまでで分かったことは、次の程度に留めるべきである。

```text
complete values には、matched controls より残差componentが少ない傾向が
一部見える。しかし、それだけで complete covering の説明とは言えない。
```

## 6. 観察4: branch-uniform null では PRC はより fragmented

v0.9 では、初めて構造保存null modelを入れた。モデル名は

```text
branch_uniform
```

である。

このnull modelでは、各 `N` と `K=1000` について、次を保存する。

```text
branch sizes
prime arc widths 1/p
```

一方で、中心 `{N/p}` は branch ごとに独立な一様乱数へ置き換える。
つまり、弧の量とbranch構成は同じだが、PRC特有の reciprocal phase
structure は壊す。

v0.9 は、既存の33 eligible seed cohort、4 roles、合計132 rowsに対して、
各row 1000 iterations で比較した。

| cohort | rows | median observed percentile | median observed < null rate | below null p05 | above null p95 |
|---|---:|---:|---:|---:|---:|
| complete | 33 | 0.929 | 0.071 | 0 | 12 |
| local_mod6_control | 33 | 0.949 | 0.051 | 1 | 16 |
| band_mod6_control | 33 | 0.957 | 0.043 | 0 | 17 |
| band_ordinary_control | 33 | 0.962 | 0.038 | 0 | 18 |

この結果は重要である。v0.7の直感だけを見ると、complete rows は
`residual_gap_count` が少ない方向に見えた。しかし branch-uniform null と
比べると、complete rows だけでなく、controls も含めたPRC全体が高い
observed percentile を持つ。

つまり、v0.9の保守的な読みは次である。

```text
PRC residual sets are more fragmented than branch-uniform random placements
with the same arc widths.
```

これは complete-specific な低component効果ではなく、PRCの phase placement
全体に関わる現象に見える。

この結果により、研究の焦点は少し変わる。

```text
なぜ complete values は gap_count が少ないのか
```

だけでは狭すぎる。より本筋の問いは、

```text
なぜ reciprocal phase structure は、同じarc量のランダム配置よりも
未被覆集合を細かく分裂させるのか。
```

である。

## 7. 現時点の結論

現時点で言えることは、次の4点である。

第一に、PRCの主指標は `A(N)` である。complete covering は重要だが、
`A(N)` と未被覆集合の形を見なければ、PRCの構造は読めない。

第二に、branch 1 は transformed prime-gap layer として読める。大きな
gap候補はここから生まれ、lower branches がそれをどう埋めるかがPRCの
中心的な現象である。

第三に、complete values は単純な早期fill-inだけでは説明できない。残差gap
構造、特に component count は有用な診断だが、complete covering の説明と
してはまだ弱い。

第四に、branch-uniform null との比較では、PRC residual sets はより
fragmented に見える。これは、PRCが単なるランダム円弧被覆ではなく、
reciprocal phase structure を持つことを示す、現在もっとも本筋に近い
実験結果である。

## 8. Non-Claims

このノートでは、次を主張しない。

- 新しい素数分布定理を発見したとは言わない。
- PRPの極限密度が新規だとは言わない。
- complete covering の発生法則を説明したとは言わない。
- `residual_gap_count` が `A(N)=0` の原因だとは言わない。
- branch-uniform null が最終的なnull modelだとは言わない。
- v0.9の高fragmentationが漸近的に成り立つとは言わない。
- Cramér予想など未解決問題への直接的な解法だとは言わない。

この研究は、現時点では有限 `N` の experimental artifact である。主張の
強さは、再現可能な数値実験と定義済みの比較モデルの範囲に限る。

## 9. 次の研究課題

次にやるべきことは、実験をむやみに増やすことではなく、v0.9の読みを
より精密にすることである。

第一に、branch-uniform null はかなり粗い。branch sizes と widths は保存
するが、within-branch の arithmetic order は壊している。次は local
branch-bucket shuffle のように、より近いnullを作る必要がある。

第二に、`A(N)` と `component_count` の関係を分けて読む必要がある。
高fragmentationは、未被覆量が小さいこととは別の現象である。

第三に、complete values と controls の比較は、より大きいcohortで確認する
必要がある。ただし、これは v0.9 の null model 読解が固まってからでよい。

第四に、v1.0以降では英語版の短い共有ノートを作る価値がある。外部の数学者
や実験数学に詳しい人へ見せるなら、主張をさらに保守的にし、既知結果との
関係を明確にする必要がある。

## Reproducibility

主要な生成コマンドは以下である。

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill \
  --n 1000 10000 100000 1000000 39069 372759 \
  --max-branch 1000 \
  --out data/summaries/prc_branch_fill_v0_3.csv

python -m prime_reciprocal_projection.cli covering-branch-fill-residual-gaps \
  --manifest data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv \
  --summary data/summaries/prc_branch_fill_cohort_summary_v0_4.csv \
  --max-branch 1000 \
  --out data/summaries/prc_branch_fill_residual_gaps_v0_5.csv

python -m prime_reciprocal_projection.cli covering-branch-fill-null-model \
  --manifest data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv \
  --observed data/summaries/prc_branch_fill_residual_gaps_v0_5.csv \
  --model branch_uniform \
  --max-branch 1000 \
  --iterations 1000 \
  --seed 1729 \
  --out data/summaries/prc_branch_uniform_null_v0_9.csv \
  --summary-out data/summaries/prc_branch_uniform_null_summary_v0_9.csv \
  --figures-out figures/v0
```

対応する詳細ログは以下に残している。

```text
notes/prc_main_v0_3.md
notes/prc_main_v0_4.md
notes/prc_main_v0_5.md
notes/prc_main_v0_6.md
notes/prc_main_v0_7.md
notes/prc_main_v0_8.md
notes/prc_main_v0_9.md
```
