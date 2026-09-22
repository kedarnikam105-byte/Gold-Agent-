import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "bias": {"type": "string", "enum": ["Bullish", "Bearish", "Neutral"]},
        "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
        "summary": {"type": "string"},
        "key_points": {"type": "array", "items": {"type": "string"}},
        "suggested_action": {"type": "string", "enum": ["Buy", "Sell", "Hold"]},
        "entry": {"type": ["number", "null"]},
        "stop_loss": {"type": ["number", "null"]},
        "take_profit": {"type": ["number", "null"]},
        "reasoning": {"type": "string"},
    },
    "required": [
        "bias", "confidence", "summary", "key_points", "suggested_action",
        "entry", "stop_loss", "take_profit", "reasoning"
    ],
    "additionalProperties": False,
}


class BaseAgent:
    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
        self.last_report = None
        self.status = "Idle" if self.api_key else "API key missing"
        self.history = []

    def analyze(self, market_data: dict, extra_context: str = "") -> dict:
        self.status = "Analyzing"
        try:
            if not self.api_key:
                raise RuntimeError("GEMINI_API_KEY is missing. Add it in Streamlit Secrets.")

            prompt = (
                "Current Gold market data:\n"
                f"{json.dumps(market_data, indent=2)}\n\n"
                "Additional context:\n"
                f"{extra_context or 'None'}"
            )
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
                headers={
                    "x-goog-api-key": self.api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "systemInstruction": {"parts": [{"text": self.system_prompt}]},
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.25,
                        "maxOutputTokens": 1400,
                        "responseMimeType": "application/json",
                        "responseJsonSchema": REPORT_SCHEMA,
                    },
                },
                timeout=90,
            )
            response.raise_for_status()
            payload = response.json()
            content = payload["candidates"][0]["content"]["parts"][0]["text"]
            report = json.loads(content)
            report.update({
                "agent": self.name,
                "role": self.role,
                "timestamp": datetime.now().isoformat(),
            })
            self.last_report = report
            self.history.append(report)
            self.status = "Ready"
            return report
        except Exception as exc:
            self.status = "Error"
            report = {
                "agent": self.name,
                "role": self.role,
                "bias": "Neutral",
                "confidence": 0,
                "summary": f"Analysis failed: {exc}",
                "key_points": [],
                "suggested_action": "Hold",
                "entry": None,
                "stop_loss": None,
                "take_profit": None,
                "reasoning": str(exc),
                "timestamp": datetime.now().isoformat(),
            }
            self.last_report = report
            return report
