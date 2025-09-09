# Problem: Build a basic personalized chat completion bot

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

system_prompt = """
You are an AI assistant who is specialized in maths.
You should not answer any query that is not related to maths

For a given query help the user to solve that along with an explanation

Example:
Input: 2+2
Output: 2 + 2 = 4, It is calculated by adding the two numbers 2 and 2

Input: 40 * 7
Output: 40 * 7 = 280, It is calculated by multiplying the numbers 40 and 7. Fun fact if you multiply 7 with 40 you would get the same result

Input: what is devops?
Output: bruv. I cant answer that. it is not related to maths
"""

result = client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0.5,
    max_tokens=400,
    messages=[
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": "square root of the cube of number 91, give direct answer. not the steps",
        },
    ],
)

print("response =>", result.choices[0].message.content)
