from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI
from dotenv import load_dotenv
import json
import os
from typing import List


def init_clients():
    print("loading clients..")
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI()
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large", api_key=openai_api_key
    )
    print("clients ready!")
    return client, embeddings


def inject_pdf(pdf_path, embeddings):
    print("injecting pdf..")
    loader = PyPDFLoader(file_path=pdf_path)

    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    split_docs = text_splitter.split_documents(documents=docs)

    vector_store = QdrantVectorStore.from_documents(
        documents=[],
        url="http://localhost:6333",
        collection_name="parallel_query",
        embedding=embeddings,
    )

    vector_store.add_documents(documents=split_docs)

    print("PDF Injection Compelete!")


def format_context(docs):
    context_blocks = []
    for i, doc in enumerate(docs, start=1):
        page = doc.metadata.get("page", "unknown")
        snippet = doc.page_content.strip().replace("\n", " ")
        context_blocks.append(f"doc_{i} (page {page}): {snippet}...")
    return "\n\n".join(context_blocks)


def get_answers(relevant_chunks, user_query, client):

    context = format_context(relevant_chunks)

    # print("context given to context", context)

    SYSTEM_PROMPT = f"""
    You are an expert AI assistant. Base all answers only on the provided Context.

    Return a single JSON object (no extra text) using this schema:
    {{
    "stage": "one of: analyse, considerations, validation, result, output",
    "content": "string (concise, user-facing; max 150 words)",
    "sources": ["optional short references to the provided context, e.g. 'doc_3: paragraph 2'"],
    "status": "final" or "continue"
    }}

    Behavior rules:
    - "analyse": 1–2 sentence summary of what the user asked and the relevant context to check.
    - "considerations": up to 3 short bullets (each 1 sentence) listing factors considered — user-facing, not private reasoning.
    - "validation": one short sentence indicating if the chosen interpretation aligns with the context/sources.
    - "result": proper answer summary.
    - "output": the final user-facing answer, clear and actionable (this is what should be shown to the user).
    - If more context or clarification is needed, set "status":"continue". Otherwise "status":"final".
    - Always return strictly valid JSON (no surrounding explanation text).
    - Do not answer on your own, only answer from the context.
    - If you don’t find the answer in context, return:  {{ "status" : "final" , "content": "I dont know bruv" }}


    Context: {context}
    """

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    for attempt in range(3):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
        )
        try:
            # print("response", resp)
            parsed = json.loads(resp.choices[0].message.content)
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON at attempt {attempt+1}, retrying...")
            continue

        if parsed.get("status") == "final":
            print(f"✅ Final answer: {parsed['content']}")
            break


def rewrite_query(client, user_query) -> List[str]:

    SYSTEM_PROMPT = """
    You are a helpful AI Assistant. 
    Take the user query and rewrite it into 3 different questions. 
    Return the output strictly as a JSON list of strings, nothing else.
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "rewrites_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "questions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 3,
                            "maxItems": 3,
                        }
                    },
                    "required": ["questions"],
                    "additionalProperties": False,
                },
            },
        },
    )

    raw_output = res.choices[0].message.content
    rewrites = json.loads(raw_output)

    user_query_list = rewrites.get("questions")
    print(f"Original User Query: {user_query}")
    print("Rewritten versions:")
    for i, q in enumerate(user_query_list, start=1):
        print(f"{i}. {q}")

    return user_query_list


def retrieve_ranked_docs(embeddings, query_list):
    print("Retrieving Relevant Chunks per Query..")
    retriever = QdrantVectorStore.from_existing_collection(
        url="http://localhost:6333",
        collection_name="parallel_query",
        embedding=embeddings,
    )

    rankings = []  # list of ranked doc_ids per query
    doc_map = {}  # map doc_id -> document

    for i, query in enumerate(query_list):
        chunks = retriever.similarity_search(query=query, k=20)

        ranking = []
        for rank, doc in enumerate(chunks):
            doc_id = f"{doc.metadata.get('page')}::{rank}"  # unique ID per doc
            ranking.append(doc_id)
            doc_map[doc_id] = doc

        rankings.append(ranking)
        print("rankinG=> ", ranking)
        print(f"\n--- Query {i}: {query} ---")
        for doc in chunks:
            print({"page": doc.metadata.get("page")})

    return rankings, doc_map


def rank_fusion(rankings, k=60):
    scores = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def main():
    client, embeddings = init_clients()

    pdf_path = Path(__file__).parent / "rag_practice.pdf"

    # inject_pdf(pdf_path, embeddings)

    user_query = "What is a queue?"

    trick_question = "how good are movies?"

    query_list = rewrite_query(client, user_query)

    # Step 1: get ranked results for each query
    rankings, doc_map = retrieve_ranked_docs(embeddings, query_list)

    print("rankings=> ", rankings)

    # Step 2: fuse the rankings
    fused = rank_fusion(rankings, k=60)

    print("fused=> ", fused)

    # Step 3: pick top N fused docs
    top_docs = [doc_map[doc_id] for doc_id, _ in fused[:3]]

    # Now you can pass fused docs to your answer generator
    get_answers(top_docs, user_query, client)


if __name__ == "__main__":
    main()
