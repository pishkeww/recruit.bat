import os
import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QScrollArea, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog, QSplitter,
    QAbstractItemView, QComboBox
)
from PyQt6.QtCore import QThread, Qt
from PyQt6.QtGui import QColor

from core.pipeline_worker import PipelineWorker
from core.batch_worker import BatchWorker
from core.processing.resume_parser import parse_resume_pdf
from core.export import export_csv, export_json
from ui.components.file_upload import FileUploadButton
from app.dependencies import build_container
from app.config import OLLAMA_URL


def check_ollama(url="http://localhost:11434/api/tags", timeout=2):
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("recruit.bat")
        self.resize(1400, 800)

        container = build_container()
        self.pipeline = container.pipeline
        self.ollama_connected = check_ollama()

        self.active_keywords = []
        self.all_chips = []
        self.batch_results = []

        root_layout = QVBoxLayout()

        status_row = QHBoxLayout()
        status_row.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Single Resume", "Batch (Folder)"])
        self.mode_combo.currentIndexChanged.connect(self.toggle_mode)
        status_row.addWidget(self.mode_combo)
        status_row.addStretch()

        self.ollama_label = QLabel()
        if self.ollama_connected:
            self.ollama_label.setText("Ollama: Connected")
            self.ollama_label.setStyleSheet(
                "color: green; font-weight: bold; padding: 4px;"
            )
        else:
            self.ollama_label.setText("Ollama: Not connected (scoring only)")
            self.ollama_label.setStyleSheet(
                "color: red; font-weight: bold; padding: 4px;"
            )
        status_row.addWidget(self.ollama_label)
        root_layout.addLayout(status_row)

        self.single_widget = self._build_single_view()
        self.batch_widget = self._build_batch_view()

        root_layout.addWidget(self.single_widget)
        root_layout.addWidget(self.batch_widget)
        self.batch_widget.hide()

        self.setLayout(root_layout)

    def _build_single_view(self):
        widget = QWidget()
        layout = QHBoxLayout()

        left = QVBoxLayout()
        right = QVBoxLayout()

        self.resume = QTextEdit()
        self.jd = QTextEdit()

        self.upload = FileUploadButton(self.handle_upload)

        self.clear_resume_btn = QPushButton("Clear Resume")
        self.clear_resume_btn.clicked.connect(self.clear_resume)

        upload_row = QHBoxLayout()
        upload_row.addWidget(self.upload)
        upload_row.addWidget(self.clear_resume_btn)

        self.run_btn = QPushButton("Analyze")
        self.run_btn.clicked.connect(self.start_analysis)

        self.clear_jd_btn = QPushButton("Clear JD")
        self.clear_jd_btn.clicked.connect(self.clear_jd)

        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.clicked.connect(self.clear_all)

        self.progress = QLabel("Idle")

        run_row = QHBoxLayout()
        run_row.addWidget(self.run_btn)
        run_row.addWidget(self.clear_jd_btn)
        run_row.addWidget(self.clear_all_btn)

        left.addWidget(QLabel("Resume"))
        left.addWidget(self.resume)
        left.addLayout(upload_row)
        left.addWidget(QLabel("Job Description"))
        left.addWidget(self.jd)
        left.addLayout(run_row)
        left.addWidget(self.progress)

        self.score = QLabel("0")
        self.score.setStyleSheet("font-size: 36px; font-weight: bold;")

        self.breakdown = QLabel("")

        self.skills = QTextEdit()
        self.skills.setReadOnly(True)

        self.cover = QTextEdit()
        self.cover.setReadOnly(True)

        self.suggest = QTextEdit()
        self.suggest.setReadOnly(True)

        self.keyword_container = QWidget()
        self.keyword_layout = QHBoxLayout()
        self.keyword_container.setLayout(self.keyword_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.keyword_container)

        right.addWidget(QLabel("ATS Score"))
        right.addWidget(self.score)
        right.addWidget(self.breakdown)
        right.addWidget(QLabel("Keywords"))
        right.addWidget(scroll)

        if self.ollama_connected:
            right.addWidget(QLabel("Skills"))
            right.addWidget(self.skills)
            right.addWidget(QLabel("Cover Letter"))
            right.addWidget(self.cover)
            right.addWidget(QLabel("Suggestions"))
            right.addWidget(self.suggest)
        else:
            right.addWidget(QLabel("Skills (requires Ollama)"))
            right.addWidget(self.skills)
            right.addWidget(QLabel("Cover Letter (requires Ollama)"))
            right.addWidget(self.cover)
            right.addWidget(QLabel("Suggestions (requires Ollama)"))
            right.addWidget(self.suggest)
            self.skills.setPlaceholderText("Connect to Ollama to extract skills")
            self.cover.setPlaceholderText("Connect to Ollama to generate cover letter")
            self.suggest.setPlaceholderText("Connect to Ollama to generate suggestions")

        layout.addLayout(left, 1)
        layout.addLayout(right, 2)
        widget.setLayout(layout)
        return widget

    def _build_batch_view(self):
        widget = QWidget()
        layout = QVBoxLayout()

        job_row = QHBoxLayout()
        job_row.addWidget(QLabel("Job Description:"))
        self.batch_jd = QTextEdit()
        self.batch_jd.setMaximumHeight(120)
        job_row.addWidget(self.batch_jd)
        layout.addLayout(job_row)

        btn_row = QHBoxLayout()

        self.batch_folder_btn = QPushButton("Select Folder of PDFs")
        self.batch_folder_btn.clicked.connect(self.select_batch_folder)
        btn_row.addWidget(self.batch_folder_btn)

        self.batch_run_btn = QPushButton("Analyze All")
        self.batch_run_btn.clicked.connect(self.start_batch)
        btn_row.addWidget(self.batch_run_btn)

        self.batch_progress = QLabel("Idle")
        btn_row.addWidget(self.batch_progress)

        btn_row.addStretch()

        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(lambda: self.export("csv"))
        self.export_csv_btn.setEnabled(False)
        btn_row.addWidget(self.export_csv_btn)

        self.export_json_btn = QPushButton("Export JSON")
        self.export_json_btn.clicked.connect(lambda: self.export("json"))
        self.export_json_btn.setEnabled(False)
        btn_row.addWidget(self.export_json_btn)

        layout.addLayout(btn_row)

        self.batch_table = QTableWidget()
        self.batch_table.setColumnCount(7)
        self.batch_table.setHorizontalHeaderLabels([
            "Rank", "File", "Score", "Keyword", "Semantic",
            "Recency", "Education"
        ])
        self.batch_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.batch_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.batch_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.batch_table.doubleClicked.connect(self.show_batch_detail)
        layout.addWidget(self.batch_table)

        self.batch_detail = QTextEdit()
        self.batch_detail.setReadOnly(True)
        self.batch_detail.setMaximumHeight(200)
        layout.addWidget(self.batch_detail)

        widget.setLayout(layout)
        return widget

    def toggle_mode(self, index):
        if index == 0:
            self.single_widget.show()
            self.batch_widget.hide()
        else:
            self.single_widget.hide()
            self.batch_widget.show()

    def handle_upload(self, file_path):
        self.resume.setPlainText(parse_resume_pdf(file_path))

    def clear_resume(self):
        self.resume.clear()
        self.progress.setText("Idle")

    def clear_jd(self):
        self.jd.clear()

    def clear_all(self):
        self.resume.clear()
        self.jd.clear()
        self.score.setText("0")
        self.breakdown.setText("")
        self.skills.clear()
        self.cover.clear()
        self.suggest.clear()
        self.progress.setText("Idle")
        self.active_keywords = []
        for chip in self.all_chips:
            chip.deleteLater()
        self.all_chips = []

    def start_analysis(self):
        resume = self.resume.toPlainText()
        job = self.jd.toPlainText()

        if not resume or not job:
            self.progress.setText("Provide both inputs")
            return

        self.run_btn.setEnabled(False)

        self.thread = QThread()
        self.worker = PipelineWorker(
            self.pipeline,
            resume,
            job,
            self.active_keywords if self.active_keywords else None
        )

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_result)
        self.worker.progress.connect(self.progress.setText)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_result(self, result):
        self.run_btn.setEnabled(True)

        self.score.setText(str(result["score"]))

        self.breakdown.setText(
            f"K:{result['keyword']} S:{result['semantic']} "
            f"R:{result['recency']} E:{result['education']} "
            f"C:{result['confidence']}"
        )

        self.skills.setText("\n".join(
            [f"{k}: {v}" for k, v in result["skills"].items()]
        ))

        self.cover.setText(result["cover_letter"])
        self.suggest.setText(result["suggestions"])

        self.build_keyword_chips(result["job_keywords"])

    def build_keyword_chips(self, keywords):
        for chip in self.all_chips:
            chip.deleteLater()

        self.all_chips = []

        for kw in keywords:
            chip = QPushButton(kw)
            chip.setCheckable(True)
            chip.setChecked(True)
            chip.clicked.connect(self.update_keywords)

            self.keyword_layout.addWidget(chip)
            self.all_chips.append(chip)

        self.update_keywords()

    def update_keywords(self):
        self.active_keywords = [
            chip.text() for chip in self.all_chips if chip.isChecked()
        ]

    def select_batch_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder of PDFs")
        if folder:
            self.batch_pdf_folder = folder
            pdfs = [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith(".pdf")
            ]
            self.batch_folder_btn.setText(
                f"Folder: {os.path.basename(folder)} ({len(pdfs)} PDFs)"
            )

    def start_batch(self):
        job = self.batch_jd.toPlainText()
        if not job:
            self.batch_progress.setText("Enter a job description")
            return

        if not hasattr(self, "batch_pdf_folder"):
            self.batch_progress.setText("Select a folder first")
            return

        pdfs = [
            os.path.join(self.batch_pdf_folder, f)
            for f in os.listdir(self.batch_pdf_folder)
            if f.lower().endswith(".pdf")
        ]

        if not pdfs:
            self.batch_progress.setText("No PDFs found in folder")
            return

        self.batch_run_btn.setEnabled(False)
        self.batch_table.setRowCount(0)
        self.batch_detail.clear()
        self.batch_results = []

        self.batch_thread = QThread()
        self.batch_worker = BatchWorker(
            self.pipeline, pdfs, job,
            self.active_keywords if self.active_keywords else None
        )

        self.batch_worker.moveToThread(self.batch_thread)
        self.batch_thread.started.connect(self.batch_worker.run)
        self.batch_worker.progress.connect(self.batch_progress.setText)
        self.batch_worker.single_done.connect(self.on_batch_single)
        self.batch_worker.finished.connect(self.on_batch_done)
        self.batch_worker.finished.connect(self.batch_thread.quit)
        self.batch_worker.finished.connect(self.batch_worker.deleteLater)
        self.batch_thread.finished.connect(self.batch_thread.deleteLater)
        self.batch_thread.start()

    def on_batch_single(self, result):
        self.batch_results.append(result)
        row = self.batch_table.rowCount()
        self.batch_table.insertRow(row)

        rank = len(self.batch_results)
        items = [
            str(rank),
            result.get("filename", ""),
            str(result.get("score", 0)),
            str(result.get("keyword", 0)),
            str(result.get("semantic", 0)),
            str(result.get("recency", 0)),
            str(result.get("education", 0))
        ]

        score = result.get("score", 0)
        for col, text in enumerate(items):
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if col == 2 and score >= 75:
                item.setBackground(QColor(0, 180, 0, 40))
            elif col == 2 and score >= 50:
                item.setBackground(QColor(255, 165, 0, 40))
            elif col == 2:
                item.setBackground(QColor(255, 0, 0, 40))
            self.batch_table.setItem(row, col, item)

    def on_batch_done(self, results):
        self.batch_run_btn.setEnabled(True)
        self.export_csv_btn.setEnabled(True)
        self.export_json_btn.setEnabled(True)
        self.batch_results = results

        self.batch_table.setRowCount(0)
        for i, r in enumerate(results, 1):
            row = self.batch_table.rowCount()
            self.batch_table.insertRow(row)

            items = [
                str(i),
                r.get("filename", ""),
                str(r.get("score", 0)),
                str(r.get("keyword", 0)),
                str(r.get("semantic", 0)),
                str(r.get("recency", 0)),
                str(r.get("education", 0))
            ]

            score = r.get("score", 0)
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col == 2 and score >= 75:
                    item.setBackground(QColor(0, 180, 0, 40))
                elif col == 2 and score >= 50:
                    item.setBackground(QColor(255, 165, 0, 40))
                elif col == 2:
                    item.setBackground(QColor(255, 0, 0, 40))
                self.batch_table.setItem(row, col, item)

    def show_batch_detail(self, index):
        row = index.row()
        if row < len(self.batch_results):
            r = self.batch_results[row]
            structured = r.get("structured", {})
            lines = [
                f"File: {r.get('filename', '')}",
                f"Score: {r.get('score', 0)}",
                f"Name: {structured.get('name', 'N/A')}",
                f"Email: {structured.get('email', 'N/A')}",
                f"Phone: {structured.get('phone', 'N/A')}",
                f"Location: {structured.get('location', 'N/A')}",
                f"Experience: {structured.get('total_experience_years', 'N/A')} years",
                "",
                "Education:"
            ]
            for edu in structured.get("education", []):
                lines.append(
                    f"  - {edu.get('degree', '')} | "
                    f"{edu.get('institution', '')} | "
                    f"{edu.get('year', '')}"
                )
            lines.append("")
            lines.append("Experience:")
            for exp in structured.get("experience", []):
                lines.append(
                    f"  - {exp.get('role', '')} @ {exp.get('company', '')} | "
                    f"{exp.get('start', '')} - {exp.get('end', '')}"
                )
            lines.append("")
            lines.append(
                "Skills: " + ", ".join(structured.get("skills", []))
            )

            self.batch_detail.setPlainText("\n".join(lines))

    def export(self, fmt):
        if not self.batch_results:
            return

        if fmt == "csv":
            path, _ = QFileDialog.getSaveFileName(
                self, "Export CSV", "results.csv", "CSV Files (*.csv)"
            )
            if path:
                export_csv(self.batch_results, path)
                self.batch_progress.setText(f"Exported to {path}")
        elif fmt == "json":
            path, _ = QFileDialog.getSaveFileName(
                self, "Export JSON", "results.json", "JSON Files (*.json)"
            )
            if path:
                export_json(self.batch_results, path)
                self.batch_progress.setText(f"Exported to {path}")
