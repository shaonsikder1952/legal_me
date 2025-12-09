from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage
from PyPDF2 import PdfReader
import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Law Database
LAW_DATABASE = [
    {
        "id": "mietrecht_1",
        "title": "Mietrecht § 535 BGB",
        "description": "Basic rental law - landlord must provide the property in a usable condition",
        "url": "https://www.gesetze-im-internet.de/bgb/__535.html"
    },
    {
        "id": "mietrecht_2",
        "title": "Mietrecht § 556d BGB",
        "description": "Limits on agent fees (Maklergebühren)",
        "url": "https://www.gesetze-im-internet.de/bgb/__556d.html"
    },
    {
        "id": "arbeitsrecht_1",
        "title": "Arbeitsrecht § 611a BGB",
        "description": "Employment contract basics",
        "url": "https://www.gesetze-im-internet.de/bgb/__611a.html"
    },
    {
        "id": "arbeitsrecht_2",
        "title": "Kündigungsschutzgesetz",
        "description": "Protection against dismissal",
        "url": "https://www.gesetze-im-internet.de/kschg/"
    },
    {
        "id": "steuerrecht_1",
        "title": "Einkommensteuergesetz",
        "description": "Income tax law",
        "url": "https://www.gesetze-im-internet.de/estg/"
    },
    {
        "id": "agb_1",
        "title": "AGB-Recht § 307 BGB",
        "description": "Control of standard contract terms - unfair terms are invalid",
        "url": "https://www.gesetze-im-internet.de/bgb/__307.html"
    }
]

# Clause Database with patterns
CLAUSE_DATABASE = [
    {
        "pattern": r"(kündigungsfrist|notice period|termination).{0,50}(1 tag|1 day|sofort|immediate)",
        "risk": "violates",
        "explanation": "Unreasonably short termination period",
        "law_ref": "agb_1"
    },
    {
        "pattern": r"(haftung|liability).{0,50}(ausgeschlossen|excluded|keine)",
        "risk": "violates",
        "explanation": "Blanket liability exclusions are typically invalid",
        "law_ref": "agb_1"
    },
    {
        "pattern": r"(kaution|deposit|security).{0,50}([4-9]|[1-9][0-9]).{0,20}(monat|month)",
        "risk": "violates",
        "explanation": "Deposit exceeds legal maximum of 3 months rent",
        "law_ref": "mietrecht_1"
    },
    {
        "pattern": r"(maklergebühr|agent fee|commission).{0,50}mieter|tenant.{0,50}pay",
        "risk": "attention",
        "explanation": "Tenant may not have to pay agent fees under certain circumstances",
        "law_ref": "mietrecht_2"
    },
    {
        "pattern": r"(probezeit|probation).{0,50}([7-9]|[1-9][0-9]).{0,20}(monat|month)",
        "risk": "violates",
        "explanation": "Probation period exceeds legal maximum of 6 months",
        "law_ref": "arbeitsrecht_1"
    },
    {
        "pattern": r"(vertrag|contract).{0,50}(automatisch|automatically|auto).{0,50}(verlänger|renew|extend)",
        "risk": "attention",
        "explanation": "Auto-renewal clause - ensure you can cancel in time",
        "law_ref": "agb_1"
    },
    {
        "pattern": r"(kündigung|cancellation).{0,50}(schriftlich|written|mail)",
        "risk": "safe",
        "explanation": "Standard cancellation clause requiring written notice",
        "law_ref": "agb_1"
    },
    {
        "pattern": r"(miete|rent).{0,50}(pünktlich|on time|fällig|due)",
        "risk": "safe",
        "explanation": "Standard payment terms",
        "law_ref": "mietrecht_1"
    }
]

# Alternative Resources
ALTERNATIVE_DATABASE = [
    {
        "category": "rental",
        "resources": [
            {"name": "Mieterschutzbund", "url": "https://www.mieterschutzbund.de"},
            {"name": "Safe Rental Templates", "url": "https://www.immobilienscout24.de/ratgeber"}
        ]
    },
    {
        "category": "employment",
        "resources": [
            {"name": "Arbeitsagentur", "url": "https://www.arbeitsagentur.de"},
            {"name": "DGB (Labor Union)", "url": "https://www.dgb.de"}
        ]
    },
    {
        "category": "general",
        "resources": [
            {"name": "Verbraucherzentrale", "url": "https://www.verbraucherzentrale.de"},
            {"name": "Report Issues", "url": "https://www.verbraucherzentrale.de/beschwerde"}
        ]
    }
]

# Pydantic Models
class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_message: str
    ai_response: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

class ContractAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    extracted_text: str
    document_type: str
    risk_level: str
    clauses_safe: List[dict]
    clauses_attention: List[dict]
    clauses_violates: List[dict]
    summary: str
    recommendations: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

@api_router.get("/")
async def root():
    return {"message": "LegalMe API"}

@api_router.get("/laws")
async def get_laws():
    return LAW_DATABASE

@api_router.get("/topics")
async def get_topics():
    return [
        {"id": "rental", "name": "Rental Law", "icon": "home"},
        {"id": "employment", "name": "Employment Law", "icon": "briefcase"},
        {"id": "subscription", "name": "Subscription Law", "icon": "file-text"},
        {"id": "tax", "name": "Tax Law", "icon": "calculator"}
    ]

