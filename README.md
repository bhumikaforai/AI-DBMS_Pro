# 🎓 AI College Assistant with MySQL Authentication

A modern, full-stack **AI College Assistant** web application built with **Python (Flask)**, **MySQL**, and a cyber-violet **Glassmorphism UI**. It features secure user authentication (Sign Up, Sign In, Sign Out), session security, chat persistence, voice input/output, and viva practice mode.

---

## 🌟 Key Features

1. **User Authentication & Authorization**:
   - Registration with Full Name, Username, Email, and Password.
   - Hashed password storage using `werkzeug.security` (PBKDF2 SHA-256).
   - Session-based route protection (`@login_required`).

2. **MySQL Database Storage**:
   - Automated database (`college_assistant`) and table creation (`users`, `chat_history`).
   - Saves conversation history associated with authenticated user accounts.

3. **Modern Cyber-Violet Glassmorphism UI**:
   - Modern dark theme with neon purple and pink accents.
   - Glassmorphism UI, smooth transitions, and responsive mobile layout.

4. **Interactive AI Capabilities**:
   - Subject knowledge in AIML, Python, Java, DBMS, MySQL, OS, DSA, Web Development, etc.
   - Viva mode practice questions.
   - Math calculation processing (`calculate 25 * 4`).
   - Voice input (Speech-to-Text) and answer speech synthesis (Text-to-Speech).

---

## 🛠️ Environment Configuration

Copy `.env.example` to `.env` and set your credentials:

```env
# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=college_assistant

# Flask Secret Key
SECRET_KEY=your_secure_random_secret_key
```

---

## 📦 Local Setup & Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**:
   ```bash
   python app.py
   ```
   Open your browser at `http://127.0.0.1:5000`.

---

## 🚀 Cloud Hosting & Deployment

This project includes production-ready configuration for deployment on platforms such as **Render**, **Railway**, **Heroku**, **VPS**, or **AWS**:

1. **WSGI HTTP Server**: `gunicorn` is included in `requirements.txt`.
2. **Procfile**: Standard entrypoint `web: gunicorn app:app` for web host execution.
3. **Environment Variables**: Configure `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`, and `SECRET_KEY` on your cloud host's environment settings.

---

## 📁 Project Structure

```
.
├── app.py              # Flask Application Routes & AI Logic
├── db.py               # MySQL Database Connection & Table Schema Setup
├── requirements.txt    # Python Package Dependencies
├── Procfile            # Deployment Process File
├── .env.example        # Environment Variable Template
├── README.md           # Project Documentation
├── static/
│   ├── css/            # Glassmorphism & Auth Styling
│   └── js/             # Interactive Speech & Chat Logic
└── templates/          # Jinja2 HTML Templates (chat, login, signup)
```
