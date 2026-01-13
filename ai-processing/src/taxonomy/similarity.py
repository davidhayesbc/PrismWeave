from __future__ import annotations

from collections.abc import Iterable
from typing import List


def cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
    a_list = list(a)
    b_list = list(b)
    if len(a_list) != len(b_list) or not a_list:
        return 0.0

    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for x, y in zip(a_list, b_list):
        fx = float(x)
        fy = float(y)
        dot += fx * fy
        norm_a += fx * fx
        norm_b += fy * fy

    if norm_a <= 0.0 or norm_b <= 0.0:
        return 0.0

    return dot / ((norm_a**0.5) * (norm_b**0.5))


def mean_vector(vectors: List[List[float]]) -> List[float]:
    if not vectors:
        return []
    dim = len(vectors[0])
    sums = [0.0] * dim
    count = 0
    for vec in vectors:
        if len(vec) != dim:
            continue
        for i, value in enumerate(vec):
            sums[i] += float(value)
        count += 1
    if count == 0:
        return []
    return [s / float(count) for s in sums]
