# ComicCraft

ComicCraft is an AI-powered comic story creator built with:

- FastAPI
- Jinja2
- Google Gemini
- Hugging Face
- Pillow
- FPDF2
- Pydantic

The application creates a five-panel comic from a user's story idea.

---

# Features

- Story prompt input
- Main character input
- Setting selection
- Story tone selection
- Art style selection
- AI-generated five-panel outline
- AI-generated narration
- AI-generated dialogue
- AI image generation
- Comic preview
- PDF export
- JSON API
- Image testing endpoint
- Health endpoint
- Automated tests

---

# Project Structure

```text
ComicCraft/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── routes.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── gemini_flash.py
│       ├── gemini_pro.py
│       ├── image_generator.py
│       ├── layout_builder.py
│       └── exporters.py
│
├── templates/
│   ├── index.html
│   ├── comic_preview.html
│   ├── export_success.html
│   └── error.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── panels/
│       └── .gitkeep
│
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_services.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── run.py