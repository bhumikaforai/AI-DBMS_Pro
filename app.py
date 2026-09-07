import os
import datetime
import random
import re
from functools import wraps
from flask import Flask, request, jsonify, render_template_string, render_template, redirect, url_for, session, flash
from dotenv import load_dotenv

import db

# Load environment configuration
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = os.getenv("SECRET_KEY", "college_assistant_secret_key_2026_super_secure")

# Initialize MySQL database & tables safely (won't crash serverless cold start if env vars are pending)
try:
    db_ready, db_status = db.init_db()
except Exception as _init_err:
    db_ready, db_status = False, str(_init_err)
    print(f"[WARN] Database initialization deferred: {_init_err}")


# =========================================================
# AUTHENTICATION DECORATOR & HELPERS
# =========================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access the AI College Assistant.", "info")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# =========================================================
# COLLEGE ASSISTANT KNOWLEDGE BASE
# =========================================================

knowledge = {
    "aiml": """🤖 AIML stands for Artificial Intelligence and Machine Learning.

Artificial Intelligence (AI) means making computers perform tasks that normally require human intelligence.

Machine Learning (ML) is a part of AI where computers learn patterns from data.

Examples:
• Chatbots
• Recommendation systems
• Face recognition
• Spam detection
• Voice assistants

Simple example:
If we give a machine many pictures of cats and dogs, it can learn to identify whether a new picture is a cat or dog.""",

    "python": """🐍 Python is a high-level, interpreted and beginner-friendly programming language.

Why Python is popular:
• Easy syntax
• Large library support
• Used in AI and ML
• Used in web development
• Used in automation
• Used in data science

Example:

name = "Student"
print("Hello", name)

Output:
Hello Student""",

    "java": """☕ Java is a high-level, object-oriented programming language.

Important features:
• Object Oriented
• Platform Independent
• Secure
• Robust
• Multithreaded

Basic example:

class Main {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}""",

    "dbms": """🗄️ DBMS stands for Database Management System.

A DBMS is software used to store, organize, manage and retrieve data.

Examples:
• MySQL
• Oracle
• PostgreSQL
• SQL Server

Important concepts:
• Tables
• Primary Key
• Foreign Key
• SQL
• Normalization
• Transactions
• Relationships""",

    "os": """💻 Operating System is system software that manages computer hardware and software.

Examples:
• Windows
• Linux
• macOS
• Android

Main functions:
• Process Management
• Memory Management
• File Management
• Device Management
• Security
• Resource Management""",

    "dsa": """📊 DSA stands for Data Structures and Algorithms.

Data Structure is a way to organize data.

Examples:
• Array
• Linked List
• Stack
• Queue
• Tree
• Graph
• Hash Table

Algorithm is a step-by-step procedure used to solve a problem.

Example:
Binary Search is an efficient algorithm for searching in a sorted array.""",

    "html": """🌐 HTML stands for HyperText Markup Language.

HTML is used to create the structure of web pages.

Example:

<!DOCTYPE html>
<html>
<head>
    <title>My Page</title>
</head>
<body>
    <h1>Hello Student</h1>
</body>
</html>""",

    "css": """🎨 CSS stands for Cascading Style Sheets.

CSS is used to design and style HTML pages.

It can control:
• Colors
• Fonts
• Spacing
• Layout
• Animations
• Responsive design

Example:

body {
    background: blue;
    color: white;
}""",

    "javascript": """⚡ JavaScript is a programming language mainly used to make websites interactive.

It can:
• Handle button clicks
• Validate forms
• Change HTML
• Create animations
• Communicate with servers

Example:

let name = "Student";
console.log("Hello " + name);""",

    "ai": """🧠 Artificial Intelligence is a branch of computer science that focuses on creating systems capable of performing tasks that normally require human intelligence.

Examples:
• Chatbots
• Self-driving systems
• Image recognition
• Speech recognition
• Recommendation systems

AI includes areas such as Machine Learning, Deep Learning, Natural Language Processing and Computer Vision.""",

    "machine learning": """🤖 Machine Learning is a branch of Artificial Intelligence.

Instead of explicitly programming every rule, we provide data and allow the computer to learn patterns.

Three common types:
1. Supervised Learning
2. Unsupervised Learning
3. Reinforcement Learning

Example:
Email spam detection can use Machine Learning to identify spam messages.""",

    "project": """📝 For a college project, you can follow these steps:

1. Select a problem
2. Define objectives
3. Research existing solutions
4. Choose technologies
5. Design the system
6. Implement the project
7. Test the project
8. Prepare documentation
9. Prepare presentation
10. Prepare viva questions

Example project:
AI College Assistant using Python, Flask & MySQL.""",

    "study plan": """📚 STUDY PLAN

Morning:
• 1 hour theory
• 30 minutes revision

Afternoon:
• 1 hour practical/coding
• 30 minutes problem solving

Evening:
• 1 hour important questions
• 30 minutes revision

Night:
• Revise today's topics
• Prepare tomorrow's goals

Tip:
Study in small sessions and take short breaks. 🎯"""
}


