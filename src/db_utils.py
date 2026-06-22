import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv() 


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Environment variable not found: OPENAI_API_KEY")
MODEL = "text-embedding-3-small"


client = OpenAI(api_key=OPENAI_API_KEY)


def get_embedding(text):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=MODEL).data[0].embedding
