import re

def logical_router(query: str) -> str:
    """Decide route with simple rules."""
    query_lower = query.lower()

    if re.search(r"\b(compare|vs|difference)\b", query_lower):
        return "DECOMPOSE"
    elif query_lower.startswith("what is") or query_lower.startswith("define"):
        return "HYDE"
    elif re.search(r"\b(how|why|steps|process)\b", query_lower):
        return "STEPBACK"
    else:
        return "DIRECT"

# --- Tests
print(logical_router("What is a queue?"))               # HYDE
print(logical_router("iPhone vs Samsung which is better?"))  # DECOMPOSE
print(logical_router("How does recursion work?"))       # STEPBACK
print(logical_router("Explain the partition function in physics"))  # DIRECT


#Semantic Routing

from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# 1. Setup embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 2. Example route categories
ROUTES = {
    "HYDE": ["what is a stack?", "define polymorphism", "explain recursion"],
    "DECOMPOSE": ["compare python and java", "difference between queue and stack"],
    "STEPBACK": ["how does memory allocation work", "why use linked lists"],
    "DIRECT": ["when was Python created", "history of AI"]
}

# 3. Build a FAISS index where each route has example queries
docs = []
metadatas = []
for route, examples in ROUTES.items():
    for ex in examples:
        docs.append(ex)
        metadatas.append({"route": route})

# Store them in FAISS vector DB
db = FAISS.from_texts(docs, embedding=embeddings, metadatas=metadatas)

# 4. Router function
def semantic_router(query: str) -> str:
    """Route query by nearest neighbor in semantic space."""
    results = db.similarity_search(query, k=1)  # top 1 match
    return results[0].metadata["route"]

# --- Tests
print(semantic_router("What is a queue?"))               # HYDE
print(semantic_router("iPhone vs Samsung which is better?"))  # DECOMPOSE
print(semantic_router("How does recursion work?"))       # STEPBACK
print(semantic_router("Tell me the history of Python"))  # DIRECT