# =========================================================
# CALCULATOR
# =========================================================

def calculate(expression):
    expression = expression.replace("calculate", "").strip()
    if not expression:
        return None
    if not re.fullmatch(r"[0-9+\-*/().% ]+", expression):
        return None
    try:
        return eval(expression, {"__builtins__": None}, {})
    except Exception:
        return None


# =========================================================
# CHATBOT ENGINE
# =========================================================

def generate_reply(message, current_user_name=None):
    original = message.strip()
    text = original.lower()

    # Name memory
    name_match = re.search(
        r"(?:my name is|i am|i'm)\s+([a-zA-Z]+)",
        original,
        re.IGNORECASE
    )

    if name_match:
        extracted_name = name_match.group(1).capitalize()
        session["active_chat_name"] = extracted_name
        return f"Nice to meet you, {extracted_name}! 😊\n\nI will remember your name during this conversation."

    active_name = session.get("active_chat_name") or current_user_name

    if (
        "what is my name" in text
        or "do you remember my name" in text
        or "mera naam kya hai" in text
    ):
        if active_name:
            return f"Your name is {active_name}. 😊"
        return "You haven't told me your name yet."

    # Greetings
    if text in ["hi", "hello", "hey", "hii", "helo"]:
        if active_name:
            return f"Hello {active_name}! 👋\n\nHow can I help you with your studies today?"
        return random.choice([
            "Hello! 👋 How can I help you?",
            "Hi there! 😊 What would you like to learn?",
            "Hey! 🤖 Ask me anything about your college studies."
        ])

    if "how are you" in text:
        return "I'm doing great! 🤖✨\nI'm ready to help you study."

    if "time" in text:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}. ⏰"

    if "date" in text or "today" in text or "aaj ki date" in text:
        today = datetime.datetime.now().strftime("%d %B %Y")
        return f"Today's date is {today}. 📅"

    if text.startswith("calculate"):
        result = calculate(original)
        if result is not None:
            return f"🧮 Answer: {result}"
        return "Sorry, I couldn't calculate that.\n\nExample:\ncalculate 25 * 4"

    # Specific knowledge
    if "machine learning" in text:
        return knowledge["machine learning"]
    if "artificial intelligence" in text:
        return knowledge["ai"]
    if "aiml" in text:
        return knowledge["aiml"]
    if "python" in text:
        return knowledge["python"]
    if "java" in text:
        return knowledge["java"]
    if "dbms" in text or "mysql" in text:
        return knowledge["dbms"]
    if "operating system" in text or text == "os":
        return knowledge["os"]
    if "data structure" in text or "algorithm" in text or "dsa" in text:
        return knowledge["dsa"]
    if "html" in text:
        return knowledge["html"]
    if "css" in text:
        return knowledge["css"]
    if "javascript" in text or "java script" in text:
        return knowledge["javascript"]

    # Viva mode
    if "viva" in text:
        return """🎓 VIVA MODE

Question 1:
What is Artificial Intelligence?

Try answering it yourself.
When you are ready, type:
"next question"

I'll give you another viva question."""

    if "next question" in text or "next viva" in text:
        questions = [
            "What is Machine Learning?",
            "What is the difference between AI and ML?",
            "What is a primary key in DBMS?",
            "What is an Operating System?",
            "What is a data structure?",
            "What is inheritance in Java?",
            "What is a Python list?",
            "What is HTML?"
        ]
        return "🎓 Viva Question:\n\n" + random.choice(questions) + "\n\nTake your time and answer it."

    if "college project" in text or "project idea" in text or text == "project":
        return knowledge["project"]

    if "study plan" in text or "study schedule" in text or "padhai plan" in text:
        return knowledge["study plan"]

    if text == "help" or "what can you do" in text or "what can you help" in text:
        return """✨ I CAN HELP YOU WITH

📚 Study & Notes
🤖 Artificial Intelligence
🧠 Machine Learning
🐍 Python
☕ Java
🗄️ DBMS & MySQL
💻 Operating Systems
📊 Data Structures & Algorithms
🌐 HTML / CSS / JavaScript
🎓 Viva Preparation
📝 College Projects
📅 Study Planning
🧮 Basic Calculations

Try asking:
"Explain AIML"
"Teach me Python"
"What is DBMS?"
"Give me viva questions"
"Give me a project idea"
"Calculate 25 * 4"
"Make a study plan"
"""

    if "thank" in text or "thanks" in text or "thx" in text:
        return random.choice([
            "You're welcome! 😊",
            "Happy to help! 🚀",
            "Anytime! Good luck with your studies! 📚"
        ])

    if text in ["bye", "exit", "quit"]:
        return "Goodbye! 👋\n\nAll the best for your studies! 🎓"

    return """🤖 I'm your AI College Assistant.

I work with built-in college knowledge and store your conversations securely in MySQL.

You can ask me about:
📚 AI / AIML
🐍 Python
☕ Java
🗄️ DBMS & MySQL
💻 Operating Systems
📊 DSA
🌐 HTML / CSS / JavaScript
🎓 Viva
📝 Projects
📅 Study Plans
🧮 Calculations

Try:
"Explain Python"
"What is DBMS?"
"Give me viva questions"
"""


