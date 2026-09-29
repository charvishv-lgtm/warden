import json
import os
import re
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from hindsight_client import Hindsight
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize FastAPI App
app = FastAPI(
    title="Identity Hindsight Security API",
    description="Analyzes Non-Human Identities (NHIs) by correlating current IAM permissions with historical context from Hindsight memory.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration & Clients
HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL", os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io"))
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
IDENTITIES_FILE = "current_identities.json"
MEMORY_BANK = "identity-memory"

hindsight_client = Hindsight(
    base_url=HINDSIGHT_BASE_URL,
    api_key=HINDSIGHT_API_KEY
)

groq_client = Groq(
    api_key=GROQ_API_KEY
)


# Request & Response Schemas
class AnalyzeRequest(BaseModel):
    identity_name: str


class AnalyzeResponse(BaseModel):
    identity: str
    risk_level: str
    current_permissions: List[str]
    historical_context: List[str]
    agent_analysis: str


def load_current_identities() -> list[dict]:
    """Loads the snapshot of identities from current_identities.json."""
    if not os.path.exists(IDENTITIES_FILE):
        raise HTTPException(
            status_code=500,
            detail=f"Configuration error: '{IDENTITIES_FILE}' not found. Please run seed_data.py first."
        )
    try:
        with open(IDENTITIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read '{IDENTITIES_FILE}': {str(e)}"
        )


def query_hindsight_history(identity_name: str) -> list[str]:
    """Queries Hindsight memory bank for the historical timeline of an identity."""
    try:
        recall_resp = hindsight_client.recall(
            bank_id=MEMORY_BANK,
            query=identity_name,
            max_tokens=2048
        )
        if recall_resp and recall_resp.results:
            return [result.text for result in recall_resp.results]
        return []
    except Exception as e:
        # Fallback if Hindsight recall encounters an error
        print(f"[!] Warning: Hindsight recall failed: {e}")
        return []


def parse_llm_json_response(raw_text: str) -> dict:
    """Parses LLM output into JSON, extracting JSON blocks if markdown is present."""
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Try extracting JSON from code fence
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Fallback simple extractor
        risk = "Medium"
        if "High" in raw_text:
            risk = "High"
        elif "Low" in raw_text:
            risk = "Low"
        return {
            "risk_level": risk,
            "agent_analysis": raw_text.strip()
        }


@app.get("/")
def root():
    return {
        "service": "Identity Hindsight Security API",
        "status": "healthy",
        "memory_bank": MEMORY_BANK,
        "model": GROQ_MODEL
    }


@app.get("/identities")
def list_identities():
    """Returns the list of all identities in the current snapshot."""
    return load_current_identities()


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_identity(payload: AnalyzeRequest):
    identity_name = payload.identity_name.strip()

    # 1. Read local current_identities.json to get CURRENT permissions
    identities = load_current_identities()
    matched_identity = next(
        (item for item in identities if item.get("name", "").lower() == identity_name.lower()),
        None
    )

    if not matched_identity:
        available_names = [item.get("name") for item in identities]
        raise HTTPException(
            status_code=404,
            detail=f"Identity '{identity_name}' not found. Available identities: {available_names}"
        )

    current_permissions = matched_identity.get("permissions", [])

    # 2. Query Hindsight identity-memory bank for chronological historical context
    historical_facts = query_hindsight_history(identity_name)

    # 3. Construct prompt for Groq
    system_prompt = (
        "You are an expert Cloud Security Agent specializing in Non-Human Identity (NHI) and IAM governance.\n"
        "Your task is to analyze an identity by comparing its CURRENT permissions against its ORIGINAL purpose, "
        "historical timeline, and usage context retrieved from memory.\n"
        "Determine the Risk Level ('High', 'Medium', or 'Low'), and provide a concise, factual explanation of the risk.\n\n"
        "Risk guidelines:\n"
        "- 'High': Identity was created for a specific project/scope that is now completed or dormant, but elevated permissions "
        "(e.g., Admin, S3 Write, unrestricted privileges) were added subsequently, or permissions diverge dangerously from intent.\n"
        "- 'Medium': Some drift or inactive permissions that warrant inspection, but without obvious critical privilege escalation.\n"
        "- 'Low': Permissions are tightly scoped and align consistently with its documented, ongoing operational purpose.\n\n"
        "You MUST respond ONLY with valid JSON in the following format:\n"
        "{\n"
        '  "risk_level": "High" | "Medium" | "Low",\n'
        '  "agent_analysis": "<concise explanation of the risk>"\n'
        "}"
    )

    history_text = (
        "\n".join([f"- {fact}" for fact in historical_facts])
        if historical_facts
        else "No historical memory found for this identity."
    )

    user_prompt = (
        f"Identity Name: {matched_identity.get('name')}\n"
        f"Type: {matched_identity.get('type', 'Unknown')}\n"
        f"Description: {matched_identity.get('description', 'N/A')}\n"
        f"Current Permissions: {', '.join(current_permissions) if current_permissions else 'None'}\n\n"
        f"Recalled Hindsight History:\n{history_text}\n\n"
        "Perform the security risk analysis and return the JSON result."
    )

    # 4. Invoke Groq LLM
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=GROQ_MODEL,
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        llm_output = chat_completion.choices[0].message.content or "{}"
        parsed = parse_llm_json_response(llm_output)

        risk_level = parsed.get("risk_level", "Medium")
        # Ensure proper casing for risk level
        if risk_level.upper() in ["HIGH", "MEDIUM", "LOW"]:
            risk_level = risk_level.capitalize()

        agent_analysis = parsed.get("agent_analysis", "Analysis completed.")

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Groq LLM analysis failed: {str(e)}"
        )

    # 5. Return the JSON response with exact specified keys
    return {
        "identity": matched_identity.get("name"),
        "risk_level": risk_level,
        "current_permissions": current_permissions,
        "historical_context": historical_facts,
        "agent_analysis": agent_analysis
    }
