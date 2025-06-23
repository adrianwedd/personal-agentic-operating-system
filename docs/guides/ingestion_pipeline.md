# Ingestion Pipeline

Run `ingestion/ingest.py` to load Gmail threads or local documents. The script:

1. Loads raw text with LangChain loaders.
2. Splits documents into chunks.
3. Embeds each chunk using the local Ollama model.
4. Stores embeddings and metadata in Qdrant.

Neo4j constraints are installed on first run to keep the PKG consistent.
