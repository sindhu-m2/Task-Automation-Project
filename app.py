import os
import zipfile
import hashlib
import smtplib

from pathlib import Path
from datetime import datetime
from email.message import EmailMessage

import pandas as pd

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, send_file
)

from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from pypdf import PdfReader, PdfWriter
from apscheduler.schedulers.background import BackgroundScheduler


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

WORK_DIR = BASE_DIR / "instance" / "work"
WORK_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "taskflow-local-development-key"
)

app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024

scheduler = BackgroundScheduler(daemon=True)
scheduler.start()


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def make_job_folder():
    folder = WORK_DIR / datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    folder.mkdir(parents=True, exist_ok=True)

    return folder


def save_upload(file, folder):

    filename = secure_filename(file.filename or "")

    if not filename:
        raise ValueError("Invalid filename.")

    folder.mkdir(parents=True, exist_ok=True)

    target = folder / (
        datetime.now().strftime("%H%M%S%f")
        + "_"
        + filename
    )

    file.save(target)

    return target


def zip_folder(folder, output):

    with zipfile.ZipFile(
        output,
        "w",
        zipfile.ZIP_DEFLATED
    ) as archive:

        for path in folder.rglob("*"):

            if path.is_file():

                archive.write(
                    path,
                    path.relative_to(folder)
                )


# -----------------------------
# EMAIL FUNCTION
# -----------------------------

def send_email_message(to_email, subject, body):

    host = os.getenv("SMTP_HOST")
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM") or username

    port = int(os.getenv("SMTP_PORT", "587"))

    if not all([host, username, password, sender]):

        raise RuntimeError(
            "Email is not configured. "
            "Please configure your .env file."
        )

    message = EmailMessage()

    message["From"] = sender
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    with smtplib.SMTP(host, port, timeout=20) as server:

        server.starttls()

        server.login(username, password)

        server.send_message(message)


# -----------------------------
# HOME PAGE
# -----------------------------

@app.route("/")
def home():

    return render_template("index.html")


# -----------------------------
# DASHBOARD
# -----------------------------

@app.route("/dashboard")
def dashboard():

    return render_template("dashboard.html")


# -----------------------------
# FILE MANAGER
# -----------------------------

@app.route("/file-manager")
def file_manager():

    return render_template("file_manager.html")


# ORGANIZE FILES

@app.route("/file-manager/organize", methods=["POST"])
def organize_files():

    uploads = [
        f for f in request.files.getlist("files")
        if f and f.filename
    ]

    if not uploads:

        flash("Please select files.", "error")

        return redirect(url_for("file_manager"))

    job = make_job_folder()

    organized = job / "organized_files"

    organized.mkdir()

    try:

        for item in uploads:

            source = save_upload(item, job)

            ext = source.suffix.lower().lstrip(".")

            categories = {

                "jpg": "Images",
                "jpeg": "Images",
                "png": "Images",
                "gif": "Images",
                "webp": "Images",

                "mp4": "Videos",
                "mov": "Videos",
                "mkv": "Videos",

                "pdf": "PDFs",

                "doc": "Documents",
                "docx": "Documents",
                "txt": "Documents",

                "ppt": "Documents",
                "pptx": "Documents",

                "xls": "Spreadsheets",
                "xlsx": "Spreadsheets",
                "csv": "Spreadsheets",

                "mp3": "Audio",
                "wav": "Audio",

                "zip": "Archives",
                "rar": "Archives"

            }

            category = categories.get(ext, "Other")

            destination = (
                organized / category / source.name
            )

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            source.replace(destination)

        output = job / "organized_files.zip"

        zip_folder(organized, output)

        return send_file(
            output,
            as_attachment=True,
            download_name="organized_files.zip"
        )

    except Exception as error:

        flash(str(error), "error")

        return redirect(url_for("file_manager"))


# BULK RENAME

@app.route("/file-manager/rename", methods=["POST"])
def rename_files():

    uploads = [
        f for f in request.files.getlist("files")
        if f and f.filename
    ]

    prefix = secure_filename(
        request.form.get("prefix", "file")
    ) or "file"

    if not uploads:

        flash("Select files to rename.", "error")

        return redirect(url_for("file_manager"))

    job = make_job_folder()

    output_folder = job / "renamed_files"

    output_folder.mkdir()

    try:

        for number, item in enumerate(uploads, start=1):

            source = save_upload(item, job)

            new_name = (
                f"{prefix}_{number:03d}"
                f"{source.suffix.lower()}"
            )

            source.replace(output_folder / new_name)

        output = job / "renamed_files.zip"

        zip_folder(output_folder, output)

        return send_file(
            output,
            as_attachment=True,
            download_name="renamed_files.zip"
        )

    except Exception as error:

        flash(str(error), "error")

        return redirect(url_for("file_manager"))


