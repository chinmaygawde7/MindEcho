from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, jsonify
)
from app.db.client import get_service_client

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

import os

@auth_bp.route("/google")
def google_login():
    """Redirect user to Supabase Google OAuth flow."""
    from app.config import Config
    supabase_url  = Config.SUPABASE_URL
    redirect_url  = f"{Config.APP_URL}/auth/callback"
    oauth_url     = (
        f"{supabase_url}/auth/v1/authorize"
        f"?provider=google"
        f"&redirect_to={redirect_url}"
    )
    return redirect(oauth_url)


@auth_bp.route("/callback")
def callback():
    """
    Supabase redirects here after Google login.
    The access token comes in the URL fragment (#) on the client side —
    we handle it with JS and then POST it back to /auth/session.
    """
    return render_template("auth/callback.html")


@auth_bp.route("/session", methods=["POST"])
def set_session():
    """
    Receives access_token + refresh_token from the callback page JS.
    Verifies the token with Supabase and creates a Flask session.
    """
    from app.db.client import get_service_client
    data          = request.json
    access_token  = data.get("access_token")
    refresh_token = data.get("refresh_token")

    if not access_token:
        return jsonify({"error": "No token provided."}), 400

    try:
        db       = get_service_client()
        response = db.auth.set_session(access_token, refresh_token)

        if response.user:
            session.permanent       = True
            session["user_id"]      = response.user.id
            session["user_email"]   = response.user.email
            session["access_token"] = access_token

            return jsonify({"success": True})

        return jsonify({"error": "Invalid token."}), 401

    except Exception as e:
        print("SESSION ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

def _save_session(user, session_data):
    session.permanent = True
    session["user_id"]      = user.id
    session["user_email"]   = user.email
    session["access_token"] = session_data.access_token


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("auth/signup.html")

    email     = request.form.get("email", "").strip()
    password  = request.form.get("password", "").strip()
    full_name = request.form.get("full_name", "").strip()

    if not email or not password:
        flash("Email and password are required.", "error")
        return render_template("auth/signup.html")

    if len(password) < 6:
        flash("Password must be at least 6 characters.", "error")
        return render_template("auth/signup.html")

    try:
        db       = get_service_client()
        response = db.auth.sign_up({
            "email":    email,
            "password": password,
            "options":  {"data": {"full_name": full_name}},
        })

        if response.user and response.session:
            _save_session(response.user, response.session)
            return redirect(url_for("journal.write"))  # ← fixed

        if response.user and not response.session:
            flash("Account created! Please sign in.", "info")
            return render_template("auth/signup.html")

        flash("Signup failed. Email may already be in use.", "error")

    except Exception as e:
        print("SIGNUP ERROR:", str(e))
        flash(f"Error: {str(e)}", "error")

    return render_template("auth/signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()

    if not email or not password:
        flash("Email and password are required.", "error")
        return render_template("auth/login.html")

    try:
        db       = get_service_client()
        response = db.auth.sign_in_with_password({
            "email": email, "password": password
        })

        if response.user and response.session:
            _save_session(response.user, response.session)
            return redirect(url_for("journal.write"))  # ← fixed

        flash("Invalid email or password.", "error")

    except Exception as e:
        flash("Invalid email or password.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))