from flask import Flask, render_template, request, jsonify, session
from chatbot.logic import handle_message

app = Flask(__name__)
app.secret_key = "replace-this-with-any-random-string"  # session needs this


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/chat")
def chat():
    data = request.get_json(force=True)
    message = (data.get("message") or "").strip()

    # initialise session state
    session.setdefault("topic", None)
    session.setdefault("word_count", None)
    session.setdefault("notes", [])
    session.setdefault("explain", False)

    reply, state = handle_message(
        message=message,
        topic=session["topic"],
        word_count=session["word_count"],
        notes=session["notes"],
        explain=session["explain"],
    )

    # update session
    session["topic"] = state["topic"]
    session["word_count"] = state["word_count"]
    session["notes"] = state["notes"]
    session["explain"] = state["explain"]

    return jsonify({"reply": reply, "state": state})


if __name__ == "__main__":
    app.run(debug=True)
