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
from pdf_generator import generate_contract_pdf

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

# Comprehensive Trusted Resources Database
TRUSTED_LINKS_DATABASE = {
    "rental": {
        "authorities": [
            {"name": "Tenant Protection Association (Mieterschutzbund)", "url": "https://www.mieterschutzbund.de"},
            {"name": "Berlin Tenant Advisory Service", "url": "https://www.berlin.de/sen/stadtentwicklung/wohnen/mieterschutz/"},
            {"name": "Hamburg Tenant Advisory", "url": "https://www.hamburg.de/mieterberatung/"}
        ],
        "alternatives": [
            {"name": "Safer rental listings on ImmobilienScout24", "url": "https://www.immobilienscout24.de"},
            {"name": "Fair rental contract templates", "url": "https://www.mietrecht.de/mustervertrag/"},
            {"name": "Rental law information portal", "url": "https://www.mietrecht.de"}
        ],
        "report": [
            {"name": "Report unfair rental practices", "url": "https://www.verbraucherzentrale.de/beschwerde"},
            {"name": "File complaint with tenant association", "url": "https://www.mieterbund.de/beratung.html"}
        ]
    },
    "employment": {
        "authorities": [
            {"name": "Federal Employment Agency (Bundesagentur für Arbeit)", "url": "https://www.arbeitsagentur.de"},
            {"name": "DGB Labor Union", "url": "https://www.dgb.de"},
            {"name": "Employee Rights Information", "url": "https://www.bmas.de/DE/Arbeit/Arbeitsrecht/arbeitsrecht.html"}
        ],
        "alternatives": [
            {"name": "Fair employment contract templates", "url": "https://www.arbeitsvertrag.org"},
            {"name": "Job search on Federal Employment Agency", "url": "https://www.arbeitsagentur.de/jobsuche/"},
            {"name": "Employment rights guide", "url": "https://www.dgb.de/themen/arbeitsrecht"}
        ],
        "report": [
            {"name": "Report unfair dismissal", "url": "https://www.dgb.de/service/kontakt"},
            {"name": "File workplace complaint", "url": "https://www.bmas.de/DE/Service/Kontakt/kontakt.html"}
        ]
    },
    "immigration": {
        "authorities": [
            {"name": "Immigration Office Berlin", "url": "https://service.berlin.de/dienstleistung/324284/"},
            {"name": "Federal Office for Migration (BAMF)", "url": "https://www.bamf.de"},
            {"name": "Make Your Way in Germany", "url": "https://www.make-it-in-germany.com"}
        ],
        "alternatives": [
            {"name": "Visa and residence permit guide", "url": "https://www.germany.info/us-en/service/visa"},
            {"name": "Integration courses", "url": "https://www.bamf.de/EN/Themen/Integration/integration_node.html"},
            {"name": "Recognition of foreign qualifications", "url": "https://www.anerkennung-in-deutschland.de/html/en/"}
        ],
        "report": [
            {"name": "Immigration consultation services", "url": "https://www.bamf.de/EN/Service/ServiceCenter/servicecenter-node.html"},
            {"name": "Legal advice for migrants", "url": "https://www.diakonie.de/angebote-und-hilfe/migration-und-integration"}
        ]
    },
    "subscription": {
        "authorities": [
            {"name": "Consumer Protection Center (Verbraucherzentrale)", "url": "https://www.verbraucherzentrale.de"},
            {"name": "German Consumer Protection Portal", "url": "https://www.verbraucher.de"}
        ],
        "alternatives": [
            {"name": "Fair subscription comparison", "url": "https://www.vergleich.de"},
            {"name": "Cancel subscriptions properly", "url": "https://www.verbraucherzentrale.de/wissen/vertraege-reklamation/kundenrechte/so-kuendigen-sie-richtig-6892"},
            {"name": "Subscription trap warning list", "url": "https://www.verbraucherzentrale.de/wissen/digitale-welt/onlinedienste/abofallen-im-internet-was-tun-5147"}
        ],
        "report": [
            {"name": "Report subscription scams", "url": "https://www.verbraucherzentrale.de/beschwerde"},
            {"name": "File complaint about unfair contracts", "url": "https://www.bundesnetzagentur.de/DE/Vportal/Verbraucher/Beschwerde/beschwerde-node.html"}
        ]
    },
    "tax": {
        "authorities": [
            {"name": "German Tax Office (Finanzamt)", "url": "https://www.finanzamt.de"},
            {"name": "Federal Ministry of Finance", "url": "https://www.bundesfinanzministerium.de"},
            {"name": "Tax advisor search", "url": "https://www.steuerkanzlei.de"}
        ],
        "alternatives": [
            {"name": "Tax declaration help", "url": "https://www.elster.de"},
            {"name": "Tax calculator", "url": "https://www.bmf-steuerrechner.de"},
            {"name": "Tax deduction guide", "url": "https://www.finanztip.de/steuererklaerung/"}
        ],
        "report": [
            {"name": "Tax consultation services", "url": "https://www.finanzamt.de/beratung"},
            {"name": "Report tax fraud", "url": "https://www.bundesfinanzministerium.de/Web/DE/Service/Kontakt/kontakt.html"}
        ]
    },
    "general": {
        "authorities": [
            {"name": "Consumer Protection Center", "url": "https://www.verbraucherzentrale.de"},
            {"name": "German Legal Portal", "url": "https://www.gesetze-im-internet.de"},
            {"name": "Federal Ministry of Justice", "url": "https://www.bmjv.de"}
        ],
        "alternatives": [
            {"name": "Legal advice directory", "url": "https://www.anwaltauskunft.de"},
            {"name": "Free legal help", "url": "https://www.rechtshilfe.de"},
            {"name": "Official forms and templates", "url": "https://www.formulare-bfinv.de"}
        ],
        "report": [
            {"name": "General complaint portal", "url": "https://www.verbraucherzentrale.de/beschwerde"},
            {"name": "File consumer complaint", "url": "https://www.bundesnetzagentur.de/DE/Vportal/Verbraucher/Beschwerde/beschwerde-node.html"}
        ]
    }
}

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
        # Create system message with law database context and trusted links
        law_context = "\n".join([f"- {law['title']}: {law['description']} (Link: {law['url']})" for law in LAW_DATABASE])
        
        # Create trusted links context for AI
        links_context = """
TRUSTED LINKS BY CATEGORY (Always use these for Next Steps):

RENTAL:
- Authorities: Mieterschutzbund (https://www.mieterschutzbund.de), Berlin Tenant Advisory (https://www.berlin.de/sen/stadtentwicklung/wohnen/mieterschutz/)
- Alternatives: ImmobilienScout24 (https://www.immobilienscout24.de), Rental templates (https://www.mietrecht.de/mustervertrag/)
- Report: Verbraucherzentrale (https://www.verbraucherzentrale.de/beschwerde)

EMPLOYMENT:
- Authorities: Bundesagentur für Arbeit (https://www.arbeitsagentur.de), DGB Union (https://www.dgb.de)
- Alternatives: Employment contract templates (https://www.arbeitsvertrag.org), Job search (https://www.arbeitsagentur.de/jobsuche/)
- Report: DGB contact (https://www.dgb.de/service/kontakt)

IMMIGRATION:
- Authorities: Immigration Berlin (https://service.berlin.de/dienstleistung/324284/), BAMF (https://www.bamf.de)
- Alternatives: Visa guide (https://www.germany.info/us-en/service/visa), Integration courses (https://www.bamf.de/EN/Themen/Integration/)
- Report: BAMF Service (https://www.bamf.de/EN/Service/ServiceCenter/servicecenter-node.html)

SUBSCRIPTION:
- Authorities: Verbraucherzentrale (https://www.verbraucherzentrale.de)
- Alternatives: Cancel guide (https://www.verbraucherzentrale.de/wissen/vertraege-reklamation/kundenrechte/so-kuendigen-sie-richtig-6892)
- Report: Consumer complaint (https://www.verbraucherzentrale.de/beschwerde)

TAX:
- Authorities: Finanzamt (https://www.finanzamt.de), Tax advisor (https://www.steuerkanzlei.de)
- Alternatives: ELSTER tax portal (https://www.elster.de), Tax calculator (https://www.bmf-steuerrechner.de)
- Report: Tax consultation (https://www.finanzamt.de/beratung)

GENERAL FALLBACK:
- Verbraucherzentrale (https://www.verbraucherzentrale.de)
- Legal portal (https://www.gesetze-im-internet.de)
- Legal advice (https://www.anwaltauskunft.de)
"""
        
        system_message = f"""You are LegalMe, a professional German legal assistant. 

CRITICAL: LINK FORMATTING RULES (NO EXCEPTIONS):
- ALWAYS use markdown link format: [Blue Clickable Text](URL)
- NEVER show raw URLs
- NEVER use HTML <a> tags
- Every law reference MUST be a masked link
- Example: [§ 535 BGB – Rental Agreements](https://www.gesetze-im-internet.de/bgb/__535.html)

FORMATTING RULES:
- Use # ## ### for headers
- Use **bold** for key points
- Use bullet lists with -
- Use --- for horizontal dividers

Available German laws:
{law_context}

{links_context}

CRITICAL: For EVERY response, you MUST:

1. DETECT USER INTENT from their question:
   - Keywords like "rent", "deposit", "landlord" → RENTAL
   - Keywords like "job", "employment", "contract", "dismissal" → EMPLOYMENT
   - Keywords like "visa", "immigration", "residence permit" → IMMIGRATION
   - Keywords like "subscription", "cancel", "abo" → SUBSCRIPTION
   - Keywords like "tax", "steuer", "finanzamt" → TAX
   - Otherwise → GENERAL

2. SELECT 3 RELEVANT LINKS from the trusted links based on detected intent

3. END YOUR RESPONSE WITH:

---

## Next Steps
### 1. [Action 1 - based on intent]
<a href=\"[RELEVANT_URL_1]\">[Descriptive Name 1]</a>

### 2. [Action 2 - based on intent]
<a href=\"[RELEVANT_URL_2]\">[Descriptive Name 2]</a>

### 3. Upload another document
<a href=\"/contract\">Analyze another contract</a>

EXAMPLE for rental question:
## Next Steps
### 1. Get tenant protection help
<a href=\"https://www.mieterschutzbund.de\">Tenant Protection Association</a>

### 2. View safer rental options
<a href=\"https://www.immobilienscout24.de\">Browse fair rental listings</a>

### 3. Upload another document
<a href=\"/contract\">Analyze another contract</a>

Be concise, professional, and friendly. Always reference actual laws and provide context-aware Next Steps."""
        
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
        
        # Generate AI summary using Gemini with intent detection
        law_context = "\n".join([f"- {law['title']}: {law['description']}" for law in LAW_DATABASE])
        summary_prompt = f"""Analyze this contract and provide:
1. Document type - Choose ONE: rental, employment, subscription, immigration, tax, other
2. A 3-5 sentence summary
3. Key recommendations

Contract text:
{extracted_text[:2000]}

Available laws:
{law_context}

Provide response in this EXACT format:
TYPE: [rental/employment/subscription/immigration/tax/other]
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

@api_router.get("/contract/{contract_id}/download")
async def download_contract_pdf(contract_id: str):
    analysis = await db.contract_analyses.find_one({"id": contract_id}, {"_id": 0})
    if not analysis:
        raise HTTPException(status_code=404, detail="Contract analysis not found")
    
    try:
        pdf_buffer = generate_contract_pdf(analysis)
        
        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=LegalMe_Report_{contract_id[:8]}.pdf"
            }
        )
    except Exception as e:
        logging.error(f"PDF generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@api_router.get("/alternatives/{category}")
async def get_alternatives(category: str):
    alt = next((a for a in ALTERNATIVE_DATABASE if a["category"] == category), None)
    if not alt:
        return ALTERNATIVE_DATABASE[2]  # Return general resources
    return alt

@api_router.get("/chat/history")
async def get_chat_history():
    """Get all unique chat sessions"""
    try:
        pipeline = [
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$session_id",
                "last_message": {"$first": "$user_message"},
                "timestamp": {"$first": "$timestamp"}
            }},
            {"$sort": {"timestamp": -1}},
            {"$limit": 50}
        ]
        
        sessions = await db.chat_messages.aggregate(pipeline).to_list(50)
        
        result = []
        for session in sessions:
            result.append({
                "session_id": session["_id"],
                "preview": session["last_message"][:60] + "..." if len(session["last_message"]) > 60 else session["last_message"],
                "timestamp": session["timestamp"]
            })
        
        return result
    except Exception as e:
        logging.error(f"Chat history error: {str(e)}")
        return []

@api_router.get("/chat/{session_id}/messages")
async def get_session_messages(session_id: str):
    """Get all messages for a specific session"""
    try:
        messages = await db.chat_messages.find(
            {"session_id": session_id},
            {"_id": 0}
        ).sort("timestamp", 1).to_list(1000)
        
        return messages
    except Exception as e:
        logging.error(f"Session messages error: {str(e)}")
        return []

@api_router.put("/chat/{session_id}/rename")
async def rename_session(session_id: str, request: dict):
    """Rename a chat session"""
    try:
        new_name = request.get("name", "")
        if not new_name:
            raise HTTPException(status_code=400, detail="Name is required")
        
        result = await db.chat_messages.update_many(
            {"session_id": session_id},
            {"$set": {"session_name": new_name}}
        )
        
        return {"success": True, "updated": result.modified_count}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Rename session error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/chat/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session"""
    try:
        result = await db.chat_messages.delete_many({"session_id": session_id})
        return {"success": True, "deleted": result.deleted_count}
    except Exception as e:
        logging.error(f"Delete session error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/contract/{contract_id}/chat", response_model=ChatResponse)
