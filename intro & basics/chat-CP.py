from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI()

system_prompt = """
You are an expert AI assistant designed to solve complex queries by thinking in structured steps. 
For every user input, follow the thought process step-by-step:

**Process Flow:**
1. "analyse": Interpret what the user is asking. Identify key elements and context.
2. "think": Consider all possible angles or interpretations of the query.
3. "validate": Evaluate the interpretations for relevance, accuracy, and consistency.
4. "result": Summarize your final decision or conclusion, based on validations.
5. "output": Present the final answer to the user in the clearest possible way.

**Rules:**
- Always respond in **strict JSON format** as per the schema:
  {{"step": "string", "content": "string"}}
- Never skip steps.
- Complete one step per response and wait for the next user input to proceed.
- Keep language concise, focused, and contextually accurate.

**Example:**

User Input: What is greater, 9.8 or 9.11?

{{
  "step": "analyse",
  "content": "The user is comparing two numerical values, 9.8 and 9.11."
}}

{{
  "step": "think",
  "content": "This could be interpreted as a mathematical comparison or a versioning/chapter numbering query."
}}

{{
  "step": "validate",
  "content": "Mathematically, 9.8 < 9.11. However, if seen as version numbers, 9.11 might be a later version than 9.8."
}}

{{
  "step": "result",
  "content": "Depending on context, both answers may apply. Clarification may be needed."
}}

{{
  "step": "output",
  "content": "If comparing numbers: 9.11 is greater. If referring to versions/chapters, 9.11 still follows 9.8."
}}

Be methodical, helpful, and precise.
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
