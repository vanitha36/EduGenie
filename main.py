import os
import google.generativeai as genai
from google.api_core import exceptions

from dotenv import load_dotenv

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ----------------------------------------
# FastAPI App
# ----------------------------------------

app = FastAPI()

# ----------------------------------------
# Gemini Configuration
# ----------------------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

# ----------------------------------------
# Static Files & Templates
# ----------------------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# ----------------------------------------
# Chat History
# ----------------------------------------

history = []

# ----------------------------------------
# Prompt Generator
# ----------------------------------------

def generate_prompt(task, question):

    if task == "Question Answering":

        return f"""
You are EduGenie, an AI Learning Assistant.

Answer ONLY the student's question.

Format:

# Answer

# Key Points

# Real-Life Example

# Summary

Rules:

- Explain in simple English.
- Use headings.
- Use bullet points.
- Do NOT generate quizzes.
- Do NOT generate learning paths.
- Do NOT ask additional questions.

Question:

{question}
"""

    elif task == "Concept Explanation":

        return f"""
You are EduGenie.

Explain the topic like an expert teacher.

Format:

# Introduction

# Detailed Explanation

# Key Concepts

# Applications

# Advantages

# Real-Life Example

# Summary

Topic:

{question}
"""

    elif task == "Quiz Generation":

        return f"""
You are EduGenie, an AI Quiz Generator.

Generate exactly 5 multiple-choice questions based on the given topic.

Instructions:

- Create exactly 5 questions.
- Each question must have 4 options.
- Label the options as A), B), C), and D).
- Mention ONLY one correct answer.
- Give a one-line explanation for the correct answer.
- Keep the questions suitable for students.
- Do NOT generate paragraphs.
- Do NOT generate markdown tables.
- Do NOT generate additional notes.

Use the following format exactly:

Q1: <Question>

A) Option A
B) Option B
C) Option C
D) Option D

Correct Answer: A

Explanation: <One-line explanation>

-----------------------------------

Q2: <Question>

A) Option A
B) Option B
C) Option C
D) Option D

Correct Answer: C

Explanation: <One-line explanation>

-----------------------------------

Repeat the same format until Question 5.

Topic:

{question}
"""

    elif task == "Summarization":

        return f"""
You are EduGenie.

Summarize the following content.

Format:

# Summary

# Important Points

# Key Takeaways

Content:

{question}
"""

    elif task == "Learning Path":

        return f"""
You are EduGenie.

Create a complete learning roadmap.

Include:

# Beginner

# Intermediate

# Advanced

# Projects

# Best Resources

# Timeline

Topic:

{question}
"""

    else:

        return question


# ----------------------------------------
# Home
# ----------------------------------------

@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "history": history
        }
    )


# ----------------------------------------
# Ask EduGenie
# ----------------------------------------

@app.post("/ask")
def ask(
    request: Request,
    task: str = Form(...),
    question: str = Form(...)
):

    question = question.strip()

    if question == "":

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "history": history
            }
        )

    if len(question) > 4000:
        question = question[:4000]

    prompt = generate_prompt(task, question)

    try:

        response = model.generate_content(prompt)

        if response.text:

            answer = response.text.strip()

        else:

            answer = "⚠️ Gemini returned an empty response."

    except exceptions.ResourceExhausted:

        answer = """
# ⚠️ Gemini API Quota Reached

EduGenie is working correctly.

The free Gemini API quota has been exhausted.

Please try one of the following:

• Wait for the quota to reset.

• Create another Gemini API Key.

• Enable billing in Google AI Studio.

"""

    except exceptions.InvalidArgument:

        answer = """
# ❌ Invalid Gemini API Key

Please check your .env file.

Example:

GEMINI_API_KEY=YOUR_API_KEY

Restart the server after updating the API key.
"""

    except Exception as e:

        print(e)

        answer = f"""
# ⚠️ Unexpected Error

{str(e)}

Please try again later.
"""

    history.append(
        {
            "task": task,
            "question": question,
            "answer": answer
        }
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "history": history
        }
    )


# ----------------------------------------
# Clear Chat
# ----------------------------------------

@app.get("/clear")
def clear():

    history.clear()

    return RedirectResponse("/", status_code=303)