from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import chromadb

from .models import Cluster, Tag


@dataclass(frozen=True)
class ClusterStoreConfig:
    persist_path: Path
    clusters_collection_name: str = "clusters"
    tag_embeddings_collection_name: str = "tag-embeddings"


class ClusterVectorStore:
    def __init__(self, config: ClusterStoreConfig):
        self._config = config
        self._client = chromadb.PersistentClient(path=str(config.persist_path))

    def upsert_clusters(self, clusters: List[Cluster]) -> None:
        collection = self._client.get_or_create_collection(name=self._config.clusters_collection_name)

        ids: List[str] = []
        embeddings: List[List[float]] = []
        metadatas: List[Dict[str, Any]] = []
        documents: List[str] = []

        for cluster in clusters:
            if not cluster.centroid_embedding:
                continue
            ids.append(cluster.id)
            embeddings.append(cluster.centroid_embedding)
            meta = dict(cluster.metadata)
            meta.update(
                {
                    "size": len(cluster.article_ids),
                    "category_id": cluster.category_id,
                    "subcategory_id": cluster.subcategory_id,
                }
            )
            metadatas.append(meta)
            documents.append("cluster centroid")

        if ids:
            collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

    def query_nearest_cluster(
        self,
        embedding: List[float],
        *,
        n_results: int = 1,
    ) -> Dict[str, Any]:
        collection = self._client.get_or_create_collection(name=self._config.clusters_collection_name)
        return collection.query(query_embeddings=[embedding], n_results=n_results, include=["distances", "metadatas"])

    def upsert_tag_embeddings(self, tag_embeddings: Dict[str, List[float]], tags: Dict[str, Tag]) -> None:
        """Store tag embeddings in ChromaDB for fast tag assignment."""

        collection = self._client.get_or_create_collection(name=self._config.tag_embeddings_collection_name)

        ids: List[str] = []
        embeddings: List[List[float]] = []
        metadatas: List[Dict[str, Any]] = []
        documents: List[str] = []

        for tag_id, embedding in sorted(tag_embeddings.items()):
            tag = tags.get(tag_id)
            if not tag or not embedding:
                continue
            ids.append(tag_id)
            embeddings.append(embedding)
            metadatas.append(
                {
                    "tag_id": tag.id,
                    "name": tag.name,
                    "normalized_name": tag.normalized_name,
                    "category_id": tag.category_id,
                }
            )
            documents.append(tag.description)

        if ids:
            collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

    def query_tag_embeddings(self, embedding: List[float], *, n_results: int = 10) -> Dict[str, Any]:
        collection = self._client.get_or_create_collection(name=self._config.tag_embeddings_collection_name)
        return collection.query(query_embeddings=[embedding], n_results=n_results, include=["distances", "metadatas"])
