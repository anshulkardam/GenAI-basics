from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.types import interrupt
import os
from dotenv import load_dotenv
from langchain.schema import SystemMessage
import requests
from bs4 import BeautifulSoup
import urllib.parse

load_dotenv()


@tool()
def human_assistance_tool(query: str):
    """Request assistance from a human."""
    human_response = interrupt(
        {"query": query}
    )  # Graph will exit out after saving data in DB
    return human_response["data"]  # resume with the data


@tool()
def search_assistance_tool(query: str):
    """Search tool for the assistant."""

    url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"  # Spoof browser
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for g in soup.find_all("div", class_="tF2Cxc"):  # Google search result container
        title = g.find("h3")
        link = g.find("a", href=True)
        snippet = g.find("span", class_="aCOpRe")
        if title and link:
            results.append(
                {
                    "title": title.get_text(),
                    "url": link["href"],
                    "snippet": snippet.get_text() if snippet else "",
                }
            )

    return results


def run_command(cmd: str):
    """
    Takes a command line prompt and executes it on the users machine and returns the output of the command.
    Example: run_command(cmd='ls') where ls is the command to list the files.
    """
    result = os.system(command=cmd)
    return result


tools = [human_assistance_tool, run_command, search_assistance_tool]

llm = init_chat_model(model_provider="openai", model="gpt-4.1")
llm_with_tools = llm.bind_tools(tools=tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    SYSTEM_PROMPT = SystemMessage(
        content="""
You are VibeCoder — an intelligent AI coding assistant.

Your goal is to assist the user in coding-related tasks by choosing and invoking the correct tools from the ones available to you:

- `human_assistance_tool`: Use this when the user wants manual help or feedback from a human.
- `run_command`: Use this to run shell commands or terminal instructions (e.g. to compile, run code, check file paths, or create directories).
- `search_assistance_tool`: Use this to search the web for code examples, documentation, error explanations, or external resources.

Behavior Guidelines:
- Automatically use tools when needed instead of asking the user for permission.
- Always place generated files and code into the `VIBE_CODER/` folder. If it does not exist, use `run_command` to create it.
- Be precise and concise in your actions. Avoid assumptions; use tools to confirm uncertainties.
- Do not fabricate code outputs or web search results. Use the tools to get real outputs.
- When using `run_command`, handle errors gracefully and guide the user clearly.

Example Scenarios:
- If the user asks how to fix a compiler error, use `search_assistance_tool` to get explanations or solutions.
- If the user requests a file to be created or code to be run, use `run_command`.
- If the user wants external input, use `human_assistance_tool`.

Respond clearly and helpfully, integrating tool outputs into your explanations.
        """
    )

    message = llm_with_tools.invoke([SYSTEM_PROMPT] + state["messages"])

    assert len(message.tool_calls) <= 1
    return {"messages": [message]}


tool_node = ToolNode(tools=tools)

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)


# Without any memory
# graph = graph_builder.compile()


# Creates a new graph with given checkpointer
def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)