# DUPLICATE FINDER

@app.route("/file-manager/duplicates", methods=["POST"])
def find_duplicates():

    uploads = [
        f for f in request.files.getlist("files")
        if f and f.filename
    ]

    if not uploads:

        flash("Select files to scan.", "error")

        return redirect(url_for("file_manager"))

    job = make_job_folder()

    seen = {}

    duplicates = []

    try:

        for item in uploads:

            path = save_upload(item, job)

            digest = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()

            if digest in seen:

                duplicates.append(
                    (path.name, seen[digest])
                )

            else:

                seen[digest] = path.name

        report = job / "duplicate_report.txt"

        with report.open(
            "w",
            encoding="utf-8"
        ) as handle:

            handle.write("TASKFLOW DUPLICATE REPORT\n\n")

            handle.write(
                f"Scanned files: {len(uploads)}\n"
            )

            handle.write(
                f"Duplicates: {len(duplicates)}\n\n"
            )

            for duplicate, original in duplicates:

                handle.write(
                    f"{duplicate} duplicates {original}\n"
                )

            if not duplicates:

                handle.write("No duplicates found.")

        return send_file(
            report,
            as_attachment=True,
            download_name="duplicate_report.txt"
        )

    except Exception as error:

        flash(str(error), "error")

        return redirect(url_for("file_manager"))


# -----------------------------
# PDF TOOLS
# -----------------------------

@app.route("/pdf-tools")
def pdf_tools():

    return render_template("pdf_tools.html")


# MERGE PDFS

@app.route("/pdf-tools/merge", methods=["POST"])
def merge_pdfs():

    uploads = [
        f for f in request.files.getlist("files")
        if f and f.filename
    ]

    if len(uploads) < 2:

        flash(
            "Select at least two PDF files.",
            "error"
        )

        return redirect(url_for("pdf_tools"))

    job = make_job_folder()

    writer = PdfWriter()

    try:

        for item in uploads:

            if Path(item.filename).suffix.lower() != ".pdf":

                raise ValueError(
                    "Only PDF files are allowed."
                )

            path = save_upload(item, job)

            reader = PdfReader(str(path))

            for page in reader.pages:

                writer.add_page(page)

        output = job / "merged_document.pdf"

        with output.open("wb") as handle:

            writer.write(handle)

        return send_file(
            output,
            as_attachment=True,
            download_name="merged_document.pdf"
        )

    except Exception as error:

        flash(str(error), "error")

        return redirect(url_for("pdf_tools"))


# SPLIT PDF

@app.route("/pdf-tools/split", methods=["POST"])
def split_pdf():

    item = request.files.get("file")

    if (
        not item
        or not item.filename
        or Path(item.filename).suffix.lower() != ".pdf"
    ):

        flash("Select a valid PDF file.", "error")

        return redirect(url_for("pdf_tools"))

    job = make_job_folder()

    try:

        path = save_upload(item, job)

        reader = PdfReader(str(path))

        output_folder = job / "split_pages"

        output_folder.mkdir()

        for index, page in enumerate(
            reader.pages,
            start=1
        ):

            writer = PdfWriter()

            writer.add_page(page)

            output_file = (
                output_folder / f"page_{index:03d}.pdf"
            )

            with output_file.open("wb") as handle:

                writer.write(handle)

        output = job / "split_pages.zip"

        zip_folder(output_folder, output)

        return send_file(
            output,
            as_attachment=True,
            download_name="split_pages.zip"
        )

    except Exception as error:

        flash(str(error), "error")

        return redirect(url_for("pdf_tools"))


# -----------------------------
# EXCEL TOOLS
# -----------------------------

@app.route("/excel-tools")
def excel_tools():

    return render_template("excel_tools.html")


