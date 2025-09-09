from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from typing import Literal
from openai import OpenAI
# from langfuse.openai import openai
from langsmith.wrappers import wrap_openai
from langsmith import traceable
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

client = wrap_openai(OpenAI())


# Schema
class DetectCallResponse(BaseModel):
    is_question_ai: bool


class CodingCallResponse(BaseModel):
    answer: str


class State(TypedDict):
    user_message: str
    is_coding_question: bool
    ai_message: str


def detect_query(state: State):
    user_message = state.get("user_message")

    SYSTEM_PROMPT = """
    You are an AI Assistant. Your job is to detect if the user's query is related to a coding question or not.
    return the response in specified JSON boolean only
    """

    result = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=DetectCallResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    state["is_coding_question"] = result.choices[0].message.parsed.is_question_ai

    return state

@traceable
def solve_coding_question(state: State):
    user_message = state.get("user_message")

    SYSTEM_PROMPT = """
    You are an AI Assistant. Your job is to resolve the user query based on the coding problem user is facing
    """

    result = client.beta.chat.completions.parse(
        model="gpt-4.1",
        response_format=CodingCallResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    state["ai_message"] = result.choices[0].message.parsed.answer

    return state


def solve_simple_question(state: State):
    user_message = state.get("user_message")

    SYSTEM_PROMPT = """
    You are an AI Assistant. Your job is to chat with the user
    """

    result = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=CodingCallResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    state["ai_message"] = result.choices[0].message.parsed.answer

    return state

def route_edge(
    state: State,
) -> Literal["solve_simple_question", "solve_coding_question"]:

    is_coding_question = state.get("is_coding_question")

    if is_coding_question:
        return "solve_coding_question"
    else:
        return "solve_simple_question"


graph_builder = StateGraph(State)


graph_builder.add_node("detect_query", detect_query)
graph_builder.add_node("solve_coding_question", solve_coding_question)
graph_builder.add_node("solve_simple_question", solve_simple_question)
graph_builder.add_node("route_edge", route_edge)


graph_builder.add_edge(START, "detect_query")

graph_builder.add_conditional_edges("detect_query", route_edge)

graph_builder.add_edge("solve_coding_question", END)

graph_builder.add_edge("solve_simple_question", END)

graph = graph_builder.compile()


def call_graph():

    state = {
        "user_message": "Hello, can you explain to me what is Pydantic Models?",
        "ai_message": "",
        "is_coding_question": False,
    }

    result = graph.invoke(state)

    print("Final Result", result)


call_graph()