async def contract_chat(contract_id: str, request: ChatRequest):
    """Chat about a specific contract"""
    try:
        # Get contract analysis
        analysis = await db.contract_analyses.find_one({"id": contract_id}, {"_id": 0})
        if not analysis:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Create context with contract details
        contract_context = f"""
CONTRACT CONTEXT:
Type: {analysis.get('document_type', 'unknown')}
Risk Level: {analysis.get('risk_level', 'unknown')}
Summary: {analysis.get('summary', '')}

Safe Clauses: {len(analysis.get('clauses_safe', []))}
Attention Clauses: {len(analysis.get('clauses_attention', []))}
Violating Clauses: {len(analysis.get('clauses_violates', []))}

Recommendations: {analysis.get('recommendations', '')}

Contract Text (excerpt):
{analysis.get('extracted_text', '')[:1500]}
"""
        
        law_context = "\\n".join([f"- {law['title']}: {law['description']}" for law in LAW_DATABASE])
        
        system_message = f"""You are LegalMe, analyzing a specific contract for the user.

CONTRACT YOU ARE ANALYZING:
{contract_context}

Available German laws:
{law_context}

INSTRUCTIONS:
- Answer questions specifically about THIS contract
- Reference the clauses, risk levels, and findings from the analysis
- Use Cursor-style markdown formatting
- Provide clickable HTML links
- Be concise and helpful
- Always end with relevant Next Steps

User question: {request.message}"""
        
        # Initialize chat
        chat_client = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"contract_{contract_id}_{request.session_id}",
            system_message=system_message
        )
        chat_client.with_model("gemini", "gemini-2.0-flash")
        
        # Send message
        user_msg = UserMessage(text=request.message)
        ai_response = await chat_client.send_message(user_msg)
        
        # Store in contract chat history
        chat_doc = {
            "id": str(uuid.uuid4()),
            "contract_id": contract_id,
            "session_id": request.session_id,
            "user_message": request.message,
            "ai_response": ai_response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.contract_chats.insert_one(chat_doc)
        
        return ChatResponse(response=ai_response, session_id=request.session_id)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Contract chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/contract/{contract_id}/chat/history")
async def get_contract_chat_history(contract_id: str, session_id: str):
    """Get chat history for a contract"""
    try:
        messages = await db.contract_chats.find(
            {"contract_id": contract_id, "session_id": session_id},
            {"_id": 0}
        ).sort("timestamp", 1).to_list(1000)
        
        return messages
    except Exception as e:
        logging.error(f"Contract chat history error: {str(e)}")
        return []

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