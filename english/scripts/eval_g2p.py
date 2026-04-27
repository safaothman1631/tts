"""Phoneme-error-rate evaluation for the G2P stack against CMUDict."""
from __future__ import annotations

import argparse
import random


def per(ref: list[str], hyp: list[str]) -> float:
    """Phoneme Error Rate (Levenshtein-based)."""
    if not ref:
        return 0.0 if not hyp else 1.0
    n, m = len(ref), len(hyp)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if ref[i - 1] == hyp[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp[n][m] / n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    random.seed(args.seed)
    try:
        from g2p_en import G2p  # type: ignore
    except ImportError:
        print("g2p-en not installed.")
        return 1
    g = G2p()
    cmu = g.cmu  # dict[word, list[list[arpa]]]
    words = random.sample(list(cmu.keys()), min(args.n, len(cmu)))

    total = 0.0
    for w in words:
        ref = [p for p in cmu[w][0] if p != " "]
        hyp = [p for p in g(w) if p != " "]
        total += per(ref, hyp)
    avg = total / len(words)
    print(f"Mean PER over {len(words)} words: {avg*100:.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
