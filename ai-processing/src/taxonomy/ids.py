from __future__ import annotations

import hashlib
from collections.abc import Iterable


def stable_cluster_id(article_ids: Iterable[str], *, algorithm: str) -> str:
    """Derive a stable cluster id from membership.

    This is deterministic for a given cluster membership + algorithm.
    """

    joined = "\n".join(sorted(article_ids))
    # usedforsecurity is not available on all Python/OpenSSL builds.
    digest = hashlib.sha1(joined.encode("utf-8")).hexdigest()[:12]
    return f"cluster:{algorithm}:{digest}"
