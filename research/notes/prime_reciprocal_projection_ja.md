# Prime Reciprocal Projection

Prime Reciprocal Projection (PRP) は、旧 PrimeClock の視覚化から出てきた
研究用の記法である。

整数 `N >= 2` を固定し、素数 `p <= N` に対して

```text
Phi_N(p) = {N / p}
```

を考える。ここで `{x}` は小数部分で、値は `[0,1)` に入る。

このとき

```text
mu_N = (1 / pi(N)) * sum_{p<=N, p prime} delta_{Phi_N(p)}
```

は `[0,1)` 上の経験分布になる。

最初の観察対象は、この経験分布が一様分布ではなく、

```text
rho(x) = sum_{k>=1} 1/(k+x)^2
```

に近づくという構造である。

この文書では、現段階では新しい素数分布定理を主張しない。目的は、
定義、既知結果との関係、再現可能な数値実験、そして次に検証すべき
予想を整理することにある。

