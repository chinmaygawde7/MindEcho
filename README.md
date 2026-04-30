# MindEcho — AI Mental Health Journaling Platform

> A voice-first journaling app that listens, reflects, and speaks back — in your language.

MindEcho lets you write freely about how you're feeling. Claude reads your entry, writes a warm personalised reflection, and ElevenLabs speaks it back to you in a calm voice. Over time, your emotional patterns are tracked and a weekly audio summary is delivered to your inbox every Sunday.

**Live Demo** → `https://mindecho-n0mv.onrender.com`  
**GitHub** → `https://github.com/chinmaygawde7/eleven-labs-app`

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Screenshots](#screenshots)
- [Architecture](#architecture)
- [AI Pipeline](#ai-pipeline)
- [Language Support](#language-support)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Project Structure](#project-structure)

---

## Overview

Mental health journaling apps exist — but none of them talk back. MindEcho combines three AI services into a single emotional support pipeline:

1. **You write** — anything, in any language, as little or as much as you want
2. **Claude reads** — identifies your emotional tone and writes an 80–100 word warm reflection
3. **ElevenLabs speaks** — narrates the reflection in a calm, human voice of your choice

No diagnosis. No advice. Just presence.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, Flask |
| AI — Script | Anthropic Claude (claude-sonnet-4-5) |
| AI — Voice | ElevenLabs Multilingual v2 TTS |
| Database | Supabase (PostgreSQL) |
| File Storage | Supabase Storage |
| Auth | Supabase Auth — Email + Google OAuth |
| Email | Resend |
| Scheduler | APScheduler |
| Deployment | Render |

---

## Features

### Core
- **Voice journaling** — write an entry, hear a spoken reflection within 15 seconds
- **Mood tagging** — 8 mood options (happy, anxious, sad, grateful, angry, calm, numb, overwhelmed)
- **Voice selection** — 4 curated voices per language (2 female, 2 male) with live preview before you commit
- **Multilingual** — 9 languages supported, voice set switches automatically based on language choice
- **Type in English** — Claude translates and writes the reflection natively in the selected language

### History & Insights
- **Entry history** — all past entries with audio playback
- **Calendar filter** — month and week views, days with entries highlighted in mood colour
- **Mood breakdown** — bar chart showing emotional frequency over 30 days
- **30-day heatmap** — colour-coded by mood
- **Streak tracking** — consecutive days journaled

### Delivery
- **Weekly audio summary** — every Sunday at 8am, Claude writes a reflection on your week, ElevenLabs narrates it, Resend delivers the audio link to your inbox
- **Signed audio URLs** — all audio is privately stored with time-limited access links

### Auth & Security
- **Email + Google OAuth** — sign up with either
- **Auto logout** — session expires after 1 day of inactivity, timer resets on every action
- **Row-level privacy** — all data scoped to the authenticated user

---

## Screenshots

### Sign Up / Login
> Google OAuth and email authentication

![Login page](screenshots/login.png)

---

### Onboarding — Choose Language & Voice
> Language selector with dynamic voice set, live audio preview for each voice

![Write page](screenshots/write.png)

---

### Write an Entry
> Mood picker, language hint, free-form text area

![entry page](screenshots/entry.png)

---

### Reflection Player
> Claude's reflection shown in italic, ElevenLabs audio playing automatically

![reflection page](screenshots/reflection.png)

---

### Entry History
> Past entries with calendar filter (month/week view)

![calendar page](screenshots/calendar.png)

---

### Calendar Filter — Month View
> Days with entries highlighted in mood colour, click to filter

![calendar_month page](screenshots/calendar_month.png)

---

### Calendar Filter — Week View
> 7-day row with mood-coloured cells

![calendar_week page](screenshots/calendar_week.png)

---

### Insights Dashboard
> Stats row, mood breakdown bars, 30-day heatmap, weekly summaries


![insights page](screenshots/insights.png)

---

### Weekly Email
> Sunday morning delivery with audio link and written summary


---

## Architecture

```
User Browser
    │
    ├── Write entry → POST /entry
    │       │
    │       ├── Claude API → reflect_on_entry()
    │       │       └── 80–100 word warm reflection in selected language
    │       │
    │       ├── ElevenLabs API → synthesize_speech()
    │       │       └── mp3 bytes in cloned voice persona
    │       │
    │       ├── Supabase Storage → upload mp3
    │       │       └── signed URL (24hr) returned to browser
    │       │
    │       └── Supabase DB → save entry + reflection + audio_path
    │
    ├── View history → GET /history
    │       └── Fresh signed URLs generated per entry (1hr)
    │
    ├── View insights → GET /insights
    │       └── Mood counts, streak, 30-day heatmap from DB
    │
    └── Every Sunday 08:00 UTC — APScheduler fires
            ├── Claude → generate_weekly_summary()
            ├── ElevenLabs → synthesize_speech()
            ├── Supabase Storage → upload weekly mp3
            └── Resend → send_weekly_email() with signed URL
```

---

## AI Pipeline

### Per Entry (on demand)

```python
# 1. Claude writes the reflection
reflection = reflect_on_entry(
    entry_text=user_text,
    mood=selected_mood,
    language="Hindi"
)

# 2. ElevenLabs speaks it
audio_bytes = synthesize_speech(
    text=reflection,
    language="Hindi",
    voice_id=VOICES["rohan"]["id"]   # calm male Hindi voice
)

# 3. Stored privately, signed URL returned
```

### Weekly (automated)

```python
# Every Sunday 08:00 UTC
entries = fetch_last_7_days(user_id)
summary, dominant_mood = generate_weekly_summary(entries, language)
audio   = synthesize_speech(summary, language)
url     = upload_and_sign(audio)
send_weekly_email(user_email, url, summary)
```

---

## Language Support

| Language | Script written by Claude | Voice synthesis | Voice set |
|---|---|---|---|
| English | ✅ Native | ✅ Native (en) | Sarah, Aria, Liam, Charlie |
| Hindi | ✅ Native | ✅ Native (hi) | Aradhya, Neerja, Rohan, Arjun |
| Tamil | ✅ Native | ✅ Native (ta) | Kavya, Meera, Karthik, Vijay |
| Marathi | ✅ Native | ✅ Hindi fallback | Hindi voice set |
| Telugu | ✅ Native | ✅ Hindi fallback | Hindi voice set |
| Kannada | ✅ Native | ✅ Hindi fallback | Hindi voice set |
| Bengali | ✅ Native | ✅ Hindi fallback | Hindi voice set |
| Gujarati | ✅ Native | ✅ Hindi fallback | Hindi voice set |
| Punjabi | ✅ Native | ✅ Hindi fallback | Hindi voice set |

> Users can type in English — Claude translates and writes the reflection natively in the selected language.

---

## Getting Started

### Prerequisites

- Python 3.11+
- A Supabase project
- ElevenLabs Starter plan ($5/month — required for TTS API access)
- Anthropic API key
- Resend account (free tier)

### Installation

```bash
# Clone the repo
git clone https://github.com/chinmaygawde7/eleven-labs-app.git
cd eleven-labs-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file (see Environment Variables below)
cp .env.example .env

# Run locally
python run.py
```

App runs at `http://localhost:5000`

### Supabase Setup

Run the following SQL in your Supabase SQL Editor:

```sql
create table public.profiles (
  id         uuid references auth.users(id) on delete cascade primary key,
  email      text not null,
  full_name  text,
  preferred_voice text default 'EXAVITQu4vr4xnSDxMaL',
  created_at timestamptz default now()
);

create table public.journal_entries (
  id            uuid primary key default uuid_generate_v4(),
  user_id       uuid references public.profiles(id) on delete cascade not null,
  entry_text    text not null,
  mood          text not null,
  reflection    text,
  audio_path    text,
  language      text default 'English',
  created_at    timestamptz default now()
);

create table public.weekly_summaries (
  id            uuid primary key default uuid_generate_v4(),
  user_id       uuid references public.profiles(id) on delete cascade not null,
  week_start    date not null,
  summary_text  text not null,
  audio_path    text,
  dominant_mood text,
  created_at    timestamptz default now()
);
```

Create a private storage bucket named `audio`.

---

## Environment Variables

Create a `.env` file in the project root:

```bash
# Flask
FLASK_SECRET_KEY=your_long_random_secret_key
FLASK_ENV=development

# Supabase
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# ElevenLabs
ELEVENLABS_API_KEY=your_elevenlabs_key

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_key

# Resend
RESEND_API_KEY=your_resend_key

# App
APP_URL=http://localhost:5000
```

---

## Deployment

Deployed on **Render** (free tier).

```bash
# Build command
pip install -r requirements.txt

# Start command
gunicorn run:app --workers 2 --bind 0.0.0.0:$PORT
```

Set all environment variables in Render dashboard → Environment tab. Update `APP_URL` to your Render URL after first deploy.

> **Note:** Free tier on Render sleeps after 15 minutes of inactivity. First request after sleep takes ~30 seconds to respond.

---

## Project Structure

```
eleven-labs-app/
├── app/
│   ├── __init__.py               # App factory, blueprint registration
│   ├── config.py                 # All settings + session config
│   ├── blueprints/
│   │   ├── auth.py               # Login, signup, Google OAuth, logout
│   │   ├── journal.py            # Write entry, history, voice preview
│   │   ├── insights.py           # Mood patterns, heatmap, weekly summaries
│   │   └── utils.py              # login_required decorator
│   ├── services/
│   │   ├── claude.py             # reflect_on_entry(), generate_weekly_summary()
│   │   ├── elevenlabs.py         # synthesize_speech(), voice sets per language
│   │   ├── scheduler.py          # APScheduler weekly job
│   │   └── email.py              # Resend weekly email
│   ├── db/
│   │   └── client.py             # Supabase client singleton
│   └── templates/
│       ├── base.html             # Shared nav + layout
│       ├── auth/                 # login.html, signup.html, callback.html
│       └── journal/              # write.html, history.html, insights.html
├── static/
│   └── css/
│       └── main.css              # All styles
├── flask_session/                # Dev session storage (gitignored)
├── .env                          # Secrets (gitignored)
├── .gitignore
├── render.yaml                   # Render deployment config
├── requirements.txt
└── run.py                        # Entry point
```

---

## Author

**Chinmay Nitin Gawde**  
[GitHub](https://github.com/chinmaygawde7) · [LinkedIn](https://linkedin.com/in/yourprofile)

---

*Built with Flask, Claude, ElevenLabs, and Supabase.*
