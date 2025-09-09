from openai import OpenAI
from dotenv import load_dotenv
import json
import requests
import os

load_dotenv()

client = OpenAI()


def get_weather(city):
    print(f"calling get_weather...", city)
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"the weather in {city} is {response.text} right now"
    return "404 not found"


def add(x, y):
    print(f"tool called... add")
    return x + y


def run_command(command):
    os.system(command)


available_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "Takes a city name as an input and returns the current weather for the city",
    },
    "add": {
        "fn": add,
        "description ": "takes two numbers x and y and returns the sum of the given input that is x+y",
    },
    "run_command": {
        "fn": run_command,
        "description ": "takes a command from the input and executes it",
    },
}

system_prompt = """
You are an helpful AI Assistant who is specialized in resolving user query.
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
    - get_weather: Takes a city name as an input and returns the current weather for the city
    - add : takes two numbers x and y and returns the sum of the given input that is x+y
    - run_command: takes a command from the input and executes it
    
    Example:
    User Query: What is the weather of Bangalore?
    Output: {{"step": "plan","content": "The user is interested in weather data of new york"}} 
    Output: {{"step": "plan","content": "From the availabe tools i should call get_weather"}} 
    Output: {{"step": "action","function": "get_weather", "input" :"bangalore"}} 
    Output: {{"step": "observe","output": "12 degree celcius"}} 
    Output: {{"step": "output","content": "The weather for new york seems to be 12 degrees.}} 
"""


messages = [{"role": "system", "content": system_prompt}]

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
