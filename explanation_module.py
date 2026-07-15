import google.generativeai as genai

def explain_concept(model, topic):
    prompt = f"Explain {topic} in simple words for students."
    response = model.generate_content(prompt)
    return response.text