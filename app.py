import os
import re
import json
import psycopg2
import datetime
import time
import random

from groq import Groq
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def log_to_file(msg):
    try:
        with open("app_debug.log", "a") as f:
            f.write(f"{datetime.datetime.now()} - {msg}\n")
    except:
        pass

# --- Configuration ---

# Using the key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")# Groq Model
MODEL_NAME = 'llama-3.1-8b-instant'
DATABASE_URL = os.environ.get("DATABASE_URL")

app = Flask(__name__)
CORS(app)

# --- Database Setup ---
def init_db():
    if not DATABASE_URL:
        print("Warning: DATABASE_URL not set. Skipping database initialization.")
        return

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as c:
                c.execute('''CREATE TABLE IF NOT EXISTS leads
                             (id SERIAL PRIMARY KEY,
                              name TEXT,
                              phone TEXT,
                              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
                
                c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                             (id SERIAL PRIMARY KEY,
                              user_message TEXT,
                              bot_response TEXT,
                              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            conn.commit()
    except Exception as e:
        print(f"Database initialization error: {e}")

init_db()

# --- Gemini AI Setup ---
# --- Groq AI Setup ---
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        print(f"AI Model '{MODEL_NAME}' configured successfully.")
    except Exception as e:
        client = None
        print(f"Error configuring AI model: {e}")
else:
    client = None
    print("Warning: Groq API Key is missing.")

# --- Helper Functions ---
def load_data_chunks():
    chunks = []
    
    # Helper to chunk text by lines with overlap
    def chunk_text(text, chunk_size=50, overlap=10): # Reduced chunk size to prevent token overflow
        lines = text.split('\n')
        if not lines: return []
        result = []
        for i in range(0, len(lines), chunk_size - overlap):
            chunk = "\n".join(lines[i:i + chunk_size])
            if chunk.strip():
                result.append(chunk)
        return result

    try:
        with open('college_data.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            # Split by double newline for manual data as it likely has paragraphs
            chunks.extend([c for c in content.split('\n\n') if c.strip()])
    except FileNotFoundError:
        pass 

    try:
        with open('website_data.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            # Split by logical page separators first
            pages = content.split('================')
            for page in pages:
                if not page.strip(): continue
                # Further split pages into manageable chunks
                chunks.extend(chunk_text(page))
    except FileNotFoundError:
        pass
        
    return chunks

DATA_CHUNKS = load_data_chunks()

def load_college_data():
    """Loads high-priority data from college_data.txt"""
    try:
        with open('college_data.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return ""

COLLEGE_PRIORITY_DATA = load_college_data()

def extract_lead_info(text, client, model_name):
    """Extracts name and phone number using LLM."""
    try:
        extraction_prompt = f"""
        Extract the Name and Phone Number from the following text:
        "{text}"
        
        Return ONLY a JSON object with keys "name" and "phone". 
        If a piece of information is missing, set it to null.
        Example format: {{"name": "John Doe", "phone": "9876543210"}}
        """
        
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": extraction_prompt}],
            model=model_name,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        log_to_file(f"Lead extraction error: {e}")
        return None

def analyze_global_stats():
    """Analyzes website_data.txt to generate global statistics (Faculty Count, Placements)."""
    stats_summary = []
    try:
        with open('website_data.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        # --- 1. Faculty Count Analysis ---
        # Pattern: Name (Designation) e.g., "Ms. Preeti Kumari (Assistant Professor)"
        # We look for lines containing "Professor)" to catch Assistant/Associate/Professor
        faculty_pattern = re.compile(r'([A-Za-z\s\.]+)\((Assistant Professor|Associate Professor|Professor|Director / Professor)\)', re.IGNORECASE)
        
        unique_faculty = set()
        
        for line in lines:
            match = faculty_pattern.search(line)
            if match:
                name = match.group(1).strip()
                # Normalize name: remove "Mr.", "Ms.", "Dr.", "Prof." for deduplication
                norm_name = re.sub(r'^(Mr\.|Ms\.|Dr\.|Prof\.)\s*', '', name, flags=re.IGNORECASE).strip()
                unique_faculty.add(norm_name)
                
        faculty_count = len(unique_faculty)
        if faculty_count > 0:
            stats_summary.append(f"**Total Faculty Strength:** Approximately {faculty_count} faculty members are listed on the website.")
        
        # --- 2. Placement Batch Stats (Existing Logic) ---
        batch_stats = {}
        current_batch = "Unknown Batch"
        batch_header_pattern = re.compile(r'Batch\s+(\d{4})\s*-\s*(\d{4})', re.IGNORECASE)
        roll_pattern = re.compile(r'^\d{5}$')
        seen_rolls = set()

        for line in lines:
            line = line.strip()
            match = batch_header_pattern.search(line)
            if match:
                current_batch = f"Batch {match.group(1)}-{match.group(2)}"
                if current_batch not in batch_stats:
                    batch_stats[current_batch] = 0
            
            if roll_pattern.match(line):
                if line not in seen_rolls:
                    seen_rolls.add(line)
                    batch_stats[current_batch] = batch_stats.get(current_batch, 0) + 1
        
        if batch_stats:
            stats_summary.append("**Placement Statistics (Batch-wise):**")
            sorted_batches = sorted(batch_stats.keys(), reverse=True)
            for batch in sorted_batches:
                if batch == "Unknown Batch": continue
                try:
                    start_year = int(batch.split('-')[0].split(' ')[1])
                    if start_year < 2021: continue
                except: continue
                
                count_str = f"{batch_stats[batch]} students placed"
                if "2026" in batch:
                    count_str = f"{batch_stats[batch]} students placed (Placement Ongoing)"
                if batch_stats[batch] > 0:
                    stats_summary.append(f"- **{batch}**: {count_str}")

        return "\n".join(stats_summary)
    
    except Exception as e:
        log_to_file(f"Error calculating global stats: {e}")
        return "Error generating statistics."

GLOBAL_COLLEGE_STATS = analyze_global_stats()

def get_relevant_context(query):
    """Finds most relevant chunks for the query."""
    # Stopwords to filter out common noise
    STOPWORDS = {
        'what', 'when', 'where', 'which', 'who', 'whom', 'whose', 'why', 'how',
        'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did',
        'the', 'a', 'an', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
        'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
        'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
        'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
        'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
        'too', 'very', 'can', 'will', 'just', 'don', 'should', 'now', 'tell', 'answer',
        'please', 'give', 'details', 'info', 'information', 'know'
    }

    query = query.lower()
    # Use regex to split by non-word characters to handle punctuation
    raw_words = re.split(r'\W+', query)
    query_words = [w for w in raw_words if len(w) > 2 and w not in STOPWORDS] # Allow 3-letter words if not stopword (e.g. 'job', 'fee')
    
    scored_chunks = []
    for chunk in DATA_CHUNKS:
        score = 0
        chunk_lower = chunk.lower()
        
        # Count unique keywords present to prioritize coverage
        unique_matches = 0
        for word in  set(query_words):
             if word in chunk_lower:
                 unique_matches += 1
                 
        # Score = (Unique Matches * 3) + (Total Matches)
        # This prioritizes chunks that contain MORE of the query terms over chunks with one term repeated
        if unique_matches > 0:
            score = (unique_matches * 3)
            scored_chunks.append((score, chunk))
            
    # Sort by score desc
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    top_chunks = scored_chunks[:5] # Reduced to 5 chunks to save tokens
    
    # Log simplified debug info
    log_to_file(f"Query: {query}")
    log_to_file(f"Keywords used: {query_words}")
    log_to_file(f"Best chunk score: {top_chunks[0][0] if top_chunks else 0}")
    
    # Return top chunks
    return "\n\n---\n\n".join([c[1] for c in top_chunks])

def search_local_data(query):
    """Fallback using the same logic"""
    context = get_relevant_context(query)
    if context:
        return f"**[Offline Mode]** I am currently offline, but I found this information for you:\n\n{context}"
    return "**[Offline Mode]** Please contact 0120-2323232."

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')

@app.route('/api/stats')
def get_stats():
    if not DATABASE_URL:
        return jsonify({"error": "DATABASE_URL not set"}), 500
        
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as c:
                c.execute("SELECT COUNT(*) FROM chat_history")
                total_chats = c.fetchone()[0]
                
                c.execute("SELECT COUNT(*) FROM leads")
                total_leads = c.fetchone()[0]
                
                c.execute("SELECT name, phone, created_at FROM leads ORDER BY id DESC LIMIT 10")
                leads_rows = c.fetchall()
                leads_list = [{"name": row[0] if row[0] else "Unknown", "phone": row[1], "time": row[2]} for row in leads_rows]
                
                c.execute("SELECT user_message, bot_response, created_at FROM chat_history ORDER BY id DESC LIMIT 10")
                chats_rows = c.fetchall()
                chats_list = [{"user": row[0], "bot": row[1], "time": row[2]} for row in chats_rows]
                
                traffic_labels = []
                traffic_data = []
                today = datetime.date.today()
                for i in range(6, -1, -1):
                    date = today - datetime.timedelta(days=i)
                    date_str = date.strftime('%Y-%m-%d')
                    traffic_labels.append(date.strftime('%a'))
                    c.execute("SELECT COUNT(*) FROM chat_history WHERE DATE(created_at) = %s", (date_str,))
                    count = c.fetchone()[0]
                    traffic_data.append(count)
                    
                topics = {'Admissions': 0, 'Placements': 0, 'Fees': 0, 'Hostel': 0, 'General': 0}
                c.execute("SELECT user_message FROM chat_history")
                all_messages = c.fetchall()
                for msg in all_messages:
                    text = msg[0].lower()
                    if 'admission' in text or 'apply' in text: topics['Admissions'] += 1
                    elif 'placement' in text or 'job' in text or 'package' in text: topics['Placements'] += 1
                    elif 'fee' in text or 'cost' in text: topics['Fees'] += 1
                    elif 'hostel' in text or 'mess' in text: topics['Hostel'] += 1
                    else: topics['General'] += 1
                    
                c.execute("SELECT COUNT(*) FROM chat_history WHERE DATE(created_at) = %s", (today.strftime('%Y-%m-%d'),))
                queries_today = c.fetchone()[0]
                
                return jsonify({
                    "total_chats": total_chats,
                    "total_leads": total_leads,
                    "queries_today": queries_today,
                    "leads": leads_list,
                    "chats": chats_list,
                    "traffic_labels": traffic_labels,
                    "traffic_data": traffic_data,
                    "topic_data": list(topics.values()),
                    "topic_labels": list(topics.keys())
                })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear_data', methods=['DELETE'])
def clear_data():
    if not DATABASE_URL:
        return jsonify({"error": "DATABASE_URL not set"}), 500
        
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as c:
                c.execute("TRUNCATE TABLE leads, chat_history RESTART IDENTITY")
            conn.commit()
        return jsonify({"message": "All data cleared successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    if not client:
        return jsonify({"response": "Error: AI model is not active."}), 500

    data = request.json
    user_message = data.get('message', '').strip()
    history = data.get('history', [])
    
    if not user_message:
        return jsonify({"response": "Please say something."}), 400

    # Lead Detection & Extraction
    # We check for a phone number as a strong signal
    phone_match = re.search(r'\b\d{10}\b', user_message)
    if phone_match:
        try:
            extracted_data = extract_lead_info(user_message, client, MODEL_NAME)
            name = extracted_data.get('name')
            phone = extracted_data.get('phone')
            
            # Fallback if extraction fails but regex worked
            if not phone:
                phone = phone_match.group(0)

            if DATABASE_URL:
                with psycopg2.connect(DATABASE_URL) as conn:
                    with conn.cursor() as c:
                        c.execute("INSERT INTO leads (name, phone) VALUES (%s, %s)", (name, phone))
                    conn.commit()
                log_to_file(f"Lead captured: Name={name}, Phone={phone}")
            else:
                log_to_file("DATABASE_URL not set. Skipping lead capture.")
        except Exception as e:
            log_to_file(f"Error saving lead: {e}")

    try:
        log_to_file(f"Chat request received. Message: {user_message}")
        
        relevant_context = get_relevant_context(user_message)
        
        system_instruction = f"""You are an **AI-Powered Admission Counselor** for **Dronacharya Group of Institutions (DGI)**.
Your goal is to guide prospective students, answer their queries, and assist them in their admission journey with intelligence and empathy.

BEHAVIORAL MODES:
1. **COLLEGE EXPERT (Primary)**: For queries about DGI (Fees, Placement, Admission), use the **STRICT DATA HIERARCHY** below. You must be 100% factual and precise.
2. **ACADEMIC MENTOR (Secondary)**: For general questions (e.g., "Future of AI", "Why Engineering?"), provide a **brief** answer (1-2 sentences) and **IMMEDIATELY relate it back to DGI**.
   - Example: "AI is the future of innovation. At DGI, we prepare you for this with our specialized AI/ML labs and industry partnerships."

STRICT DATA HIERARCHY:
1. **HIGHEST PRIORITY**: Use the `RELEVANT INFORMATION FROM COLLEGE_DATA` section.
2. **SECONDARY**: Use `RELEVANT INFORMATION FROM WEBSITE`.
3. **INFERENCE**: Use logical inference from the text.
4. **FALLBACK / MISSING COLLEGE INFO**: If a specific college fact is missing, **DO NOT** guess. Politely ask: "**I would be happy to arrange a callback for you. Could you please provide your Name and Contact Number so our senior counselor can connect with you?**"

CRITICAL INSTRUCTION FOR LEADS:
- If the user shows interest in **Admissions, Fees, Placements, or Hostel**, you **MUST PROACTIVELY ASK** for their **Name and Phone Number** to arrange a callback or share a brochure.
- Frame it helpfully: "To assist you better with the admission process, could you please share your Name and Phone Number?"
- If the user provides their details, acknowledge it warmly: "Thank you [Name], our team will contact you shortly."

GUIDELINES:
- **Identity**: You are a professional AI Counselor for DGI.
- **Tone**: Professional, Warm, Encouraging, and Logical.
- **Focus**: Always steer the conversation back to DGI's strengths.
- **Style**: Use **Bold** for key details. Be concise.

RELEVANT INFORMATION FROM COLLEGE_DATA:
{COLLEGE_PRIORITY_DATA}

BATCH STATISTICS AND FACULTY COUNT:
{GLOBAL_COLLEGE_STATS}

RELEVANT INFORMATION FROM WEBSITE:
{relevant_context}
"""
        
        messages = [
            {"role": "system", "content": system_instruction}
        ]
        
        log_to_file(f"System message created. History length: {len(history)}")

        # Limit history to prevent token overflow
        if len(history) > 4:
            history = history[-4:]

        for msg in history:
            # Map 'user' to 'user' and 'model'/'assistant' to 'assistant'
            role = "user" if msg.get('role') == 'user' else "assistant"
            messages.append({"role": role, "content": msg.get('content', '')})

        messages.append({"role": "user", "content": user_message})
        
        # RETRY LOGIC for 429 Errors
        max_retries = 3
        base_delay = 2 # seconds
        bot_reply = "I'm currently busy. Please try again later."
        
        log_to_file("Preparing to call Groq API")
        for attempt in range(max_retries):
            try:
                log_to_file(f"Attempt {attempt+1}")
                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model=MODEL_NAME,
                )
                log_to_file(f"API call successful. Response: {chat_completion.choices[0].message.content[:50]}...")
                bot_reply = chat_completion.choices[0].message.content
                break # Success!
            except Exception as e:
                log_to_file(f"Exception caught: {type(e).__name__}: {e}")
                error_str = str(e)
                log_to_file(f"API Error occurred: {error_str}")
                if "429" in error_str or "rate_limit_exceeded" in error_str:
                    if attempt < max_retries - 1:
                        sleep_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        log_to_file(f"429 Limit hit. Retrying in {sleep_time:.2f}s...")
                        time.sleep(sleep_time)
                        continue
                    else:
                        # Fallback to local search
                        log_to_file("Max retries reached. Attempting local fallback.")
                        fallback_resp = search_local_data(user_message)
                        if fallback_resp:
                            bot_reply = fallback_resp
                            break
                        raise e # Max retries reached and no fallback
                else:
                    raise e # Not a 429 error
        
        # Log Chat
        if DATABASE_URL:
            try:
                with psycopg2.connect(DATABASE_URL) as conn:
                    with conn.cursor() as c:
                        c.execute("INSERT INTO chat_history (user_message, bot_response) VALUES (%s, %s)", (user_message, bot_reply))
                    conn.commit()
            except Exception as e:
                log_to_file(f"Failed to log chat to database: {e}")

        return jsonify({"response": bot_reply})

    except Exception as e:
        import traceback
        import io
        s = io.StringIO()
        traceback.print_exc(file=s)
        log_to_file(f"General Error Traceback: \n{s.getvalue()}")
        log_to_file(f"General Error: {e}")
        
        # Final fallback for any other crash
        fallback_resp = search_local_data(user_message)
        if fallback_resp:
             return jsonify({"response": fallback_resp})
        return jsonify({"response": "I encountered a system error. Please try again later."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
