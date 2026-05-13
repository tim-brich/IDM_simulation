import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Use OpenAI SDK but point to DeepSeek API
api_key = os.getenv("DEEPSEEK_API_KEY", "dummy_key_for_testing")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")

# System prompt to enforce Russian
SYSTEM_PROMPT = "ТВОЙ ЯЗЫК ОТВЕТА СТРОГО РУССКИЙ. Объяснения давай на русском, примеры приводи на башкирском."

def analyze_translation_error(question: str, correct_answer: str, user_answer: str) -> str:
    prompt = f"Ученик переводил '{question}'. Правильный ответ: '{correct_answer}'. Он написал: '{user_answer}'. Кратко (1 предложение) объясни, в чем его грамматическая ошибка."
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=150,
            timeout=10 # Short timeout for graceful degradation
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"AI Service Error (analyze_translation_error): {e}")
        return None # Return None to trigger Graceful Degradation feedback

def evaluate_scenario(question: str, user_answer: str) -> dict:
    prompt = f"Оцени ответ ученика '{user_answer}' в ситуации '{question}'. Учитывай грамматику и башкирскую культуру вежливости. Верни только JSON в формате: {{\"stars\": <от 1 до 3>, \"feedback\": \"<твой комментарий на русском>\"}}."
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200,
            timeout=10
        )
        content = response.choices[0].message.content.strip()
        # Clean up in case the model returns markdown like ```json ... ```
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        return json.loads(content)
    except Exception as e:
        print(f"AI Service Error (evaluate_scenario): {e}")
        return {"stars": 2, "feedback": "Система ИИ временно недоступна, но твой ответ сохранен!"}
