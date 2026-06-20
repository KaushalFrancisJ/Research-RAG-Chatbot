import json
import re
from groq import Groq
from config import GROQ_API_KEY, EVALUATION_MODEL

EVAL_PROMPT = """You are an evaluation judge for a RAG system.

Given:
- Question: {question}
- Retrieved Context: {context}
- Generated Answer: {answer}

Score the answer on these 2 metrics:

1. Faithfulness (1-5): Is the answer factually grounded in the context?
2. Answer Relevancy (1-5): Does the answer actually address the question?

Respond in this JSON format only:
{{
  "faithfulness": <score>,
  "faithfulness_reason": "<one sentence>",
  "answer_relevancy": <score>,
  "answer_relevancy_reason": "<one sentence>"
}}"""

_client = Groq(api_key=GROQ_API_KEY)


def evaluate(question: str, context: str, answer: str) -> dict:
    prompt = EVAL_PROMPT.format(question=question, context=context, answer=answer)
    response = _client.chat.completions.create(
        model=EVALUATION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},  # Groq supports forced JSON mode
    )
    return json.loads(response.choices[0].message.content)
