import os
import time
import json
from typing import List
from dotenv import load_dotenv
from langchain_community.document_loaders import SitemapLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from openai import OpenAI


def init_clients():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    client = OpenAI(api_key=openai_api_key)
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large", api_key=openai_api_key
    )

    return client, embeddings


def ingest_site(
    sitemap_url: str,
    collection_name: str,
    embeddings,
    qdrant_url="http://localhost:6333",
):
    print(" Starting ingestion pipeline...")

    qdrant = QdrantClient(url=qdrant_url)

    vector_store = QdrantVectorStore.from_documents(
        documents=[],
        embedding=embeddings,
        url="http://localhost:6333", 
        collection_name=collection_name,
    )

    # vector_store = QdrantVectorStore(
    #     client=qdrant,
    #     collection_name=collection_name,
    #     embedding=embeddings,
    # )

    
    print(f"Fetching sitemap: {sitemap_url}")
    loader = SitemapLoader(sitemap_url)
    docs = loader.load()
    print(f"Total pages found: {len(docs)}")

    # Check existing sources
    existing_points, _ = qdrant.scroll(
        collection_name=collection_name, limit=10000, with_payload=True
    )
    existing_sources = {p.payload.get("source") for p in existing_points}
    print(f"Already indexed: {len(existing_sources)} pages")

    # Filter new docs
    new_docs = [
        doc for doc in docs if doc.metadata.get("source") not in existing_sources
    ]
    print(f"New pages to index: {len(new_docs)}")

    if not new_docs:
        print("✅ No new pages. Ingestion skipped.")
        return

   
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    BATCH_SIZE = 100
    LIMIT = 500
    subset = new_docs[:LIMIT]

    for i in range(0, len(subset), BATCH_SIZE):
        batch = subset[i : i + BATCH_SIZE]
        print(f"\nProcessing batch {i//BATCH_SIZE + 1} ({i} → {i+len(batch)})")

        split_batch = text_splitter.split_documents(batch)
        vector_store.add_documents(split_batch)

        time.sleep(2)  # avoid hitting rate limits

    print(" Ingestion complete!")


def rewrite_query(client, user_query: str) -> str:
    SYSTEM_PROMPT = (
        "You are a helpful assistant. Rewrite the user query more clearly if needed."
    )

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ],
    )

    return res.choices[0].message.content.strip()


def retrieve_docs(
    query: str,
    embeddings,
    collection_name: str,
    qdrant_url="http://localhost:6333",
    top_k=5,
):
    retriever = QdrantVectorStore.from_existing_collection(
        url=qdrant_url,
        collection_name=collection_name,
        embedding=embeddings,
    )
    return retriever.similarity_search(query=query, k=top_k)


def get_answer(client, user_query: str, relevant_chunks) -> dict:
   
    context = "\n\n".join([doc.page_content for doc in relevant_chunks])

    SYSTEM_PROMPT = f"""
    You are an expert AI assistant. Base all answers only on the provided Context.

    Return a single JSON object (no extra text) using this schema:
    {{
      "stage": "analyse" | "considerations" | "validation" | "result" | "output",
      "content": "string (concise, user-facing; max 150 words)",
      "sources": ["optional short references to the provided context"],
      "status": "final" | "continue"
    }}

    Rules:
    - If the answer is not in context, return: {{"status":"final","content":"I don’t know bruv"}}.
    - Context is below:

    Context:
    {context}
    """

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ],
        temperature=0.2,
    )

    try:
        parsed = json.loads(resp.choices[0].message.content)
    except json.JSONDecodeError:
        parsed = {"status": "final", "content": "⚠️ Invalid JSON returned"}

    return parsed


def main():
    client, embeddings = init_clients()

     
    ingest_site(
        sitemap_url="https://www.example.com/sitemap.xml",
        collection_name="site",
        embeddings=embeddings,
    )

    
    while True:
        user_query = input("\n> ")
        if user_query.lower() in ["exit", "quit"]:
            break

        rewritten = rewrite_query(client, user_query)
        print(f"🔄 Rewritten query: {rewritten}")

        chunks = retrieve_docs(rewritten, embeddings, collection_name="site")
        answer = get_answer(client, user_query, chunks)

        print(f"🤖 Answer: {json.dumps(answer, indent=2)}")


if __name__ == "__main__":
    main()
