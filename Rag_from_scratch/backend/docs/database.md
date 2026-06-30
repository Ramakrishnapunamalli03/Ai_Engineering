# Retrieval Augmented Generation

RAG stands for Retrieval-Augmented Generation.

RAG combines document retrieval with large language models.

The ingestion pipeline consists of:

1. Read documents
2. Chunk documents
3. Generate embeddings
4. Store embeddings in a vector database

During querying:

1. User asks a question.
2. The query is converted into an embedding.
3. Similar chunks are retrieved.
4. The LLM answers using the retrieved context.