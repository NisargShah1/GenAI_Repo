from simpleeval import simple_eval
from openai import OpenAI
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def calculate_if_needed(prompt: str, model="gpt-4"):
    try:
        if "calculate" in prompt.lower():
            expr = prompt.lower().replace("calculate", "").strip()
            result = simple_eval(expr)
            return result
        else:
            return call_llm(prompt, model)
    except Exception:
        return call_llm(prompt, model)

def call_llm(prompt, model="gpt-4"):
    if model.startswith("gpt"):
        # Use OpenAI
        response = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    else:
        # Use Gemini
        gemini_model = genai.GenerativeModel(model)
        response = gemini_model.generate_content(prompt)
        print(f"gemini : {prompt} {model}")
        print(f"gemini response: {response}")
        return response.text