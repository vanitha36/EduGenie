import google.generativeai as genai

def learning_path(model, topic):
    prompt = f"Create a learning roadmap for {topic}."
    response = model.generate_content(prompt)
    return response.text