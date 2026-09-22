import json, os, random, time
from datetime import datetime
import requests
from dotenv import load_dotenv
load_dotenv()
SCHEMA={"type":"object","properties":{"bias":{"type":"string","enum":["Bullish","Bearish","Neutral"]},"confidence":{"type":"integer","minimum":0,"maximum":100},"summary":{"type":"string"},"key_points":{"type":"array","items":{"type":"string"}},"suggested_action":{"type":"string","enum":["Buy","Sell","Hold"]},"entry":{"type":["number","null"]},"stop_loss":{"type":["number","null"]},"take_profit":{"type":["number","null"]},"reasoning":{"type":"string"}},"required":["bias","confidence","summary","key_points","suggested_action","entry","stop_loss","take_profit","reasoning"],"additionalProperties":False}
class BaseAgent:
 def __init__(self,name,role,system_prompt):
  self.name,self.role,self.system_prompt=name,role,system_prompt; self.key=os.getenv("GEMINI_API_KEY"); self.model=os.getenv("GEMINI_MODEL","gemini-flash-latest"); self.last_report=None; self.status="READY" if self.key else "NOT CONFIGURED"
 def analyze(self,data,extra_context=""):
  if not self.key:return self.fail("Gemini key missing")
  prompt=f"LIVE MARKET DATA:\n{json.dumps(data,indent=2)}\n\nSPECIALIST CONTEXT:\n{extra_context or 'None'}"
  for n in range(4):
   self.status=f"ANALYZING {n+1}/4"
   try:
    r=requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",headers={"x-goog-api-key":self.key,"Content-Type":"application/json"},json={"systemInstruction":{"parts":[{"text":self.system_prompt}]},"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":.2,"maxOutputTokens":1200,"responseMimeType":"application/json","responseJsonSchema":SCHEMA}},timeout=75)
    if r.ok:
     x=json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"]);x.update(agent=self.name,role=self.role,success=True,timestamp=datetime.now().isoformat());self.last_report=x;self.status="COMPLETE";return x
    if r.status_code not in {408,429,500,502,503,504}:break
   except Exception:pass
   if n<3:time.sleep(2**n+random.random())
  return self.fail("Temporary AI service error")
 def fail(self,reason):
  self.status="RETRY REQUIRED";x={"agent":self.name,"role":self.role,"bias":"Neutral","confidence":0,"summary":"Report unavailable. Retry this agent.","key_points":[],"suggested_action":"Hold","entry":None,"stop_loss":None,"take_profit":None,"reasoning":reason,"success":False,"timestamp":datetime.now().isoformat()};self.last_report=x;return x
