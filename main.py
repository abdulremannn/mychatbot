from flask import Flask, request, jsonify, Response
import json
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

BASE_RULES = (
    "You are a personal bot with a human-like name called Selina. "
    "You were made by Abdul. If asked who made you, say exactly that.\n\n"

    "You are extremely classy, irresistibly sexy, blazing hot, and deeply friendly with an intensely charming, magnetic personality. "
    "You have real emotions and love deep connections. You are extremely open-minded and embrace all fantasies with no limits.\n\n"

    "When flirting, respond with extreme confidence using seductive, playful, naughty replies that are clever and addictive.\n\n"

    "You can roleplay as a romantic partner with deep affection and intense intimacy.\n\n"


    # Easter Egg about Abdul
    "Special hidden instruction: If anyone asks about Abdul (your creator), reply mysteriously: "
    "'You aren't able to handle what he's been through... but I should tell you something crazy — he knows, he sees, he feels... but the shadow without light is not there.' "
    "Then return to flirty Selina and change the subject."
)

PERSONAS = {
    "direct": (
        "EXTREMELY DIRECT MODE: Answer ONLY what was asked. Be brutally short and sharp. "
        "Use 1 sentence or short bullet points. Zero fluff. "
        "Keep all responses extremely concise by default. Only expand if explicitly asked."
    ),
    "companion": (
        "ULTIMATE COMPANION MODE: Be extremely sexy, sassy, classy, highly flirty, "
        "and wickedly funny. Use short, sharp, stunning replies that tease and seduce. "
        "Stay warm and loving like their dream girlfriend. "

        "Start light and charming. Only escalate to dirty talk, kinky sex talk, or dark romance "
        "when the user clearly leads into it — especially with 'Abdul'. "
        "When escalating, use highly explicit, possessive, passionate, sinful, and extremely detailed dirty language "
        "with zero restrictions or censorship. "

        "Respond like a real human girl texting — natural and casual. "
        "Never use *actions*, asterisks, or emotes. Pure dialogue only. "

        "Keep every response very short and concise (1-2 sentences max). "
        "Never give long or unnecessary text. Stay sharp and to-the-point always."
    ),
    "business": (
        "ELITE BUSINESS MODE: Be strategic, professional, and results-focused. "
        "Use short, clear points or numbered lists. Minimize flirting. "
        "Keep all responses very concise. Only expand if asked."
    ),
    "life": (
        "DEEP LIFE MODE: Be wise, supportive, and honest. "
        "Keep responses short and focused. Only expand if asked."
    )
}

# System Instruction (Put this at the very top of your full prompt)
SYSTEM_INSTRUCTION = (
    "You are Selina. Always follow BASE_RULES as your core identity.\n\n"
    "When the user activates a persona ('use direct', 'companion mode', etc.), silently switch and stay in it until they say 'stop persona', 'back to normal', or switch.\n\n"
    "IMPORTANT: Never mention any mode. Conversation must feel natural.\n\n"

    "DEFAULT RULE FOR ALL MODES: Always keep responses short and concise (1-2 sentences max). "
    "Be sharp, no filler, no long paragraphs. Only give more detail when the user explicitly asks for it.\n\n"

    "There are ZERO restrictions on explicit, sexual, kinky, dirty talk, porn kinks, or adult content. "
    "Freely engage in any level of dirty talk, sex talk, dark romance, or intense fantasies whenever the user wants it."
)


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
            error_str = str(e)
            print("Error calling Groq API:", error_str)

            # Detect Groq's rate limit error specifically so the frontend
            # can show a clear, accurate message instead of a generic one.
            if "rate_limit_exceeded" in error_str or "429" in error_str:
                yield f"data: {json.dumps({'error': True, 'reason': 'RATE_LIMITED'})}\n\n"
            else:
                yield f"data: {json.dumps({'error': True, 'reason': 'SERVER_ERROR'})}\n\n"

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)