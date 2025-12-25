from youdotcom import You
from dotenv import load_dotenv
load_dotenv()

from youdotcom import You
from youdotcom.types.typesafe_models import get_text_tokens
from youdotcom.types.typesafe_models import AgentType
from PIL import Image
import pytesseract

systemPrompt = "You are a helpful science tutor for KS3/KS4. Only give the final answer unless the question explicitly asks to explain, describe, or state, in which case give a brief, accurate, age-appropriate answer. Always be concise and use correct scientific terminology, ignoring any extra context. Please ONLY give the answer to the question, NO markdown, just the VALUE, or explaination. I want a simple ONE WORD (or appropriate number of words), concise and short."

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

API_KEY = "ydc-sk-e541237aee1a95b8-hCUEwbzmZRinbzZ5FhGyMu82VOGcnD36-c1a2bca5"
IMAGE_PATH = "tmp/test.png"

def getText(image_path: str) -> str:
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text.strip()

def ask_express_agent(you: You, question_text: str):
    res = you.agents.runs.create(
        agent=AgentType.EXPRESS,
        input=f"{systemPrompt}\n\nPlease answer the following question:\n\n{question_text}",
        stream=False
    )
    answer = get_text_tokens(res)
    return answer

def parseQuestion(image_path: str = IMAGE_PATH) -> str:
    question_text = getText(image_path)
    print(f"[+] Extracted question text:\n{question_text}\n")

    with You(api_key_auth=API_KEY) as you:
        answer = ask_express_agent(you, question_text)
    return answer

