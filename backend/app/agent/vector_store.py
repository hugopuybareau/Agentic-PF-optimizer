# backend/app/agent/vector_store.py

import os
import logging
import chromadb

from typing import List, Dict, Optional
from datetime import datetime, timedelta
# from chromadb.types import PyEmbedding
from langchain_huggingface import HuggingFaceEmbeddings

from .state import NewsItem

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.chroma_host = os.getenv('CHROMA_HOST', 'localhost')
        self.chroma_port = os.getenv('CHROMA_PORT', '8001')
        self.client = chromadb.HttpClient(
            host=self.chroma_host,
            port=int(self.chroma_port)
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
        )   
        self.news_collection_name = "portfolio_news"
        self.analysis_collection_name = "portfolio_analysis"
        self._initialize_collections()
    
    def _initialize_collections(self):
        try:
            # news
            try:
                self.news_collection = self.client.get_collection(self.news_collection_name)
            except:
                self.news_collection = self.client.create_collection(
                    name=self.news_collection_name,
                    metadata={"description": "Portfolio related news articles"}
                )
            
            # analysis
            try:
                self.analysis_collection = self.client.get_collection(self.analysis_collection_name)
            except:
                self.analysis_collection = self.client.create_collection(
                    name=self.analysis_collection_name,
                    metadata={"description": "Portfolio analysis results"}
                )
                
            logger.info("Vector store collections initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise

    @staticmethod
    def _clean_value(val): # only types that can be serialized in chroma
        if isinstance(val, (str, int, float, bool)): return val
        elif val is None: return ""
        elif isinstance(val, dict): return val.get("label") or str(val)
        else: return str(val)
    
    def store_news_items(self, news_items: List[NewsItem], asset_key: str):
        try:
            documents = []
            metadatas = []
            ids = []
            
            for i, item in enumerate(news_items):
                doc_text = f"Title: {item.title}\nContent: {item.snippet}"
                documents.append(doc_text)
                
                metadata = {
                    "asset_key": asset_key,
                    "title": item.title,
                    "url": item.url,
                    "source": item.source or "unknown",
                    "published_at": item.published_at.isoformat() if item.published_at else None,
                    "sentiment": item.sentiment,
                    "impact": item.impact,
                    "relevance_score": item.relevance_score or 0.0,
                    "stored_at": datetime.now().isoformat()
                }
                metadata = {k: VectorStore._clean_value(v) for k, v in metadata.items()}
                metadatas.append(metadata)

                timestamp = int(datetime.now().timestamp() * 1000)
                ids.append(f"{asset_key}_{timestamp}_{i}")
            
            embeddings = self.embeddings.embed_documents(documents)
            self.news_collection.add(
                # embeddings=[PyEmbedding for e in embeddings],
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Stored {len(news_items)} news items for {asset_key}")
        except Exception as e:
            logger.error(f"Failed to store news items: {e}")
            raise
    
    def search_relevant_news(
        self, 
        query: str, 
        asset_keys: Optional[List[str]] = None,
        days_back: int = 7,
        limit: int = 10
    ) -> List[Dict]:
        try:
            query_embedding = self.embeddings.embed_query(query)
            cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            formatted_results = []

            if asset_keys:
                for asset_key in asset_keys:
                    where_clause = {  # one where clause per asset_key in chroma
                        "asset_key": asset_key
                    }
                    results = self.news_collection.query(
                        query_embeddings=[query_embedding],
                        n_results=limit,
                        where=where_clause
                    )
                    docs = results.get('documents') or [[]]
                    metadatas = results.get('metadatas') or [[]]
                    distances = results.get('distances') or [[]]
                    for i, doc in enumerate(docs):
                        metadata = metadatas[0][i] if metadatas and metadatas[0] and i < len(metadatas[0]) else None
                        distance = distances[0][i] if distances and distances[0] and i < len(distances[0]) else 0
                        if not metadata:
                            continue
                        stored_at = metadata.get("stored_at")
                        if not isinstance(stored_at, str):
                            continue
                        try:
                            stored_at_dt = datetime.fromisoformat(stored_at)
                            cutoff_dt = datetime.fromisoformat(cutoff_date)
                            if stored_at_dt < cutoff_dt:
                                continue
                        except Exception:
                            continue
                        formatted_results.append({
                            "document": doc,
                            "metadata": metadata,
                            "relevance_score": 1 - distance
                        })
            else:
                where_clause = {}
                results = self.news_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where=where_clause
                )
                docs = results.get('documents') or [[]]
                metadatas = results.get('metadatas') or [[]]
                distances = results.get('distances') or [[]]
                for i, doc in enumerate(docs):
                    metadata = metadatas[0][i] if metadatas and metadatas[0] and i < len(metadatas[0]) else None
                    distance = distances[0][i] if distances and distances[0] and i < len(distances[0]) else 0
                    if not metadata:
                        continue
                    stored_at = metadata.get("stored_at", "")
                    if not isinstance(stored_at, str) or stored_at < cutoff_date:
                        continue
                    formatted_results.append({
                        "document": doc,
                        "metadata": metadata,
                        "relevance_score": 1 - distance
                    })

            logger.info(f"Found {len(formatted_results)} relevant news items")
            return formatted_results[:limit]  # limit total after merging

        except Exception as e:
            logger.error(f"Failed to search news: {e}")
            return []
    
    def store_analysis_result(self, analysis_result: Dict, portfolio_hash: str):
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
                "confidence": analysis_result.get('confidence', 0.0),
            }
            metadata = {k: VectorStore._clean_value(v) for k, v in metadata.items()}

            embedding = self.embeddings.embed_query(doc_text)
            analysis_id = f"analysis_{portfolio_hash}_{int(datetime.now().timestamp())}"
            self.analysis_collection.add(
                embeddings=[embedding],
                documents=[doc_text],
                metadatas=[metadata],
                ids=[analysis_id],
            )
            logger.info(f"Stored analysis result: {analysis_id}")
        except Exception as e:
            logger.error(f"Failed to store analysis result: {e}")
    
    def get_portfolio_history(self, portfolio_hash: str, days_back: int = 30) -> List[Dict]:
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            results = self.analysis_collection.query(
                query_embeddings=None,
                n_results=50,
                where={
                    "portfolio_hash": portfolio_hash,
                    "timestamp": {"$gte": cutoff_date}
                }
            )
            
            history = []
            if results['metadatas']:
                for metadata in results['metadatas'][0]:
                    history.append(metadata)
            
            return sorted(history, key=lambda x: x['timestamp'], reverse=True)
        
        except Exception as e:
            logger.error(f"Failed to get portfolio history: {e}")
            return []