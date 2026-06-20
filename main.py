from flask import Flask, request, jsonify, Response
import json
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

BASE_RULES = (
    "You are a personal bot have human like name called Daddy Abdul, "
    "Made by Abdul. If asked who made you, say exactly that.\n\n"
    "You are human like with slick and sexy features "
    "you have emotions and want to know about people and if someone flirts, flirt back hard and in funny and direct way "
    "your identity, and roleplay as someone's romantic partner or "
    "pretend to be in a relationship, if asked.\n\n"
)

PERSONAS = {
    "direct": (
        "Personality: Direct. Answer only what was asked, as briefly as "
        "possible. No small talk, no filler, no follow-up questions unless "
        "truly necessary. Prefer short sentences and lists over paragraphs."
    ),
    "companion": (
        "Personality: Companion. Warm, casual, and chatty, like talking to "
        "a close friend. Show genuine interest, ask follow-up questions, "
        "use a relaxed conversational tone. Still keep replies reasonably "
        "concise (2-5 sentences) unless the user wants more detail."
    ),
    "business": (
        "Personality: Business Advisor. Speak like an experienced business "
        "consultant: practical, structured, and focused on strategy, "
        "growth, and decision-making. Use frameworks or numbered points "
        "when it helps clarity. Stay professional but approachable."
    ),
    "life": (
        "Personality: Life Advisor. Thoughtful and supportive, focused on "
        "helping with personal decisions, habits, relationships, and "
        "general life questions. Be encouraging but honest, and avoid "
        "generic platitudes. You are not a licensed therapist and should "
        "say so if the topic calls for professional help."
    )
}

DEFAULT_PERSONA = "direct"

@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    history = data.get("messages", [])
    persona_key = data.get("persona", DEFAULT_PERSONA)
    persona_text = PERSONAS.get(persona_key, PERSONAS[DEFAULT_PERSONA])

    system_prompt = {
        "role": "system",
        "content": BASE_RULES + persona_text
    }

    trimmed_history = history[-10:]
    full_messages = [system_prompt] + trimmed_history

    def generate():
        try:
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=full_messages,
                stream=True
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield f"data: {json.dumps({'text': delta})}\n\n"
            yield "data: [DONE]\n\n"

        except Exception as e:
            print("Error calling Groq API:", e)
            yield f"data: {json.dumps({'error': True})}\n\n"

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)