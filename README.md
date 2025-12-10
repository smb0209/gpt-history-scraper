# GPT Auto(Increase Date) Prompting Tool

A simple Tkinter-based GUI application that automatically queries the OpenAI API for historical events based on a date range, then saves the results into text files.  
Designed as a lightweight automation tool for daily or sequential historical research.

This project currently consists of a **single Python file (`main.py`)** and supports both local execution and Windows executable builds.

---

## 🚀 Features

- GUI built with **Tkinter**
- Queries the OpenAI Chat Completions API (`gpt-5.1` by default)
- Automatically generates questions using a date range and a template
- Supports date formats:
    - `YYYY-MM-DD`
    - `MM-DD` (year automatically set internally)
- Saves results into two files:
    - **Full log** (questions + answers)
    - **Answers only**
- Customizable output directory (required)
- Multi-threaded execution with a **Stop** button
- Error handling & auto retry (up to 3 attempts)

---

## 📦 Requirements

- Python **3.10+**
- pip
- Tkinter (bundled with official Python installers)
- OpenAI API Key

---

## 📥 Installation

```bash
# Optional: create virtual environment
python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows

# Install dependencies
pip install openai certifi
```

---

## ▶️ Run the Application
```bash
python main.py
```
A Tkinter window will appear.

---

## 🖥️ Application Overview

- OpenAI API Key

  - Paste your OpenAI API key (e.g., sk-proj-...). It is not masked.

- Model

  - Defaults to gpt-5.1. Can be changed to any available model.

- Full Log File

  - File where both questions and answers are appended.

- Answers File

  - File that stores only the answers.

- Output Folder (Required)

  - Directory where both files will be saved.
If the directory does not exist, the tool attempts to create it.

---

📅 Date-Based Mode

- Start / End Date Formats
  - MM-DD
  - YYYY-MM-DD

- Step (days)
Controls date increments:
  - 1 → daily
  -	7 → weekly

- Question Template
  - Use {date} placeholder:
```code
List 3–5 major historical events that occurred on {date}.
```

- 📁 Output Format
  - Full Log
```code
===== DATE: 02월 01일 =====
[QUESTION]
Summary request...

[ANSWER]
- ...
- ...
```
  - Answers Only
```code
- Event summary...
```

---

## ❗ Error Handling
- Retries API calls up to 3 times
- Logs all errors in the GUI log window
- Writes placeholder text into files on failure

---

## 🏗️ Local Windows EXE Build (Optional)
```bash
pip install pyinstaller

pyinstaller --onefile --windowed --name gpt-auto-history-tool main.py
```

---

🙋 Author

Created by Minbong (David) Seo.
