# backend/app/agent/vector_store.py

import logging
import os
import uuid
from datetime import datetime, timedelta

from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Condition,
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    PointStruct,
    Range,
    VectorParams,
)

from ...models import NewsItem
from ..utils import clean_value

logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self):
        self.qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
        self.qdrant_port = int(os.getenv('QDRANT_PORT', '6333'))
        self.client = QdrantClient(
            host=self.qdrant_host,
            port=self.qdrant_port,
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.news_collection_name = "portfolio_news"
        self.analysis_collection_name = "portfolio_analysis"
        self.vector_size = 384  # all-MiniLM-L6-v2

        self._initialize_collections()

    def _initialize_collections(self):
        try:
            if not self.client.collection_exists(self.news_collection_name):
                self.client.create_collection(
                    collection_name=self.news_collection_name,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
                )
            if not self.client.collection_exists(self.analysis_collection_name):
                self.client.create_collection(
                    collection_name=self.analysis_collection_name,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
                )
            logger.info("Vector store collections initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise

    def store_news_items(self, news_items: list[NewsItem], asset_key: str):
        try:
            documents = []
            points = []
            for item in news_items:
                doc_text = f"Title: {item.title}\nContent: {item.snippet}"
                documents.append(doc_text)
                metadata = {
                    "asset_key": asset_key,
                    "title": item.title,
                    "url": item.url,
                    "source": item.source or "unknown",
                    "published_at": item.published_at.isoformat() if item.published_at else "",
                    "sentiment": item.sentiment,
                    "impact": item.impact,
                    "relevance_score": item.relevance_score or 0.0,
                    "stored_at": float(datetime.now().timestamp())
                }
                metadata = {k: clean_value(v) for k, v in metadata.items()}
                point_id = str(uuid.uuid4())
                points.append(
                    PointStruct(
                        id=point_id,
                        vector=self.embeddings.embed_query(doc_text),
                        payload=metadata
                    )
                )
            if points:
                self.client.upsert(collection_name=self.news_collection_name, points=points)
                logger.info(f"Stored {len(news_items)} news items for {asset_key}")
        except Exception as e:
            logger.error(f"Failed to store news items: {e}")
            raise

    def search_relevant_news(
        self,
        query: str,
        asset_keys: list[str] | None = None,
        days_back: int = 7,
        limit: int = 10
    ) -> list[dict]:
        try:
            query_embedding = self.embeddings.embed_query(query)
            cutoff_ts = (datetime.now() - timedelta(days=days_back)).timestamp()
            filters = []

            if asset_keys:
                if len(asset_keys) == 1:
                    filters.append(FieldCondition(
                        key="asset_key",
                        match=MatchValue(value=asset_keys[0])
                    ))
                else:
                    filters.append(FieldCondition(
                        key="asset_key",
                        match=MatchAny(any=asset_keys)
                    ))
            filters.append(FieldCondition(
                key="stored_at",
                range=Range(gte=cutoff_ts)
            ))

            result = self.client.search(
                collection_name=self.news_collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=Filter(must=filters)
            )
            formatted_results = []
            for point in result:
                metadata = point.payload or {}
                doc = f"Title: {metadata.get('title', '')}\nContent: {metadata.get('content', '')}"
                formatted_results.append({
                    "document": doc,
                    "metadata": metadata,
                    "relevance_score": point.score
                })
            logger.info(f"Found {len(formatted_results)} relevant news items")
            return formatted_results

        except Exception as e:
            logger.error(f"Failed to search news: {e}")
            return []

    def store_analysis_result(self, analysis_result: dict, portfolio_hash: str):
        try:
            doc_text = (
                f"Analysis: {analysis_result.get('summary', '')}\n"
                f"Recommendations: {', '.join(analysis_result.get('recommendations', []))}"
            )
            metadata = {
                "portfolio_hash": portfolio_hash,
                "analysis_type": analysis_result.get('type', 'general'),
                "timestamp": datetime.now().isoformat(),
                "risk_level": analysis_result.get('risk_level'),
                "confidence": analysis_result.get('confidence', 0.0)
            }
            metadata = {k: clean_value(v) for k, v in metadata.items()}
            analysis_id = str(uuid.uuid4())
            point = PointStruct(
                id=analysis_id,
                vector=self.embeddings.embed_query(doc_text),
                payload=metadata
            )
            self.client.upsert(collection_name=self.analysis_collection_name, points=[point])
            logger.info(f"Stored analysis result: {analysis_id}")
        except Exception as e:
            logger.error(f"Failed to store analysis result: {e}")

    def get_portfolio_history(self, portfolio_hash: str, days_back: int = 30) -> list[dict]:
        try:
            cutoff_ts = (datetime.now() - timedelta(days=days_back)).timestamp()
            filters: list[Condition] = [
                FieldCondition(
                    key="portfolio_hash",
                    match=MatchValue(value=portfolio_hash)
                ),
                FieldCondition(
                    key="timestamp",
                    range=Range(gte=cutoff_ts)
                )
            ]
            result = self.client.scroll(
                collection_name=self.analysis_collection_name,
                limit=50,
                filter=Filter(must=filters)
            )
            history = []
            for point in result[0]:
                history.append(point.payload)
            return sorted(history, key=lambda x: x['timestamp'], reverse=True)
        except Exception as e:
            logger.error(f"Failed to get portfolio history: {e}")
            return []
