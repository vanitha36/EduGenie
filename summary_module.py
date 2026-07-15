import google.generativeai as genai

def summarize_text(model, text):
    prompt = f"Summarize this:\n{text}"
    response = model.generate_content(prompt)
    return response.text