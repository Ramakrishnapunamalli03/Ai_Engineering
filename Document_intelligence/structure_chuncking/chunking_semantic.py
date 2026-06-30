"""
Recursive text splitter — splits on natural boundaries (paragraphs, sentences, words).
This is the best default strategy for most use cases.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Target chunk size in characters
    chunk_overlap=200,    # Overlap between chunks (prevents context loss)
    separators=[
        "\n\n",  # First try: split on paragraph breaks
        "\n",    # Then: line breaks
        ". ",    # Then: sentences
        " ",     # Last resort: words
        "",      # Emergency: characters
    ],
)

text = """Chapter 1: Introduction to AI

Artificial intelligence has transformed how we build software.
Modern AI systems use large language models trained on vast datasets.

The key breakthrough was the transformer architecture, introduced in 2017.
This enabled models to process text in parallel rather than sequentially.

Chapter 2: Practical Applications

The most common AI applications today include chatbots, code generation,
and document analysis. Each requires different optimization strategies."""

chunks = splitter.split_text(text)
for i, chunk in enumerate(chunks):
    print(f"\nChunk {i+1} ({len(chunk)} chars):")
    print(chunk[:100] + "...")