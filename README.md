# 🚀 TaskFlow – Automation Suite

A modern, web-based task automation application built using Python and Flask. TaskFlow brings multiple productivity tools together in one place, helping users automate everyday tasks through a simple and attractive interface.

## ✨ Features

### 📁 File Manager
- Organize uploaded files.
- Bulk rename files.
- Detect duplicate files.

### 📄 PDF Tools
- Merge multiple PDF files.
- Split PDF files into separate documents.

### 📊 Excel Tools
- Upload and preview Excel files.
- Clean spreadsheet data.

### 📧 Email Automation
- Send emails using SMTP configuration.

### ⏰ Scheduler
- Schedule emails for a selected date and time.

### 📌 Dashboard
- Access all automation tools from one dashboard.
- Navigate easily between different sections.

## 🛠️ Technologies Used

- **Python** – Backend programming
- **Flask** – Web framework
- **HTML5** – Web page structure
- **CSS3** – Styling and animations
- **JavaScript** – Interactive functionality
- **Pandas** – Excel data processing
- **OpenPyXL** – Excel file handling
- **pypdf** – PDF processing
- **APScheduler** – Task scheduling

## 📂 Project Structure

```text
Task Automation Project/
│
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── file_manager.html
│   ├── pdf_tools.html
│   ├── excel_tools.html
│   ├── email_automation.html
│   ├── scheduler.html
│   └── about.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
└── instance/
    └── work/
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/TaskFlow-Automation-Suite.git
```

### 2. Open the project folder

```bash
cd TaskFlow-Automation-Suite
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

For Windows:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure environment variables

Create a `.env` file using `.env.example` as a reference.

Add the required Flask secret key and SMTP credentials if you want to use email automation.

Keep your actual credentials private.

### 7. Run the application

```bash
python app.py
```

### 8. Open in your browser

```text
http://127.0.0.1:5000
```

## 🔐 Security Notes

- Environment variables are used for sensitive configuration.
- The `.env` file is excluded from Git using `.gitignore`.
- Do not upload passwords, API keys, or SMTP credentials to GitHub.

## ⚠️ Important Notes

- Uploaded files are processed by the application.
- Scheduled jobs are stored in memory and may be lost when the application restarts.
- Email automation requires valid SMTP configuration.
- Temporary uploaded files are not intended for permanent storage.

## 🎯 Project Objective

The main objective of TaskFlow is to simplify repetitive tasks by combining useful automation tools into a single web application.

## 👩‍💻 Developer
**Boddu Sudarshana Laxmi Sindhu**
