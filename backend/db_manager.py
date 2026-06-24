import os
from typing import List, Dict, Any
from pymilvus import MilvusClient, DataType
from langchain_huggingface import HuggingFaceEmbeddings

from config import DB_PATH, COLLECTION_NAME, EMBEDDING_DIM


class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH, collection_name: str = COLLECTION_NAME):
        self.db_path = db_path
        self.collection_name = collection_name
        self.embedding_dim = EMBEDDING_DIM

        # Instantiate the multilingual embedding model
        print("💡 Booting up Multilingual Embedding Model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

        # Instantiate the Milvus Client
        self.client = MilvusClient(uri=self.db_path)

        # Pull the database from the hard drive into RAM for fast searching
        if self.client.has_collection(self.collection_name):
            print(f"📦 Loading collection '{self.collection_name}' into memory...")
            self.client.load_collection(self.collection_name)

    def initialize_collection(self) -> None:
        """Drops the existing collection and builds a fresh schema with indexing."""
        print(f"🧹 Resetting collection '{self.collection_name}' in Milvus Lite...")
        if self.client.has_collection(self.collection_name):
            self.client.drop_collection(self.collection_name)

        # Build production schema allowing flexible dynamic metadata fields
        schema = self.client.create_schema(auto_id=True, enable_dynamic_field=True)
        schema.add_field("id", DataType.INT64, is_primary=True)
        schema.add_field("vector", DataType.FLOAT_VECTOR, dim=self.embedding_dim)
        schema.add_field("text", DataType.VARCHAR, max_length=4096)

        # Prepare modern similarity metrics
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="FLAT",
            metric_type="COSINE",
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params,
        )
        print(f"✅ Clean collection '{self.collection_name}' successfully created.")

    def insert_documents(self, chunked_documents: List[Any]) -> None:
        """Converts chunked docs into vectors and writes them cleanly with metadata."""
        print(f"📐 Vectorizing {len(chunked_documents)} chunks...")
        texts = [doc.page_content for doc in chunked_documents]
        vectors = self.embeddings.embed_documents(texts)

        print("💾 Bulk writing records to database...")
        data = [
            {
                "vector": vectors[i],
                "text": texts[i],
                # Keeps metadata intact (source file paths, page numbers, etc.)
                **{k: str(v) for k, v in chunked_documents[i].metadata.items()},
            }
            for i in range(len(texts))
        ]

        self.client.insert(collection_name=self.collection_name, data=data)
        print(f"🎉 Database completely built! Loaded {len(data)} vectors.")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Vector searches the index and pulls both text content AND metadata.

        Returns a list of structured dictionaries:
        [{"text": "...", "metadata": {"source": "...", "page": "..."}}]
        """
        query_vector = self.embeddings.embed_query(query)

        # Request all fields to preserve our dynamic metadata columns
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            limit=top_k,
            output_fields=[
                "text", "source"
            ],
        )

        formatted_hits = []
        for hit in results[0]:
            # Extract standard text payload
            text_payload = hit["entity"].get("text", "")

            # Filter out internal database keys to isolate clean metadata
            metadata_payload = {
                k: v
                for k, v in hit["entity"].items()
                if k not in ["text", "vector", "id"]
            }

            formatted_hits.append({"text": text_payload, "metadata": metadata_payload})

        return formatted_hits
