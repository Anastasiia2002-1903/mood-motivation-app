"""Flask web application for DAFEU - Digital Emotional Support Assistant."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, g, jsonify, redirect, render_template, request, session, url_for

import config
from database.db_manager import DatabaseManager
from database.seed_data import seed_database
from i18n.translations import load_language, t
from services.breathing_service import BreathingService
from services.emotion_service import EmotionService
from services.journal_service import JournalService
from services.motivation_service import MotivationService

app = Flask(__name__)
app.secret_key = "nare-emotional-companion-secret-key"

# Initial setup: create tables and seed once
_init_db = DatabaseManager()
_init_db.connect()
_init_db.create_tables()
if not _init_db.is_seeded():
    seed_database(_init_db)
_init_db.close()


def get_db() -> DatabaseManager:
    """Get a per-request database connection."""
    if "db" not in g:
        g.db = DatabaseManager()
        g.db.connect()
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def get_services():
    db = get_db()
    return EmotionService(db), MotivationService(db), BreathingService(db), JournalService(db)


def get_lang() -> str:
    lang = session.get("lang", config.DEFAULT_LANGUAGE)
    load_language(lang)
    return lang


@app.route("/")
def welcome():
    lang = get_lang()
    return render_template("welcome.html", t=t, lang=lang, config=config)


@app.route("/set-language/<lang>")
def set_language(lang):
    if lang in config.SUPPORTED_LANGUAGES:
        session["lang"] = lang
    return redirect(request.referrer or url_for("welcome"))


@app.route("/emotions")
def emotions():
    lang = get_lang()
    emotion_svc, _, _, _ = get_services()
    all_emotions = emotion_svc.get_all_emotions()
    return render_template("emotions.html", t=t, lang=lang, emotions=all_emotions)


@app.route("/response", methods=["POST"])
def response():
    lang = get_lang()
    emotion_svc, _, _, _ = get_services()

    emotion_id = int(request.form.get("emotion_id", 1))
    intensity = int(request.form.get("intensity", 5))
    notes = request.form.get("notes", "").strip()

    emotion = emotion_svc.get_emotion(emotion_id)
    if not emotion:
        return redirect(url_for("emotions"))

    emotion_svc.log_interaction(emotion_id, intensity, notes)

    empathic_text = emotion_svc.get_empathic_response(emotion_id, lang)
    intensity_note = emotion_svc.get_intensity_note(intensity, lang)

    session["last_emotion_id"] = emotion_id
    session["last_intensity"] = intensity

    return render_template(
        "response.html",
        t=t,
        lang=lang,
        emotion=emotion,
        empathic_text=empathic_text,
        intensity_note=intensity_note,
        intensity=intensity,
    )


@app.route("/motivation")
@app.route("/motivation/<int:filter_id>")
def motivation(filter_id=None):
    lang = get_lang()
    emotion_svc, motivation_svc, _, _ = get_services()

    emotion_id = filter_id or session.get("last_emotion_id")

    all_emotions = emotion_svc.get_all_emotions()
    current_emotion = emotion_svc.get_emotion(emotion_id) if emotion_id else None

    facts = motivation_svc.get_all_facts(emotion_id, lang)
    thoughts = motivation_svc.get_all_thoughts(emotion_id, lang)

    return render_template(
        "motivation.html",
        t=t,
        lang=lang,
        facts=facts,
        thoughts=thoughts,
        emotions=all_emotions,
        current_emotion=current_emotion,
        current_filter_id=emotion_id,
    )


# --- Breathing exercises ---

@app.route("/breathing")
def breathing():
    lang = get_lang()
    _, _, breathing_svc, _ = get_services()
    exercises = breathing_svc.get_all_exercises()
    return render_template("breathing.html", t=t, lang=lang, exercises=exercises)


@app.route("/breathing/<int:exercise_id>")
def breathing_exercise(exercise_id):
    lang = get_lang()
    _, _, breathing_svc, _ = get_services()
    exercise = breathing_svc.get_exercise(exercise_id)
    if not exercise:
        return redirect(url_for("breathing"))
    return render_template("breathing.html", t=t, lang=lang, exercises=None, exercise=exercise)


# --- Journal ---

@app.route("/journal")
def journal():
    lang = get_lang()
    emotion_svc, _, _, journal_svc = get_services()
    entries = journal_svc.get_entries()
    all_emotions = emotion_svc.get_all_emotions()
    return render_template("journal.html", t=t, lang=lang, entries=entries, emotions=all_emotions)


@app.route("/journal/new", methods=["POST"])
def journal_new():
    _, _, _, journal_svc = get_services()

    content = request.form.get("content", "").strip()
    if not content:
        return redirect(url_for("journal"))

    title = request.form.get("title", "").strip()
    emotion_id = request.form.get("emotion_id")
    intensity = request.form.get("intensity")

    journal_svc.create_entry(
        content=content,
        title=title,
        emotion_id=int(emotion_id) if emotion_id else None,
        intensity=int(intensity) if intensity else None,
    )
    return redirect(url_for("journal"))


@app.route("/journal/<int:entry_id>/delete", methods=["POST"])
def journal_delete(entry_id):
    _, _, _, journal_svc = get_services()
    journal_svc.delete_entry(entry_id)
    return redirect(url_for("journal"))


# --- Mood history ---

@app.route("/mood-history")
def mood_history():
    lang = get_lang()
    db = get_db()
    history = db.get_interactions_history(30)
    frequency = db.get_emotion_frequency(30)
    return render_template("mood_history.html", t=t, lang=lang, history=history, frequency=frequency)


@app.route("/api/mood-data")
def mood_data():
    lang = get_lang()
    db = get_db()
    history = db.get_interactions_history(30)
    frequency = db.get_emotion_frequency(30)

    name_key = "name_de" if lang == "de" else "name_en"

    timeline = [
        {
            "date": h["timestamp"],
            "intensity": h["intensity"],
            "emotion": h[name_key],
            "color": h["color"],
        }
        for h in history
    ]

    freq = [
        {"emotion": f[name_key], "count": f["count"], "color": f["color"]}
        for f in frequency
    ]

    return jsonify({"timeline": timeline, "frequency": freq})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
