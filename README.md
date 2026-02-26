# Dronacharya Group of Institutions Chatbot

A Flask-based chatbot application for Dronacharya Group of Institutions using Google Gemini AI.

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
   - `GOOGLE_API_KEY`: Your Gemini API key
   - `MODEL_NAME`: (Optional) Model to use
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
