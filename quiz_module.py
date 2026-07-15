import google.generativeai as genai

def generate_quiz(model, topic):
    prompt = f"Generate 5 MCQs on {topic}."
    response = model.generate_content(prompt)
    return response.text