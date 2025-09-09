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


def retrieve_unique_docs(embeddings, query_list):
    print("Retrieving Relevant Unique Chunks..")
    retriever = QdrantVectorStore.from_existing_collection(
        url="http://localhost:6333",
        collection_name="parallel_query",
        embedding=embeddings,
    )

    for id, query in enumerate(query_list):
        print("\n")
        chunks = retriever.similarity_search(query=query)
        for doc in chunks:
            print({f"pages for query id: {id} are": doc.metadata.get("page")})
        
        uni

    #     chunks_page_list = list({chunk.metadata.get("page") for chunk in chunks})

    # print("unqiye chinks", unique_chunks)


# def get_answers():

#     SYSTEM_PROMPT = f"""
#     You are an expert AI assistant. Base all answers only on the provided Context.

#     Return a single JSON object (no extra text) using this schema:
#     {{
#     "stage": "one of: analyse, considerations, validation, result, output",
#     "content": "string (concise, user-facing; max 150 words)",
#     "sources": ["optional short references to the provided context, e.g. 'doc_3: paragraph 2'"],
#     "status": "final" or "continue"
#     }}

#     Behavior rules:
#     - "analyse": 1–2 sentence summary of what the user asked and the relevant context to check.
#     - "considerations": up to 3 short bullets (each 1 sentence) listing factors considered — user-facing, not private reasoning.
#     - "validation": one short sentence indicating if the chosen interpretation aligns with the context/sources.
#     - "result": proper answer summary.
#     - "output": the final user-facing answer, clear and actionable (this is what should be shown to the user).
#     - If more context or clarification is needed, set "status":"continue". Otherwise "status":"final".
#     - Always return strictly valid JSON (no surrounding explanation text).

#     Context: {relevant_chunks}
#     """

#     client = OpenAI()

#     messages = [
#         {"role": "system", "content": SYSTEM_PROMPT},
#         {"role": "user", "content": user_query},
#     ]

#     for attempt in range(3):
#         resp = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=messages,
#             temperature=0,
#         )
#         try:
#             parsed = json.loads(resp.choices[0].message.content)
#         except json.JSONDecodeError:
#             print(f"⚠️ Invalid JSON at attempt {attempt+1}, retrying...")
#             continue

#         if parsed.get("status") == "final":
#             print(f"✅ Final answer: {parsed['content']}")
#             break


def main():
    client, embeddings = init_clients()

    pdf_path = Path(__file__).parent / "rag_practice.pdf"

    # inject_pdf(pdf_path, embeddings)

    user_query = "What is a stack ?"

    query_list = rewrite_query(client, user_query)

    retrieve_unique_docs(embeddings, query_list)


if __name__ == "__main__":
    main()