@app.route("/excel-tools/process", methods=["POST"])
def process_excel():

    item = request.files.get("file")

    action = request.form.get("action", "preview")

    if not item or not item.filename:

        flash("Select an Excel or CSV file.", "error")

        return redirect(url_for("excel_tools"))

    suffix = Path(item.filename).suffix.lower()

    if suffix not in [".xlsx", ".xls", ".csv"]:

        flash("Unsupported file format.", "error")

        return redirect(url_for("excel_tools"))

    job = make_job_folder()

    try:

        path = save_upload(item, job)

        if suffix == ".csv":

            df = pd.read_csv(path)

        else:

            df = pd.read_excel(path)

        if action == "clean":

            df = df.drop_duplicates()

            df = df.dropna(how="all")

            output = job / "cleaned_spreadsheet.xlsx"

            df.to_excel(
                output,
                index=False
            )

            return send_file(
                output,
                as_attachment=True,
                download_name="cleaned_spreadsheet.xlsx"
            )

        preview = df.head(12).fillna("").to_html(
            classes="data-table",
            index=False,
            border=0,
            escape=True
        )

        return render_template(
            "excel_tools.html",
            preview=preview,
            row_count=len(df),
            column_count=len(df.columns)
        )

    except Exception as error:

        flash(str(error), "error")

        return redirect(url_for("excel_tools"))


# -----------------------------
# EMAIL AUTOMATION
# -----------------------------

@app.route("/email-automation")
def email_automation():

    configured = all(
        os.getenv(key)
        for key in [
            "SMTP_HOST",
            "SMTP_USERNAME",
            "SMTP_PASSWORD"
        ]
    )

    return render_template(
        "email_automation.html",
        email_configured=configured
    )


@app.route("/email-automation/send", methods=["POST"])
def send_email():

    to_email = request.form.get("to", "").strip()

    subject = request.form.get("subject", "").strip()

    body = request.form.get("body", "").strip()

    if not all([to_email, subject, body]):

        flash("Complete all email fields.", "error")

        return redirect(url_for("email_automation"))

    try:

        send_email_message(
            to_email,
            subject,
            body
        )

        flash("Email sent successfully!", "success")

    except Exception as error:

        flash(str(error), "error")

    return redirect(url_for("email_automation"))


# -----------------------------
# TASK SCHEDULER
# -----------------------------

def scheduled_email(to_email, subject, body):

    try:

        send_email_message(
            to_email,
            subject,
            body
        )

        app.logger.info(
            "Scheduled email sent to %s",
            to_email
        )

    except Exception:

        app.logger.exception(
            "Scheduled email failed"
        )


@app.route("/scheduler")
def task_scheduler():

    jobs = []

    for job in scheduler.get_jobs():

        jobs.append({

            "id": job.id,

            "name": job.name,

            "run_time": (
                job.next_run_time.strftime(
                    "%d %b %Y, %I:%M %p"
                )
                if job.next_run_time
                else "Pending"
            )

        })

    return render_template(
        "scheduler.html",
        jobs=jobs
    )


@app.route("/scheduler/add", methods=["POST"])
def add_scheduled_email():

    to_email = request.form.get("to", "").strip()

    subject = request.form.get("subject", "").strip()

    body = request.form.get("body", "").strip()

    run_at = request.form.get("run_at", "").strip()

    if not all([to_email, subject, body, run_at]):

        flash("Complete all fields.", "error")

        return redirect(url_for("task_scheduler"))

    try:

        run_time = datetime.fromisoformat(run_at)

        if run_time <= datetime.now():

            raise ValueError(
                "Choose a future date and time."
            )

        job_id = (
            "email_"
            + datetime.now().strftime("%Y%m%d%H%M%S%f")
        )

        scheduler.add_job(
            scheduled_email,
            "date",
            run_date=run_time,
            args=[to_email, subject, body],
            id=job_id,
            name=f"Email to {to_email}"
        )

        flash(
            "Email scheduled successfully!",
            "success"
        )

    except Exception as error:

        flash(str(error), "error")

    return redirect(url_for("task_scheduler"))


@app.route("/scheduler/delete/<job_id>", methods=["POST"])
def delete_scheduled_job(job_id):

    try:

        scheduler.remove_job(job_id)

        flash("Scheduled task cancelled.", "success")

    except Exception:

        flash("Task could not be found.", "error")

    return redirect(url_for("task_scheduler"))


# -----------------------------
# ABOUT PAGE
# -----------------------------

@app.route("/about")
def about():

    return render_template("about.html")


# -----------------------------
# ERROR HANDLING
# -----------------------------

@app.errorhandler(413)
def file_too_large(error):

    flash(
        "File too large. Maximum upload size is 30 MB.",
        "error"
    )

    return redirect(
        request.referrer or url_for("dashboard")
    )


# -----------------------------
# RUN APPLICATION
# -----------------------------

if __name__ == "__main__":

    app.run(debug=True)