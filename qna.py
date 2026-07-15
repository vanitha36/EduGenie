import google.generativeai as genai

def ask_question(model, question):
    response = model.generate_content(question)
    return response.text