# =========================================================
# HTML TEMPLATES (GLASSMORPHISM CYBER-VIOLET THEME)
# =========================================================

COMMON_STYLES = """
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}

body {
    min-height: 100vh;
    background:
        radial-gradient(circle at 15% 20%, rgba(139, 92, 246, 0.45), transparent 45%),
        radial-gradient(circle at 85% 80%, rgba(236, 72, 153, 0.45), transparent 45%),
        linear-gradient(135deg, #0f0c1b, #221541, #130924);
    display: flex;
    justify-content: center;
    align-items: center;
    color: #ffffff;
    padding: 20px;
}

.glass-card {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 28px;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.2);
}

.auth-box {
    width: 100%;
    max-width: 460px;
    padding: 40px 35px;
    animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.auth-header {
    text-align: center;
    margin-bottom: 30px;
}

.auth-logo {
    width: 72px;
    height: 72px;
    margin: 0 auto 16px;
    border-radius: 22px;
    background: linear-gradient(135deg, #8b5cf6, #ec4899);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 38px;
    box-shadow: 0 10px 25px rgba(139, 92, 246, 0.45);
}

.auth-header h2 {
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #ffffff, #d8b4fe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.auth-header p {
    color: #c4b5fd;
    font-size: 13.5px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    font-size: 12.5px;
    font-weight: 600;
    color: #e9d5ff;
    margin-bottom: 8px;
    letter-spacing: 0.3px;
}

.input-wrap {
    position: relative;
    display: flex;
    align-items: center;
}

.input-wrap .icon {
    position: absolute;
    left: 14px;
    font-size: 16px;
    color: #a78bfa;
    pointer-events: none;
}

.input-wrap input {
    width: 100%;
    padding: 13px 14px 13px 44px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 14px;
    color: #ffffff;
    font-size: 14px;
    outline: none;
    transition: all 0.25s ease;
}

.input-wrap input:focus {
    background: rgba(255, 255, 255, 0.14);
    border-color: #a855f7;
    box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.25);
}

.input-wrap input::placeholder {
    color: #9ca3af;
}

.input-wrap .toggle-pwd {
    position: absolute;
    right: 14px;
    background: none;
    border: none;
    color: #c4b5fd;
    cursor: pointer;
    font-size: 14px;
}

.btn-primary {
    width: 100%;
    padding: 14px;
    border: none;
    border-radius: 14px;
    background: linear-gradient(135deg, #7c3aed, #db2777);
    color: #ffffff;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 10px 25px rgba(124, 58, 237, 0.4);
    transition: all 0.25s ease;
    margin-top: 10px;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 30px rgba(124, 58, 237, 0.55);
    background: linear-gradient(135deg, #8b5cf6, #ec4899);
}

.auth-footer {
    text-align: center;
    margin-top: 25px;
    font-size: 13px;
    color: #ddd6fe;
}

.auth-footer a {
    color: #f472b6;
    text-decoration: none;
    font-weight: 600;
    transition: color 0.2s;
}

.auth-footer a:hover {
    color: #fb7185;
    text-decoration: underline;
}

.alert {
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 20px;
    font-size: 13px;
    display: flex;
    align-items: center;
    gap: 10px;
    animation: fadeIn 0.3s ease;
}

.alert-error {
    background: rgba(239, 68, 68, 0.22);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: #fca5a5;
}

.alert-success {
    background: rgba(34, 197, 94, 0.22);
    border: 1px solid rgba(34, 197, 94, 0.4);
    color: #86efac;
}

.alert-info {
    background: rgba(147, 51, 234, 0.22);
    border: 1px solid rgba(147, 51, 234, 0.4);
    color: #d8b4fe;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign In - AI College Assistant</title>
    <style>
        """ + COMMON_STYLES + """
    </style>
</head>
<body>

<div class="glass-card auth-box">
    <div class="auth-header">
        <div class="auth-logo">🤖</div>
        <h2>Welcome Back</h2>
        <p>Sign in to your AI College Assistant account</p>
    </div>

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ 'error' if category == 'error' else ('success' if category == 'success' else 'info') }}">
                    <span>{{ '⚠️' if category == 'error' else ('✅' if category == 'success' else 'ℹ️') }}</span>
                    <span>{{ message }}</span>
                </div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    <form method="POST" action="{{ url_for('login') }}">
        <div class="form-group">
            <label for="identifier">Username or Email</label>
            <div class="input-wrap">
                <span class="icon">👤</span>
                <input type="text" id="identifier" name="identifier" placeholder="Enter username or email" required autofocus>
            </div>
        </div>

        <div class="form-group">
            <label for="password">Password</label>
            <div class="input-wrap">
                <span class="icon">🔒</span>
                <input type="password" id="password" name="password" placeholder="Enter your password" required>
                <button type="button" class="toggle-pwd" onclick="togglePassword('password', this)">👁️</button>
            </div>
        </div>

        <button type="submit" class="btn-primary">Sign In ➤</button>
    </form>

    <div class="auth-footer">
        Don't have an account? <a href="{{ url_for('signup') }}">Sign up here</a>
    </div>
</div>

<script>
function togglePassword(fieldId, btn) {
    const input = document.getElementById(fieldId);
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '🙈';
    } else {
        input.type = 'password';
        btn.textContent = '👁️';
    }
}
</script>

</body>
</html>
"""

