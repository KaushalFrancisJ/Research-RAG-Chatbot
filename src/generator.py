import ollama
from groq import Groq
from config import ENV, GENERATION_MODEL, GROQ_GENERATION_MODEL, OLLAMA_URL, GROQ_API_KEY


def generate(query: str, context: str) -> str:
    prompt = f"Use the context below to answer the question.\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"
    if ENV == "production":
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_GENERATION_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    else:
        client = ollama.Client(host=OLLAMA_URL)
        response = client.chat(model=GENERATION_MODEL, messages=[{"role": "user", "content": prompt}])
        return response['message']['content']
