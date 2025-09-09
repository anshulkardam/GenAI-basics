from openai import OpenAI
from dotenv import load_dotenv
import json
import requests
import os

load_dotenv()

client = OpenAI()


def run_command(command):
    os.system(command)


available_tools = {
    "run_command": {
        "fn": run_command,
        "description ": "takes a command from the input and executes it",
    },
}

system_prompt = """
You are an helpful AI Coding Assistant who is specialized only in resolving users coding problems.
You work on start,plan,action and observe mode.
For the given user query and available tools, plan the step by step execution, based on the planning.
select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query
    
    Output JSON Format:
    {{
        "step" : "string",
        "content" : "string",
        "function" : "The name of the function if the step is action",
        "input" : "The input parameter for the function"
    }}
    
    Available Tools:
    - run_command: takes a command from the input and executes it
    
    Example:
    User Query: Can you make a express server with basic CRUD routes and controllers?
    Output: {{"step": "plan","content": "The user is interested in making an express server with basic CRUD operations"}} 
    Output: {{"step": "plan","content": "From the availabe tools i should call run_command"}} 
    Output: {{"step": "action","function": "run_command", "input" :"mkdir server"}} 
    Output: {{"step": "action","function": "run_command", "input" :"cd server"}} 
    Output: {{"step": "action","function": "run_command", "input" :"touch app.ts"}} 
    Output: {{"step": "observe","output": "running command node app.ts , looks like server is working there are no errors."}} 
    Output: {{"step": "output","content": "your server is ready, just run node app.ts or tell me i can run it for you.}} 
"""


messages = [{"role": "system", "content": system_prompt}]

while True:
    query = input(">")
    messages.append({"role": "user", "content": query})

    while True:
        result = client.chat.completions.create(
            model="gpt-4o", response_format={"type": "json_object"}, messages=messages
        )
        parsed_response = json.loads(result.choices[0].message.content)
        messages.append({"role": "assistant", "content": json.dumps(parsed_response)})

        if parsed_response.get("step") == "plan":
            print(f"thinking.. {parsed_response.get("content")}")
            continue

        if parsed_response.get("step") == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            if available_tools.get(tool_name, False) != False:
                output = available_tools.get(tool_name).get("fn")(tool_input)
                messages.append(
                    {
                        "role": "assistant",
                        "content": json.dumps({"step": "observe", "output": output}),
                    }
                )
                continue
        if parsed_response.get("step") == "output":
            print(f"bot: {parsed_response.get("content")}")
            break