SIGNUP_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Account - AI College Assistant</title>
    <style>
        """ + COMMON_STYLES + """
    </style>
</head>
<body>

<div class="glass-card auth-box">
    <div class="auth-header">
        <div class="auth-logo">🎓</div>
        <h2>Create Account</h2>
        <p>Join the AI College Assistant platform</p>
    </div>

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ 'error' if category == 'error' else ('success' if category == 'success' else 'info') }}">
                    <span>{{ '⚠️' if category == 'error' else ('✅' if category == 'success' else 'ℹ️') }}</span>
                    <span>{{ message }}</span>
                </div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    <form method="POST" action="{{ url_for('signup') }}" onsubmit="return validateForm()">
        <div class="form-group">
            <label for="full_name">Full Name</label>
            <div class="input-wrap">
                <span class="icon">📝</span>
                <input type="text" id="full_name" name="full_name" placeholder="e.g. John Doe" required autofocus>
            </div>
        </div>

        <div class="form-group">
            <label for="username">Username</label>
            <div class="input-wrap">
                <span class="icon">👤</span>
                <input type="text" id="username" name="username" placeholder="Choose a unique username" required>
            </div>
        </div>

        <div class="form-group">
            <label for="email">Email Address</label>
            <div class="input-wrap">
                <span class="icon">📧</span>
                <input type="email" id="email" name="email" placeholder="student@college.edu" required>
            </div>
        </div>

        <div class="form-group">
            <label for="password">Password (min 6 characters)</label>
            <div class="input-wrap">
                <span class="icon">🔒</span>
                <input type="password" id="password" name="password" placeholder="Create a strong password" minlength="6" required>
                <button type="button" class="toggle-pwd" onclick="togglePassword('password', this)">👁️</button>
            </div>
        </div>

        <div class="form-group">
            <label for="confirm_password">Confirm Password</label>
            <div class="input-wrap">
                <span class="icon">🔐</span>
                <input type="password" id="confirm_password" name="confirm_password" placeholder="Re-enter your password" required>
                <button type="button" class="toggle-pwd" onclick="togglePassword('confirm_password', this)">👁️</button>
            </div>
        </div>

        <button type="submit" class="btn-primary">Create Account ➤</button>
    </form>

    <div class="auth-footer">
        Already have an account? <a href="{{ url_for('login') }}">Sign in here</a>
    </div>
