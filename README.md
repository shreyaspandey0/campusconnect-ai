# Dronacharya Group of Institutions Chatbot

A Flask-based chatbot application for Dronacharya Group of Institutions using Groq AI (Llama-3).

## Features
- AI-powered chat interface
- Fallback to local data when offline or rate-limited
- Admin dashboard for stats and lead generation
- Responsive UI

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up environment variables in `.env`:
   - `GROQ_API_KEY`: Your Groq API key
   - `DATABASE_URL`: (Optional) PostgreSQL connection string
3. Run the application:
   ```bash
   python app.py
   ```
4. Access the chat at `http://127.0.0.1:5000`

## Structure
- `app.py`: Main application logic.
- `static/`: CSS, JS, and images.
- `templates/`: HTML templates.
- `tests/`: Verification scripts.
- `scripts/`: Utility scripts.
