import uuid
import datetime
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, jsonify, flash,
    Response
)
from app.blueprints.utils import login_required
from app.db.client import get_service_client
from app.services.claude import reflect_on_entry, MOODS, LANGUAGES
from app.services.elevenlabs import synthesize_speech, VOICES, VOICE_SETS, generate_voice_preview, get_voices_for_language

journal_bp = Blueprint("journal", __name__)


@journal_bp.route("/")
@journal_bp.route("/write")
@login_required
def write():
    return render_template(
        "journal/write.html",
        moods=MOODS,
        languages=LANGUAGES,
    )


@journal_bp.route("/entry", methods=["POST"])
@login_required
def submit_entry():
    db      = get_service_client()
    user_id = session["user_id"]

    entry_text = request.json.get("entry_text", "").strip()
    mood       = request.json.get("mood", "").strip()
    language   = request.json.get("language", "English").strip()
    voice_key  = request.json.get("voice_key", "sarah").strip()

    if not entry_text:
        return jsonify({"error": "Please write something before submitting."}), 400
    if not mood:
        return jsonify({"error": "Please select a mood."}), 400
    if len(entry_text) < 10:
        return jsonify({"error": "Entry is too short. Write a little more."}), 400

    try:
        # 1. Claude writes the reflection
        reflection = reflect_on_entry(entry_text, mood, language)

        # 2. Resolve voice — use voice_key from request,
        #    fall back to profile preference, then default
        voice_id = VOICES.get(voice_key, VOICES["sarah"])["id"]

        # 3. ElevenLabs synthesizes
        audio_bytes = synthesize_speech(reflection, language, voice_id)

        # 4. Upload audio to Supabase Storage
        entry_id  = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        path      = f"journal/{user_id}/{timestamp}_{entry_id}.mp3"

        db.storage.from_("audio").upload(
            path,
            audio_bytes,
            {"content-type": "audio/mpeg", "upsert": "true"},
        )

        # 5. Signed URL valid for 24 hours
        signed    = db.storage.from_("audio").create_signed_url(path, 86400)
        audio_url = signed["signedURL"]

        # 6. Save entry to DB
        db.table("journal_entries").insert({
            "id":         entry_id,
            "user_id":    user_id,
            "entry_text": entry_text,
            "mood":       mood,
            "reflection": reflection,
            "audio_path": path,
            "language":   language,
        }).execute()

        return jsonify({
            "success":    True,
            "reflection": reflection,
            "audio_url":  audio_url,
            "mood":       mood,
        })

    except Exception as e:
        print("JOURNAL ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


@journal_bp.route("/history")
@login_required
def history():
    db      = get_service_client()
    user_id = session["user_id"]

    entries = (
        db.table("journal_entries")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    ).data

    # Generate fresh signed URLs for each entry's audio
    for entry in entries:
        if entry.get("audio_path"):
            try:
                signed = db.storage.from_("audio").create_signed_url(
                    entry["audio_path"], 3600
                )
                entry["audio_url"] = signed["signedURL"]
            except Exception:
                entry["audio_url"] = None

    return render_template("journal/history.html", entries=entries)


@journal_bp.route("/entry/<entry_id>/delete", methods=["POST"])
@login_required
def delete_entry(entry_id: str):
    db      = get_service_client()
    user_id = session["user_id"]

    result = (
        db.table("journal_entries")
        .select("audio_path")
        .eq("id", entry_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    entry = result.data
    if entry and entry.get("audio_path"):
        try:
            db.storage.from_("audio").remove([entry["audio_path"]])
        except Exception:
            pass

    db.table("journal_entries").delete()\
        .eq("id", entry_id)\
        .eq("user_id", user_id)\
        .execute()

    flash("Entry deleted.", "success")
    return redirect(url_for("journal.history"))


@journal_bp.route("/voice-preview/<voice_key>")
@login_required
def voice_preview(voice_key: str):
    if voice_key not in VOICES:
        return jsonify({"error": "Unknown voice."}), 400

    try:
        language    = request.args.get("language", "English")
        voice_id    = VOICES[voice_key]["id"]
        audio_bytes = generate_voice_preview(voice_id, language)

        return Response(
            audio_bytes,
            mimetype="audio/mpeg",
            headers={"Content-Disposition": "inline"},
        )
    except Exception as e:
        print("PREVIEW ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


@journal_bp.route("/save-voice", methods=["POST"])
@login_required
def save_voice():
    """
    Save the user's preferred voice ID to their profile.
    Called automatically when they click a voice card.
    """
    voice_key = request.json.get("voice_key", "sarah")

    if voice_key not in VOICES:
        return jsonify({"error": "Unknown voice."}), 400

    db       = get_service_client()
    user_id  = session["user_id"]
    voice_id = VOICES[voice_key]["id"]

    db.table("profiles").update({
        "preferred_voice": voice_id
    }).eq("id", user_id).execute()

    session["preferred_voice"] = voice_id

    return jsonify({"success": True, "voice_id": voice_id})

@journal_bp.route("/voices-for-language/<language>")
@login_required
def voices_for_language(language: str):
    """Return the 4 voice options for a given language as JSON."""
    voices = get_voices_for_language(language)
    return jsonify(voices)