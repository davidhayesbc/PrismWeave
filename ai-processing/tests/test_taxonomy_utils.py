from __future__ import annotations

from pathlib import Path

from src.taxonomy.ids import stable_cluster_id
from src.taxonomy.models import ArticleTagAssignment, Tag, TaxonomyCategory
from src.taxonomy.normalize import canonicalize_normalized_name, normalize_name
from src.taxonomy.store import TaxonomyStore, TaxonomyStoreConfig


def test_normalize_name_slugifies_deterministically() -> None:
    assert normalize_name(" Large Language Models ") == "large-language-models"
    assert normalize_name("K8s / Kubernetes") == "k8s-kubernetes"
    assert normalize_name("CI/CD") == "ci-cd"


def test_canonicalize_synonyms() -> None:
    assert canonicalize_normalized_name("llm") == "large-language-models"
    assert canonicalize_normalized_name("k8s") == "kubernetes"


def test_stable_cluster_id_is_deterministic() -> None:
    ids1 = ["b", "a", "c"]
    ids2 = ["c", "b", "a"]

    c1 = stable_cluster_id(ids1, algorithm="kmeans")
    c2 = stable_cluster_id(ids2, algorithm="kmeans")
    assert c1 == c2


def test_taxonomy_store_roundtrip(tmp_path: Path) -> None:
    db_path = tmp_path / "taxonomy.sqlite"
    store = TaxonomyStore(TaxonomyStoreConfig(sqlite_path=db_path))
    store.initialize()

    categories = [
        TaxonomyCategory(id="cat:tech", name="Tech", description="Tech", parent_id=None, level=0),
        TaxonomyCategory(id="cat:tech/ai", name="AI", description="AI", parent_id="cat:tech", level=1),
    ]
    tags = [
        Tag(id="tag:llm", name="LLM", normalized_name="llm", description="LLM", category_id="cat:tech/ai"),
        Tag(
            id="tag:kubernetes",
            name="Kubernetes",
            normalized_name="kubernetes",
            description="Kubernetes",
            category_id="cat:tech",
        ),
    ]

    store.upsert_categories(categories)
    store.upsert_tags(tags)
    loaded = store.list_tags()
    assert [t.id for t in loaded] == ["tag:kubernetes", "tag:llm"]

    store.map_cluster_to_category("cluster:kmeans:abc", "cat:tech", "cat:tech/ai")
    mapping = store.get_cluster_category_map()
    assert mapping["cluster:kmeans:abc"] == ("cat:tech", "cat:tech/ai")

    store.upsert_article_tag_assignments([ArticleTagAssignment(article_id="a1", tag_id="tag:llm", confidence=0.9)])
    assignments = store.get_article_tags("a1")
    assert assignments[0].tag_id == "tag:llm"
    assert assignments[0].confidence == 0.9
