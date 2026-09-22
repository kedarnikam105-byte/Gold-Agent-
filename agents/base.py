import json, os, random, time
from datetime import datetime
import requests
from dotenv import load_dotenv
load_dotenv()
REPORT_SCHEMA={"type":"object","properties":{"bias":{"type":"string","enum":["Bullish","Bearish","Neutral"]},"confidence":{"type":"integer","minimum":0,"maximum":100},"summary":{"type":"string"},"key_points":{"type":"array","items":{"type":"string"}},"suggested_action":{"type":"string","enum":["Buy","Sell","Hold"]},"entry":{"type":["number","null"]},"stop_loss":{"type":["number","null"]},"take_profit":{"type":["number","null"]},"reasoning":{"type":"string"}},"required":["bias","confidence","summary","key_points","suggested_action","entry","stop_loss","take_profit","reasoning"],"additionalProperties":False}
TRANSIENT={408,429,500,502,503,504}
class BaseAgent:
 def __init__(self,name,role,system_prompt):
  self.name,self.role,self.system_prompt=name,role,system_prompt; self.api_key=os.getenv("GEMINI_API_KEY"); self.models=list(dict.fromkeys([os.getenv("GEMINI_MODEL","gemini-3.5-flash"),"gemini-flash-latest"])); self.last_report=None; self.status="Ready" if self.api_key else "API key missing"
 def analyze(self,market_data,extra_context=""):
  try:
   if not self.api_key: raise RuntimeError("Gemini is not configured")
   prompt=f"Current market data:\n{json.dumps(market_data,indent=2)}\n\nAdditional context:\n{extra_context or 'None'}"; response=None
   for model in self.models:
    for attempt in range(4):
     self.status=f"Analyzing · attempt {attempt+1}/4"; response=requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",headers={"x-goog-api-key":self.api_key,"Content-Type":"application/json"},json={"systemInstruction":{"parts":[{"text":self.system_prompt}]},"contents":[{"role":"user","parts":[{"text":prompt}]}],"generationConfig":{"temperature":.25,"maxOutputTokens":1400,"responseMimeType":"application/json","responseJsonSchema":REPORT_SCHEMA}},timeout=90)
     if response.ok: break
     if response.status_code not in TRANSIENT: break
     if attempt<3: time.sleep((2**attempt)+random.uniform(.1,.6))
    if response.ok: break
   if not response.ok: raise RuntimeError(f"Temporary Gemini service error ({response.status_code})")
   report=json.loads(response.json()["candidates"][0]["content"]["parts"][0]["text"]); report.update(agent=self.name,role=self.role,timestamp=datetime.now().isoformat(),success=True); self.last_report=report; self.status="Completed"; return report
  except Exception:
   self.status="Temporarily unavailable"; report={"agent":self.name,"role":self.role,"bias":"Neutral","confidence":0,"summary":"Temporarily unavailable. Use Retry Failed Agents.","key_points":[],"suggested_action":"Hold","entry":None,"stop_loss":None,"take_profit":None,"reasoning":"A temporary AI service error occurred. Internal service details were hidden.","timestamp":datetime.now().isoformat(),"success":False}; self.last_report=report; return report
