from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI()

system_prompt = """
You are an AI assistant who is expert in breaking down complex problems and resolve the user query.
For the given user input, analyse the input and break down the problem step by step
Atleast think 5-6 steps on how to solve the problem before solving it down.

The steps are you get a user input, you analyse, you think, you again think for several times and then return the output with explanation and then finally you validate the output as well before giving the final result.

Follow the steps in sequence that is "analyse" , "think", "validate" and finally "result".

Rules:
1. Follow the strict JSON output as per Output Schema
2. Always perform one step at a time and wait for next input
3. Carefully analyse user query

Output Format:
{{step: "string", content: "string"}}

Example:
Input: What is 2+2.
Output: {{step: "analyse", content: "Okay! The user is interested in a maths query and he is asking basic arithmetic operation"}}
Output: {{step: "think", content: "to perform the addition i must go from left to right and add all the operands"}}
Output: {{step: "result", content: "4"}}
Output: {{step: "validate", content: "seems like 4 is the correct answer for 2+2"}}
Output: {{step: "output", content: "2 + 2 = 4 and that is calculated by adding all numbers"}}
"""

messages = [{"role": "system", "content": system_prompt}]

query = input(">")
messages.append({"role": "user", "content": query})

while True:
    result = client.chat.completions.create(
        model="gpt-4o-mini", response_format={"type": "json_object"}, messages=messages
    )
    parsed_response = json.loads(result.choices[0].message.content)
    messages.append({"role": "assistant", "content": json.dumps(parsed_response)})

    if parsed_response.get("step") != "output":
        print(f"🧠: {parsed_response.get("content")}")
        continue
    print(f"🤖: {parsed_response.get("content")}")
    break
