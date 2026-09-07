# 🎓 AI-DBMS Pro — Intelligent Academic & Database Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Flask-2.x-lightgrey?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/MySQL-8.0+-orange?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/UI-Cyber%20Glassmorphism-purple?style=for-the-badge" alt="Glassmorphism UI" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

---

## 📖 Overview

**AI-DBMS Pro** is a modern, full-stack web application engineered for computer science students, educators, and engineers. It combines an **intelligent academic knowledge engine** with **MySQL database persistence**, **secure session authentication**, and a **cyber-violet glassmorphism dashboard**.

Whether you're mastering **DBMS (Normalization, ACID, Joins, Indexing, SQL queries)**, preparing for **Viva exams**, debugging code in **Python/Java/Web Dev**, or practicing concepts with speech recognition, **AI-DBMS Pro** provides instant, structured, and interactive assistance.

---

## 🌟 Key Features

### 🔐 1. Secure User Authentication
- **Account Registration & Login**: Multi-field registration with username, email, full name, and password validation.
- **Cryptographic Password Hashing**: Utilizes `werkzeug.security` (PBKDF2 SHA-256) to ensure credentials are never stored in plaintext.
- **Session Security**: Protected application routes with `@login_required` decorators and session cleanup on logout.

### 🗄️ 2. Automated MySQL Database Architecture
- **Self-Healing Initializer**: Automatically verifies and provisions the MySQL database (`college_assistant`) and schema upon application launch.
- **Persistent Chat History**: Securely records user prompts and assistant responses associated with foreign-key constrained user accounts.
- **Connection Health Checks**: Dynamic status indicators reflecting live MySQL server health in the UI.

### 📚 3. Academic Knowledge & DBMS Engine
- **Comprehensive DBMS Topics**:
  - Relational Models, Keys (Primary, Foreign, Candidate, Composite, Super)
  - Normalization (1NF, 2NF, 3NF, BCNF)
  - Transactions & ACID Properties (Atomicity, Consistency, Isolation, Durability)
  - SQL Syntax & Query Building (DDL, DML, DQL, DCL, TCL, complex Joins, Group By, Having)
  - Indexing (B-Trees, Hash Indexing, Clustered vs Non-Clustered)
- **Multi-Subject Tutoring**:
  - Artificial Intelligence & Machine Learning (AIML)
  - Python Programming (Syntax, OOP, data structures)
  - Java (Object-oriented concepts, multithreading, collections)
  - Operating Systems & Data Structures
  - Web Development (HTML, CSS, JavaScript)
- **🎯 Viva & Interview Practice Mode**: Simulated viva interview questions with immediate feedback and model answers.
- **🧮 Computational Logic & Math**: Real-time evaluation of mathematical expressions and algorithms.

### 🎙️ 4. Voice Interaction & Modern Glassmorphism UI
- **Speech-to-Text**: Real-time voice query input using the browser's Web Speech Recognition API.
- **Text-to-Speech**: Speech synthesis to speak out explanations and viva responses.
- **Aesthetic UI**: Cyber-violet dark glassmorphism design with frosted-glass containers, glow highlights, animated chips, and code snippet styling.
- **Responsive Layout**: Optimized for desktop, tablet, and mobile with an off-canvas drawer navigation.

---

## 🏗️ Architecture & Tech Stack

```
AI-DBMS_Pro/
│
├── Frontend Layer       HTML5 / Vanilla CSS3 / JavaScript (ES6+) / Web Speech API
│                        Modern Glassmorphism Design System
│
├── Backend Layer        Python 3.x / Flask Framework
│                        Werkzeug Security / Python-dotenv / Gunicorn WSGI
│
└── Database Layer       MySQL Server 8.x / PyMySQL Connector (InnoDB Engine)
                         Tables: users, chat_history
```

---

## 🗃️ Database Schema

```sql
-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    full_name VARCHAR(120) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Chat History Table
CREATE TABLE IF NOT EXISTS chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chat_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+** installed on your system.
- **MySQL Server** (8.0 or compatible / MariaDB) running locally or remotely.
- **Git** installed.

### 1. Clone the Repository
```bash
git clone https://github.com/bhumikaforai/AI-DBMS_Pro.git
cd AI-DBMS_Pro
```

### 2. Set Up a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment configuration:
```bash
# Windows PowerShell
copy .env.example .env

# Linux / macOS / Bash
cp .env.example .env
```

Open `.env` and fill in your database credentials:
```env
# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=college_assistant

# Flask Secret Key
SECRET_KEY=your_secure_random_secret_key_here
```

> **Note**: The application will automatically create the `college_assistant` database and all required tables upon first launch!

### 5. Run the Application
```bash
python app.py
```

Access the application in your browser at:
```
http://127.0.0.1:5000
```

---

## 🌐 Production & Cloud Deployment

The application supports both traditional WSGI containers (**Render**, **Railway**, **Heroku**, **VPS**) and Serverless deployment (**Vercel**):

### Deploying on Vercel
1. **Zero-Config Routing**: Includes `vercel.json` and `api/index.py` for seamless Flask serverless execution.
2. **Configure Environment Variables in Vercel Dashboard**:
   Go to your Project Settings > **Environment Variables** in Vercel and add:
   - `MYSQL_HOST`: Your TiDB Cloud or MySQL host (e.g. `gateway01.ap-southeast-1.prod.aws.tidbcloud.com`)
   - `MYSQL_PORT`: `4000` (or `3306`)
   - `MYSQL_USER`: Your MySQL username
   - `MYSQL_PASSWORD`: Your database password
   - `MYSQL_DB`: `college_assistant`
   - `MYSQL_USE_SSL`: `auto`
   - `SECRET_KEY`: A secure random secret string

### Deploying on Render / Railway / Heroku
1. **WSGI Server**: `gunicorn` is included in `requirements.txt`.
2. **Process File**: Standard `Procfile` is pre-configured:
   ```
   web: gunicorn app:app
   ```
3. **Environment Variables**: Configure your MySQL credentials and `SECRET_KEY` in your hosting dashboard.

---

## 📁 Repository Structure

```
├── app.py              # Flask application, routing, auth guards & AI knowledge engine
├── db.py               # MySQL connection pooling, schema migration & DB operations
├── requirements.txt    # Production & development dependencies
├── Procfile            # Cloud WSGI process declaration
├── .env.example        # Template for environment configuration
├── .gitignore          # Git exclusion rules (safeguards .env & virtualenvs)
├── README.md           # Project documentation
├── static/
│   ├── css/
│   │   ├── auth.css    # Authentication pages styling (cyber-violet theme)
│   │   └── chat.css    # Interactive dashboard & glassmorphism chat styling
│   └── js/
│       └── chat.js     # Chat engine, voice recognition & speech synthesis logic
└── templates/
    ├── base.html       # Base template with HTML meta tags and CDN assets
    ├── chat.html       # Interactive AI dashboard & chat interface
    ├── login.html      # Glassmorphism login portal
    └── signup.html     # Registration interface with validation
```

---

## 🛡️ Security Highlights

- **Hashed Passwords**: PBKDF2 with SHA-256 prevents credential disclosure.
- **SQL Injection Prevention**: Parameterized queries via PyMySQL prevent injection vulnerabilities.
- **Environment Isolation**: Sensitive configuration (`.env`) is explicitly excluded from version control via `.gitignore`.
- **Session Protection**: Guarded routes prevent unauthenticated access.

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use and customize it for educational and academic purposes.
