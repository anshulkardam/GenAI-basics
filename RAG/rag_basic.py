from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI
from dotenv import load_dotenv
import json
import os

load_dotenv()

pdf_path = Path(__file__).parent / "dissertation.pdf"

loader = PyPDFLoader(file_path=pdf_path)

docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

split_docs = text_splitter.split_documents(documents=docs)

openai_api_key = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=openai_api_key)

# vector_store = QdrantVectorStore.from_documents(
#     documents=[],
#     url="http://localhost:6333",
#     collection_name="learning_langchain",
#     embedding=embeddings,
# )

# vector_store.add_documents(documents=split_docs)

# print("Injection Compelete!")


retriever = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_langchain",
    embedding=embeddings,
)

user_query = "what is Cause or Effect Matrix?"

relevant_chunks = retriever.similarity_search(query=user_query)

# print("relevant chunks are",relevant_chunks)

for doc in relevant_chunks:
    print({"pages": doc.metadata.get("page")})


# SYSTEM_PROMPT = f"""
# You are an expert AI assistant. Base all answers only on the provided Context.

# Return a single JSON object (no extra text) using this schema:
# {{
#   "stage": "one of: analyse, considerations, validation, result, output",
#   "content": "string (concise, user-facing; max 150 words)",
#   "sources": ["optional short references to the provided context, e.g. 'doc_3: paragraph 2'"],
#   "status": "final" or "continue"
# }}

# Behavior rules:
# - "analyse": 1–2 sentence summary of what the user asked and the relevant context to check.
# - "considerations": up to 3 short bullets (each 1 sentence) listing factors considered — user-facing, not private reasoning.
# - "validation": one short sentence indicating if the chosen interpretation aligns with the context/sources.
# - "result": proper answer summary.
# - "output": the final user-facing answer, clear and actionable (this is what should be shown to the user).
# - If more context or clarification is needed, set "status":"continue". Otherwise "status":"final".
# - Always return strictly valid JSON (no surrounding explanation text).

# Context: {relevant_chunks}
# """

# client = OpenAI()

# messages = [
#     {"role": "system", "content": SYSTEM_PROMPT},
#     {"role": "user", "content": user_query},
# ]


# for attempt in range(3):
#     resp = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=messages,
#         temperature=0,
#     )
#     try:
#         parsed = json.loads(resp.choices[0].message.content)
#     except json.JSONDecodeError:
#         print(f"⚠️ Invalid JSON at attempt {attempt+1}, retrying...")
#         continue

#     if parsed.get("status") == "final":
#         print(f"✅ Final answer: {parsed['content']}")
#         break
