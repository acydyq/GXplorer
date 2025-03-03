import os
import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox
)
try:
    import openai
except ImportError:
    openai = None

class AIIntegrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Assistant")
        self.resize(600, 400)
        self.api_key = None  # Optional: user provided API key
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # API Key Input
        key_layout = QHBoxLayout()
        key_label = QLabel("OpenAI API Key (optional):")
        self.key_input = QLineEdit()
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_input)
        self.layout.addLayout(key_layout)
        
        # Prompt Input
        self.prompt_edit = QLineEdit()
        self.prompt_edit.setPlaceholderText("Enter your query...")
        self.layout.addWidget(self.prompt_edit)
        
        # Response Display
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        self.layout.addWidget(self.response_display)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_request)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.send_btn)
        btn_layout.addWidget(self.close_btn)
        self.layout.addLayout(btn_layout)
    
    def send_request(self):
        prompt = self.prompt_edit.text().strip()
        if not prompt:
            QMessageBox.warning(self, "Input Error", "Please enter a prompt.")
            return
        
        # Check if user provided an API key
        self.api_key = self.key_input.text().strip()
        if self.api_key and openai:
            openai.api_key = self.api_key
            try:
                response = openai.Completion.create(
                    engine="davinci",
                    prompt=prompt,
                    max_tokens=50
                )
                answer = response.choices[0].text.strip()
            except Exception as e:
                answer = f"Error communicating with OpenAI: {e}"
        else:
            # Free demo mode: echo the prompt with a simple transformation
            answer = f"Demo mode: You said '{prompt}'. (Implement advanced AI integration here.)"
        
        self.response_display.append(">> " + prompt)
        self.response_display.append(answer)
        self.response_display.append("\n")
