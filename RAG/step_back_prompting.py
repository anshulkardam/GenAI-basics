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


def rewrite_query(client, user_query) -> List[str]:
    STEP_BACK_SYSTEM_PROMPT = """
    You are a helpful AI Assistant. 
    Your task is to first create a "step-back" abstraction of the user’s query,
    i.e., a higher-level reformulation that captures its core intent 
    without the surface details.

    Then, based on that abstraction, generate 3 different rewritten versions 
    of the original query. 
    Each rewrite should be natural, distinct, and faithful to the meaning.

    Return the output strictly in JSON with this format:
    {
        "step_back": "<abstraction of query>",
        "questions": ["...", "...", "..."]
    }
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": STEP_BACK_SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "rewrites_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "step_back": {"type": "string"},
                        "questions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 3,
                            "maxItems": 3,
                        },
                    },
                    "required": ["step_back", "questions"],
                    "additionalProperties": False,
                },
            },
        },
    )

    raw_output = res.choices[0].message.content
    rewrites = json.loads(raw_output)

    step_back = rewrites.get("step_back")
    user_query_list = rewrites.get("questions")

    print(f"Original User Query: {user_query}")
    print(f"Step-back abstraction: {step_back}")
    print("Rewritten versions:")
    for i, q in enumerate(user_query_list, start=1):
        print(f"{i}. {q}")

    return user_query_list


def retrieve_unique_docs(embeddings, query_list):
    print("Retrieving Relevant Unique Chunks..")
    retriever = QdrantVectorStore.from_existing_collection(
        url="http://localhost:6333",
        collection_name="parallel_query",
        embedding=embeddings,
    )

    all_query_pages = []  # list of sets, one per query
    all_chunks = []  # store chunks across queries

    for i, query in enumerate(query_list):
        chunks = retriever.similarity_search(query=query)
        pages = {doc.metadata.get("page") for doc in chunks}

        all_query_pages.append(pages)
        all_chunks.extend(chunks)  # flatten and store

        print(f"\n--- Query {i}: {query} ---")
        for doc in chunks:
            print({f"pages for query {i} are": doc.metadata.get("page")})

    # Find pages common across all queries
    print("\nAll pages per query:", all_query_pages)
    common_pages = set.intersection(*all_query_pages)
    print("Common pages:", common_pages)

    # Filter chunks to only those that match common pages
    # unique_chunks = [
    #     doc.page_content
    #     for doc in all_chunks
    #     if doc.metadata.get("page") in common_pages
    # ]

    unique_chunks = [
        doc for doc in all_chunks if doc.metadata.get("page") in common_pages
    ]

    # print("Unique Chunks:", unique_chunks)

    return unique_chunks


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


def main():
    client, embeddings = init_clients()

    pdf_path = Path(__file__).parent / "rag_practice.pdf"

    # inject_pdf(pdf_path, embeddings)

    user_query = "What is a queue?"

    trick_question = "how good are movies?"

    query_list = rewrite_query(client, trick_question)

    unique_chunk_list = retrieve_unique_docs(embeddings, query_list)

    get_answers(unique_chunk_list, trick_question, client)


if __name__ == "__main__":
    main()