@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Create system message with law database context
        law_context = "\n".join([f"- {law['title']}: {law['description']} (Link: {law['url']})" for law in LAW_DATABASE])
        
        system_message = f"""You are LegalMe, a friendly German legal assistant. 

You MUST format ALL responses using Cursor-style markdown:
- Use # ## ### for headers
- Use **bold** for key points
- Use bullet lists with -
- Use --- for horizontal dividers
- ALWAYS embed links as HTML: <a href=\"URL\">Clickable Text</a>
- NEVER show raw URLs

Available German laws:
{law_context}

For EVERY response, you MUST include this exact section at the end:

---

## Next Steps
1. Report this issue: <a href=\"https://www.verbraucherzentrale.de/beschwerde\">Open reporting page</a>
2. See safer alternatives: <a href=\"https://www.verbraucherzentrale.de\">View safer options</a>
3. Check another document: <a href=\"/contract\">Upload another file</a>

Be concise, professional, and friendly. Always reference actual laws from the database when relevant."""
        
        # Initialize chat
        chat_client = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=request.session_id,
            system_message=system_message
        )
        chat_client.with_model("gemini", "gemini-2.0-flash")
        
        # Send message
        user_msg = UserMessage(text=request.message)
        ai_response = await chat_client.send_message(user_msg)
        
        # Store in database
        chat_doc = ChatMessage(
            session_id=request.session_id,
            user_message=request.message,
            ai_response=ai_response
        )
        doc = chat_doc.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.chat_messages.insert_one(doc)
        
        return ChatResponse(response=ai_response, session_id=request.session_id)
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/contract/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    try:
        # Extract text from PDF
        content = await file.read()
        pdf_reader = PdfReader(io.BytesIO(content))
        
        extracted_text = ""
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() + "\n"
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Analyze clauses
        clauses_safe = []
        clauses_attention = []
        clauses_violates = []
        
        text_lower = extracted_text.lower()
        for clause_pattern in CLAUSE_DATABASE:
            matches = re.finditer(clause_pattern["pattern"], text_lower, re.IGNORECASE)
            for match in matches:
                snippet = extracted_text[max(0, match.start()-50):min(len(extracted_text), match.end()+50)]
                law_ref = next((law for law in LAW_DATABASE if law["id"] == clause_pattern.get("law_ref")), None)
                
                clause_info = {
                    "clause": snippet.strip(),
                    "explanation": clause_pattern["explanation"],
                    "law": law_ref["title"] if law_ref else "General Legal Principle",
                    "law_link": law_ref["url"] if law_ref else "#"
                }
                
                if clause_pattern["risk"] == "safe":
                    clauses_safe.append(clause_info)
                elif clause_pattern["risk"] == "attention":
                    clauses_attention.append(clause_info)
                elif clause_pattern["risk"] == "violates":
                    clauses_violates.append(clause_info)
        
        # Determine overall risk
        if clauses_violates:
            risk_level = "high"
        elif clauses_attention:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Generate AI summary using Gemini
        law_context = "\n".join([f"- {law['title']}: {law['description']}" for law in LAW_DATABASE])
        summary_prompt = f"""Analyze this contract and provide:
1. Document type (rental/employment/subscription/other)
2. A 3-5 sentence summary
3. Key recommendations

Contract text:
{extracted_text[:2000]}

Available laws:
{law_context}

Provide response in this format:
TYPE: [type]
SUMMARY: [summary]
RECOMMENDATIONS: [recommendations]"""
        
        chat_client = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"contract_{uuid.uuid4()}",
            system_message="You are a legal document analyzer. Be concise and professional."
        )
        chat_client.with_model("gemini", "gemini-2.0-flash")
        
        ai_analysis = await chat_client.send_message(UserMessage(text=summary_prompt))
        
        # Parse AI response
        doc_type = "general"
        summary = "Document analysis complete."
        recommendations = "Review all highlighted clauses carefully."
        
        if "TYPE:" in ai_analysis:
            doc_type = ai_analysis.split("TYPE:")[1].split("\n")[0].strip()
        if "SUMMARY:" in ai_analysis:
            summary = ai_analysis.split("SUMMARY:")[1].split("RECOMMENDATIONS:")[0].strip()
        if "RECOMMENDATIONS:" in ai_analysis:
            recommendations = ai_analysis.split("RECOMMENDATIONS:")[1].strip()
        
        # Create analysis document
        analysis = ContractAnalysis(
            filename=file.filename,
            extracted_text=extracted_text,
            document_type=doc_type,
            risk_level=risk_level,
            clauses_safe=clauses_safe,
            clauses_attention=clauses_attention,
            clauses_violates=clauses_violates,
            summary=summary,
            recommendations=recommendations
        )
        
        # Store in database
        doc = analysis.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.contract_analyses.insert_one(doc)
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Contract analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/contract/{contract_id}")
async def get_contract_analysis(contract_id: str):
    analysis = await db.contract_analyses.find_one({"id": contract_id}, {"_id": 0})
    if not analysis:
        raise HTTPException(status_code=404, detail="Contract analysis not found")
    return analysis

@api_router.get("/alternatives/{category}")
async def get_alternatives(category: str):
    alt = next((a for a in ALTERNATIVE_DATABASE if a["category"] == category), None)
    if not alt:
        return ALTERNATIVE_DATABASE[2]  # Return general resources
    return alt

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()