</div>

<script>
function togglePassword(fieldId, btn) {
    const input = document.getElementById(fieldId);
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '🙈';
    } else {
        input.type = 'password';
        btn.textContent = '👁️';
    }
}

function validateForm() {
    const p1 = document.getElementById('password').value;
    const p2 = document.getElementById('confirm_password').value;
    if (p1 !== p2) {
        alert("Passwords do not match. Please verify.");
        return false;
    }
    return true;
}
</script>

</body>
</html>
"""

CHAT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI College Assistant - Dashboard</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
        }

        body {
            min-height: 100vh;
            background:
                radial-gradient(circle at top left, #8b5cf6, transparent 35%),
                radial-gradient(circle at bottom right, #ec4899, transparent 35%),
                linear-gradient(135deg, #15102b, #30205c);
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            padding: 10px;
        }

        .app {
            width: 95%;
            max-width: 1200px;
            height: 90vh;
            display: flex;
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.20);
            border-radius: 30px;
            overflow: hidden;
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            box-shadow: 0 25px 80px rgba(0,0,0,0.45);
        }

        /* SIDEBAR */
        .sidebar {
            width: 280px;
            padding: 30px 22px;
            background: linear-gradient(180deg, rgba(124,58,237,0.88), rgba(236,72,153,0.65));
            display: flex;
            flex-direction: column;
            border-right: 1px solid rgba(255,255,255,0.12);
        }

        .logo {
            width: 65px;
            height: 65px;
            border-radius: 20px;
            background: rgba(255,255,255,0.20);
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 35px;
            margin-bottom: 16px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }

        .sidebar h2 {
            font-size: 22px;
            margin-bottom: 4px;
        }

        .user-chip {
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(0, 0, 0, 0.22);
            padding: 8px 12px;
            border-radius: 16px;
            margin: 12px 0 16px;
            border: 1px solid rgba(255, 255, 255, 0.12);
        }

        .user-chip-avatar {
            width: 32px;
            height: 32px;
            border-radius: 10px;
            background: linear-gradient(135deg, #ec4899, #8b5cf6);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
        }

        .user-chip-info {
            overflow: hidden;
        }

        .user-chip-name {
            font-size: 12.5px;
            font-weight: 700;
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
        }

        .user-chip-sub {
            font-size: 11px;
            color: #d8b4fe;
        }

        .online {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            width: fit-content;
            background: rgba(0,0,0,0.22);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            margin-bottom: 18px;
        }

        .online span {
            color: #4ade80;
        }

        .features {
            background: rgba(255,255,255,0.12);
            padding: 16px;
            border-radius: 18px;
            line-height: 2.1;
            font-size: 12.5px;
            border: 1px solid rgba(255,255,255,0.1);
        }

        .features h3 {
            margin-bottom: 4px;
            font-size: 13.5px;
        }

        .sidebar-actions {
            margin-top: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .sidebar-btn {
            padding: 11px;
            border: none;
            border-radius: 14px;
            background: rgba(255,255,255,0.16);
            color: white;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.2s;
            text-align: center;
            text-decoration: none;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .sidebar-btn:hover {
            background: rgba(255,255,255,0.25);
            transform: translateY(-2px);
        }

        .btn-logout {
            background: rgba(239, 68, 68, 0.35);
            border: 1px solid rgba(239, 68, 68, 0.4);
        }

        .btn-logout:hover {
            background: rgba(239, 68, 68, 0.6);
        }

        /* CHAT SECTION */
        .chat {
            flex: 1;
            display: flex;
            flex-direction: column;
            min-width: 0;
        }

        .header {
            height: 80px;
            padding: 15px 25px;
            border-bottom: 1px solid rgba(255,255,255,0.12);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .profile {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .avatar {
            width: 50px;
            height: 50px;
            border-radius: 17px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 28px;
            background: linear-gradient(135deg, #8b5cf6, #ec4899);
            box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4);
        }

        .header h1 {
            font-size: 19px;
        }

        .header p {
            color: #cfc7e8;
            font-size: 11px;
            margin-top: 3px;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .header-logout {
            padding: 7px 14px;
            border-radius: 12px;
            background: rgba(239, 68, 68, 0.25);
            border: 1px solid rgba(239, 68, 68, 0.4);
            color: #fca5a5;
            text-decoration: none;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.2s;
        }

        .header-logout:hover {
            background: rgba(239, 68, 68, 0.5);
            color: #ffffff;
        }

        /* CHATBOX */
        .chatbox {
            flex: 1;
            overflow-y: auto;
            padding: 25px;
            display: flex;
            flex-direction: column;
        }

        .message {
            display: flex;
            margin-bottom: 20px;
            animation: appear 0.3s ease;
        }

        .message.user {
            justify-content: flex-end;
        }

        .bubble {
            max-width: 72%;
            padding: 14px 18px;
            border-radius: 18px;
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.12);
            line-height: 1.6;
            font-size: 14px;
            white-space: pre-wrap;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }

        .user .bubble {
            background: linear-gradient(135deg, #7c3aed, #db2777);
            border-bottom-right-radius: 5px;
            box-shadow: 0 6px 20px rgba(124, 58, 237, 0.3);
        }

        .bot .bubble {
            border-bottom-left-radius: 5px;
        }

        .name {
            font-size: 11px;
            color: #d8c9ff;
            margin-bottom: 5px;
            font-weight: bold;
        }

        /* QUICK BUTTONS */
        .quick {
            padding: 0 25px 12px;
        }

        .quick-title {
            font-size: 11.5px;
            color: #bdb3d8;
            margin-bottom: 7px;
            font-weight: 600;
        }

        .buttons {
            display: flex;
            gap: 7px;
            flex-wrap: wrap;
        }

        .buttons button {
            border: 1px solid rgba(255,255,255,0.18);
            background: rgba(255,255,255,0.08);
            color: #eee8ff;
            padding: 8px 14px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 11.5px;
            transition: all 0.2s;
        }

        .buttons button:hover {
            background: rgba(255,255,255,0.22);
            transform: translateY(-2px);
            border-color: rgba(255,255,255,0.3);
        }

        /* INPUT */
        .input-container {
            margin: 0 25px 8px;
            padding: 7px;
            display: flex;
            gap: 8px;
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 18px;
        }

        input#input {
            flex: 1;
            border: none;
            outline: none;
            background: transparent;
            color: white;
            padding: 12px;
            font-size: 14px;
        }

        input#input::placeholder {
            color: #aaa1c4;
        }

        .mic {
            width: 45px;
            border: none;
            border-radius: 13px;
            background: rgba(255,255,255,0.12);
            color: white;
            cursor: pointer;
            font-size: 18px;
            transition: 0.2s;
        }

        .mic:hover {
            background: rgba(255,255,255,0.22);
        }

        .send {
            padding: 0 22px;
            border: none;
            border-radius: 13px;
            background: linear-gradient(135deg, #8b5cf6, #ec4899);
            color: white;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
        }

        .send:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(236, 72, 153, 0.4);
        }

        .footer {
            text-align: center;
            color: #9188aa;
            font-size: 10px;
            padding: 6px;
        }

        @keyframes appear {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media(max-width:768px) {
            .sidebar { display: none; }
            .app { width: 98%; height: 96vh; }
            .bubble { max-width: 88%; }
        }
    </style>
</head>
<body>

<div class="app">

    <!-- SIDEBAR -->
    <div class="sidebar">
        <div class="logo">🤖</div>
        <h2>AI Assistant</h2>

        <!-- USER CHIP -->
        <div class="user-chip">
            <div class="user-chip-avatar">{{ user.full_name[0]|upper if user and user.full_name else 'U' }}</div>
            <div class="user-chip-info">
                <div class="user-chip-name">{{ user.full_name if user else 'Student' }}</div>
                <div class="user-chip-sub">@{{ user.username if user else 'user' }}</div>
            </div>
        </div>

        <div class="online">
            <span>●</span> AI Online • MySQL Connected
        </div>

        <div class="features">
            <h3>✨ I can help with</h3>
            <div>📚 Study & Notes</div>
            <div>💻 Coding Help</div>
            <div>🤖 AIML Knowledge</div>
            <div>🎓 Viva Preparation</div>
            <div>📝 College Projects</div>
            <div>📅 Study Planning</div>
        </div>

        <div class="sidebar-actions">
            <button class="sidebar-btn" onclick="clearChat()">
                🗑 Clear Conversation
            </button>
            <a href="{{ url_for('logout') }}" class="sidebar-btn btn-logout">
                🚪 Sign Out
            </a>
        </div>
    </div>

    <!-- CHAT AREA -->
    <div class="chat">
        <div class="header">
            <div class="profile">
                <div class="avatar">🤖</div>
                <div>
                    <h1>AI College Assistant</h1>
                    <p>Logged in as {{ user.full_name }} (@{{ user.username }})</p>
                </div>
            </div>
            <div class="header-actions">
                <a href="{{ url_for('logout') }}" class="header-logout">Sign Out 🚪</a>
            </div>
        </div>

        <div class="chatbox" id="chatbox">
            <div class="message bot">
                <div class="bubble">
                    <div class="name">🤖 AI Assistant</div>
                    Hello {{ user.full_name }}! 👋

I'm your AI College Assistant, powered by Flask and backed by MySQL.

Ask me anything about your studies, programming (Python, Java, DBMS), viva questions, calculations, or study schedules! 🚀
                </div>
            </div>
        </div>

        <div class="quick">
            <div class="quick-title">⚡ Quick Topics</div>
            <div class="buttons">
                <button onclick="quick('Explain AIML')">🤖 Explain AIML</button>
                <button onclick="quick('Give me Python viva questions')">🐍 Python Viva</button>
                <button onclick="quick('Explain DBMS')">🗄 DBMS</button>
                <button onclick="quick('Give me a study plan')">📚 Study Plan</button>
                <button onclick="quick('calculate 12 * 15')">🧮 Calculator</button>
            </div>
        </div>

        <div class="input-container">
            <button class="mic" onclick="startVoice()" id="mic" title="Voice Input">🎤</button>
            <input id="input" placeholder="Ask your question here..." autocomplete="off">
            <button class="send" onclick="sendMessage()">Send ➤</button>
        </div>

        <div class="footer">
            AI College Assistant • Python + Flask + MySQL Authentication
        </div>
    </div>

</div>

<script>
const input = document.getElementById("input");
const chatbox = document.getElementById("chatbox");

/* SEND MESSAGE */
async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;

    addUser(message);
    input.value = "";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        addBot(data.reply);

        if (!data.error) {
            speak(data.reply);
        }
    } catch(error) {
        addBot("❌ Connection error: " + error.message);
    }
}

/* RENDER USER MESSAGE */
function addUser(text) {
    chatbox.innerHTML += `
        <div class="message user">
            <div class="bubble">
                <div class="name">You</div>
                ${escapeHTML(text)}
            </div>
        </div>
    `;
    scroll();
}

/* RENDER BOT MESSAGE */
function addBot(text) {
    chatbox.innerHTML += `
        <div class="message bot">
            <div class="bubble">
                <div class="name">🤖 AI Assistant</div>
                ${escapeHTML(text)}
            </div>
        </div>
    `;
    scroll();
}

/* QUICK QUESTIONS */
function quick(question) {
    input.value = question;
    sendMessage();
}

/* CLEAR CHAT */
async function clearChat() {
    try {
        await fetch("/clear", { method: "POST" });
    } catch (error) {
        console.log(error);
    }

    chatbox.innerHTML = `
        <div class="message bot">
            <div class="bubble">
                <div class="name">🤖 AI Assistant</div>
                Conversation cleared! 👋 What would you like to learn next?
            </div>
        </div>
    `;
}

/* VOICE INPUT */
function startVoice() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("Voice input works best in Google Chrome.");
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    const micBtn = document.getElementById("mic");
    micBtn.innerHTML = "🔴";

    recognition.start();

    recognition.onresult = function(event) {
        input.value = event.results[0][0].transcript;
        micBtn.innerHTML = "🎤";
        sendMessage();
    };

    recognition.onerror = function() {
        micBtn.innerHTML = "🎤";
    };

    recognition.onend = function() {
        micBtn.innerHTML = "🎤";
    };
}

/* TEXT TO SPEECH */
function speak(text) {
    if ("speechSynthesis" in window) {
        speechSynthesis.cancel();
        // Remove emojis and special markdown-like symbols for clearer voice speech
        const cleanText = text.replace(/[🤖🐍☕🗄💻📊🌐🎨⚡🧠📝📚🎓🧮✨👋😊●]/g, "");
        const speech = new SpeechSynthesisUtterance(cleanText);
        speech.rate = 0.95;
        speech.pitch = 1;
        speechSynthesis.speak(speech);
    }
}

/* ENTER KEY */
input.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

/* SECURITY ESCAPE */
function escapeHTML(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

/* AUTO SCROLL */
function scroll() {
    chatbox.scrollTop = chatbox.scrollHeight;
}
</script>

</body>
</html>
"""


# =========================================================
# ROUTES: AUTHENTICATION
# =========================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not full_name or not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("signup.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("signup.html")

        success, message, user_id = db.register_user(
            username=username,
            email=email,
            full_name=full_name,
            password=password
        )

        if success:
            flash(message, "success")
            return redirect(url_for("login"))
        else:
            flash(message, "error")
            return render_template("signup.html")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        if not identifier or not password:
            flash("Please provide your username/email and password.", "error")
            return render_template("login.html")

        success, message, user_info = db.authenticate_user(identifier, password)

        if success and user_info:
            session.clear()
            session["user_id"] = user_info["id"]
            session["username"] = user_info["username"]
            session["full_name"] = user_info["full_name"]
            session["email"] = user_info["email"]
            session["active_chat_name"] = user_info["full_name"]
            return redirect(url_for("home"))
        else:
            flash(message, "error")
            return render_template("login.html")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("login"))


# =========================================================
# ROUTES: MAIN APPLICATION (PROTECTED)
# =========================================================

@app.route("/")
@login_required
def home():
    user = {
        "id": session.get("user_id"),
        "username": session.get("username"),
        "full_name": session.get("full_name"),
        "email": session.get("email")
    }
    return render_template("chat.html", user=user)


# =========================================================
# API: CHAT & CLEAR
# =========================================================

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "reply": "Please type a question 😊",
            "error": False
        })

    user_id = session.get("user_id")
    user_name = session.get("full_name") or session.get("username")

    # Generate answer
    answer = generate_reply(message, current_user_name=user_name)

    # Save to MySQL chat_history table
    if user_id:
        db.save_chat_message(user_id, "user", message)
        db.save_chat_message(user_id, "assistant", answer)

    return jsonify({
        "reply": answer,
        "error": False
    })


@app.route("/clear", methods=["POST"])
@login_required
def clear():
    session.pop("active_chat_name", None)
    return jsonify({
        "message": "Conversation cleared"
    })


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")

    print()
    print("=" * 55)
    print("[AI COLLEGE ASSISTANT WITH MYSQL AUTHENTICATION]")
    print("=" * 55)
    print(f"[*] MySQL Status: {db_status}")
    print("[*] Auth System: Sign Up & Sign In Enabled")
    print(f"[*] Application URL: http://{host}:{port}")
    print("=" * 55)
    print()

    app.run(host=host, port=port, debug=debug_mode)

