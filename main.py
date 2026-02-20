"""
AI Resume Generator Backend - Vercel Compatible
Uses LangGraph for agentic workflow to generate tailored resumes
Compiles LaTeX using online API (no local dependencies)
Structured responses via LangGraph's with_structured_output (tool-call based)
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import pdfplumber
import os
from pathlib import Path
import tempfile
import json
from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse
from agentstate import AgentState, ResumeMetadata
from latex_handler import generate_latex
from online_compiler import compile_latex_online
import logging

load_dotenv()

app = FastAPI(title="AI Resume Generator")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatBedrockConverse(
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name="us-east-1",
)

# ──────────────────────────────────────────────
# Pydantic schemas for structured output
# ──────────────────────────────────────────────

class WorkExperience(BaseModel):
    company: str = Field(description="Company or organisation name")
    role: str = Field(description="Job title / role")
    duration: str = Field(description="Employment period, e.g. 'Jan 2022 – Mar 2024'")
    achievements: List[str] = Field(description="Bullet-point achievements / responsibilities")

class Education(BaseModel):
    institution: str
    degree: str
    duration: str

class Project(BaseModel):
    name: str = Field(description="Project title")
    technologies: List[str] = Field(description="Up to 3 key technologies used")
    date: str = Field(description="Completion month and year, e.g. 'December 2024'")
    achievements: List[str] = Field(description="2-3 bullet-point achievements with metrics")

class PositionOfResponsibility(BaseModel):
    organization: str
    role: str
    duration: str
    location: Optional[str] = ""
    description: str = Field(description="Summary of responsibilities")

class Certification(BaseModel):
    name: str
    issuer: Optional[str] = ""
    date: Optional[str] = ""

class CodingStats(BaseModel):
    platform: str
    description: str

class ExtractedResumeInfo(BaseModel):
    """Complete structured information extracted from a resume."""
    name: str
    email: str
    phone: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    experiences: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    technical_skills: dict = Field(
        default_factory=dict,
        description="Dict of category → list of skill strings, e.g. {'Languages': ['Python']}"
    )
    soft_skills: List[str] = Field(default_factory=list)
    positions_of_responsibility: List[PositionOfResponsibility] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    coding_stats: Optional[List[CodingStats]] = None

class GeneratedProjects(BaseModel):
    """Three projects tailored to the job description."""
    projects: List[Project] = Field(description="Exactly 3 generated projects")

class TechnicalSkills(BaseModel):
    """Technical skills grouped by category."""
    skills: dict = Field(
        description=(
            "Keys are category names (e.g. 'Languages/Frameworks', 'Tools', 'Concepts'), "
            "values are lists of skill strings. Max 7 items per category."
        )
    )


# ──────────────────────────────────────────────
# Structured-output LLM bindings
# (each uses a tool call under the hood)
# ──────────────────────────────────────────────

extractor_llm   = llm.with_structured_output(ExtractedResumeInfo)
project_llm     = llm.with_structured_output(GeneratedProjects)
skills_llm      = llm.with_structured_output(TechnicalSkills)


# ──────────────────────────────────────────────
# Node 1: Extract information from existing resume
# ──────────────────────────────────────────────

def extract_resume_info(state: AgentState) -> AgentState:
    """Extract user information from existing resume using structured output."""

    messages = [
        SystemMessage(content=(
            "You are an expert at extracting structured information from resumes. "
            "Extract ALL information present in the resume text. "
            "If a field is absent, use an empty list or null as appropriate. "
            "Never fabricate information that is not in the resume."
        )),
        HumanMessage(content=f"Resume text:\n\n{state['resume_text']}")
    ]

    # with_structured_output uses a tool call → returns a validated Pydantic object
    extracted: ExtractedResumeInfo = extractor_llm.invoke(messages)

    return {
        **state,
        "extracted_info": extracted.model_dump(),
        "messages": [HumanMessage(content="Extracted information from resume")]
    }


# ──────────────────────────────────────────────
# Node 2: Generate relevant projects
# ──────────────────────────────────────────────

def generate_projects(state: AgentState) -> AgentState:
    """Generate 3 relevant projects tailored to the job description."""

    experience_summary = json.dumps(
        state["extracted_info"].get("experiences", []), indent=2
    )

    messages = [
        SystemMessage(content=(
            "You are an expert at creating compelling project descriptions for resumes. "
            "Generate exactly 3 technical projects that align with the job description and "
            "the candidate's existing experience level. "
            "Each project must have 2-3 achievement bullet points with specific metrics and numbers. "
            "Keep the technologies list to at most 3 items per project. "
            "Make the projects realistic and impressive."
        )),
        HumanMessage(content=(
            f"Job Description:\n{state['job_description']}\n\n"
            f"Candidate's existing experience:\n{experience_summary}\n\n"
            "Generate 3 relevant projects."
        ))
    ]

    result: GeneratedProjects = project_llm.invoke(messages)

    return {
        **state,
        "generated_projects": [p.model_dump() for p in result.projects],
        "messages": [HumanMessage(content=f"Generated {len(result.projects)} relevant projects")]
    }


# ──────────────────────────────────────────────
# Node 3: Generate relevant technical skills
# ──────────────────────────────────────────────

def generate_skills(state: AgentState) -> AgentState:
    """Generate relevant technical skills based on the job description."""

    messages = [
        SystemMessage(content=(
            "You are an expert at identifying key technical skills for job applications. "
            "Based on the job description, return a comprehensive set of technical skills "
            "grouped into categories such as 'Languages/Frameworks', 'Tools', and 'Concepts'. "
            "Limit each category to at most 7 items. "
            "Only include skills that are genuinely relevant to the role."
        )),
        HumanMessage(content=f"Job Description:\n{state['job_description']}")
    ]

    result: TechnicalSkills = skills_llm.invoke(messages)

    return {
        **state,
        "generated_skills": result.skills,
        "messages": [HumanMessage(content="Generated relevant technical skills")]
    }


# ──────────────────────────────────────────────
# Node 4: Assemble resume metadata
# ──────────────────────────────────────────────

def create_metadata(state: AgentState) -> AgentState:
    """Assemble structured resume metadata from all previous nodes."""

    extracted = state["extracted_info"]

    # --- Experiences (already validated by Pydantic in Node 1) ---
    formatted_experiences = [
        {
            "company":      exp.get("company", ""),
            "role":         exp.get("role", ""),
            "duration":     exp.get("duration", ""),
            "achievements": exp.get("achievements", [])
        }
        for exp in extracted.get("experiences", [])
    ]

    # --- Positions of responsibility ---
    formatted_por = [
        {
            "organization": por.get("organization", ""),
            "role":         por.get("role", ""),
            "duration":     por.get("duration", ""),
            "location":     por.get("location", ""),
            "description":  por.get("description", "")
        }
        for por in extracted.get("positions_of_responsibility", [])
    ]

    # --- Certifications (already dicts from Pydantic model) ---
    formatted_certifications = [
        {
            "name":   cert.get("name", ""),
            "issuer": cert.get("issuer", ""),
            "date":   cert.get("date", "")
        }
        for cert in extracted.get("certifications", [])
    ]

    # --- Projects: prefer AI-generated ones over extracted ---
    raw_projects = (
        state["generated_projects"]
        if state.get("generated_projects")
        else extracted.get("projects", [])
    )
    formatted_projects = [
        {
            "name":         proj.get("name", ""),
            "technologies": proj.get("technologies", []),
            "date":         proj.get("date", ""),
            "achievements": proj.get("achievements", [])
        }
        for proj in raw_projects
    ]

    # --- Coding stats: convert list-of-dicts → single dict if needed ---
    raw_coding = extracted.get("coding_stats")
    if isinstance(raw_coding, list):
        coding_stats = {item["platform"]: item["description"] for item in raw_coding if isinstance(item, dict)}
    elif isinstance(raw_coding, dict):
        coding_stats = raw_coding
    else:
        coding_stats = None

    metadata = ResumeMetadata(
        name=extracted.get("name", "John Doe"),
        email=extracted.get("email", "john@example.com"),
        phone=extracted.get("phone"),
        github=extracted.get("github"),
        linkedin=extracted.get("linkedin"),
        experiences=formatted_experiences,
        education=extracted.get("education", []),
        projects=formatted_projects,
        technical_skills=state.get("generated_skills") or extracted.get("technical_skills", {}),
        soft_skills=extracted.get("soft_skills", []),
        positions_of_responsibility=formatted_por,
        certifications=formatted_certifications,
        coding_stats=coding_stats,
    )

    return {
        **state,
        "resume_metadata": metadata,
        "messages": [HumanMessage(content="Created resume metadata")]
    }


# ──────────────────────────────────────────────
# LangGraph workflow
# ──────────────────────────────────────────────

def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("extract_info",      extract_resume_info)
    workflow.add_node("generate_projects", generate_projects)
    workflow.add_node("generate_skills",   generate_skills)
    workflow.add_node("create_metadata",   create_metadata)
    workflow.add_node("generate_latex",    generate_latex)

    workflow.set_entry_point("extract_info")
    workflow.add_edge("extract_info",      "generate_projects")
    workflow.add_edge("generate_projects", "generate_skills")
    workflow.add_edge("generate_skills",   "create_metadata")
    workflow.add_edge("create_metadata",   "generate_latex")
    workflow.add_edge("generate_latex",    END)

    return workflow.compile()


graph = build_graph()


# ──────────────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────────────

@app.post("/api/generate-resume")
async def generate_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """Generate a tailored resume from an existing resume PDF + job description."""
    try:
        resume_text = ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await resume_file.read()
            tmp_file.write(content)
            tmp_filename = tmp_file.name

        try:
            with pdfplumber.open(tmp_filename) as pdf:
                for page in pdf.pages:
                    resume_text += page.extract_text() + "\n"
        finally:
            if os.path.exists(tmp_filename):
                os.unlink(tmp_filename)

        initial_state = {
            "resume_text":        resume_text,
            "job_description":    job_description,
            "extracted_info":     None,
            "generated_projects": None,
            "generated_skills":   None,
            "resume_metadata":    None,
            "latex_code":         None,
            "messages":           []
        }

        final_state = graph.invoke(initial_state)

        logger.info("=== FINAL STATE DEBUG ===")
        logger.info(f"Experiences : {len(final_state['resume_metadata'].experiences)}")
        logger.info(f"Projects    : {len(final_state['resume_metadata'].projects)}")

        return JSONResponse({
            "success":   True,
            "metadata":  final_state["resume_metadata"].model_dump() if final_state["resume_metadata"] else None,
            "latex_code": final_state["latex_code"],
            "debug": {
                "extracted_experiences_count": len(final_state["extracted_info"].get("experiences", [])),
                "generated_projects_count":    len(final_state["generated_projects"] or []),
                "final_experiences_count":     len(final_state["resume_metadata"].experiences) if final_state["resume_metadata"] else 0,
                "final_projects_count":        len(final_state["resume_metadata"].projects)    if final_state["resume_metadata"] else 0,
            }
        })

    except Exception as e:
        logger.exception("Error in generate_resume")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/compile-latex")
async def compile_latex(latex_code: str = Form(...)):
    """Compile LaTeX to PDF via online API (Vercel-compatible)."""
    try:
        logger.info("Starting online LaTeX compilation...")
        success, pdf_bytes, error = compile_latex_online(latex_code, timeout=45)

        if success:
            import base64
            return JSONResponse({
                "success":    True,
                "pdf_base64": base64.b64encode(pdf_bytes).decode()
            })
        else:
            logger.error(f"Compilation failed: {error}")
            return JSONResponse({
                "success":    False,
                "error":      error,
                "diagnostic": "Online LaTeX compilation failed. The LaTeX code may have syntax errors."
            }, status_code=500)

    except Exception as e:
        logger.exception("Unexpected error in compile_latex")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "compiler": "online", "vercel_compatible": True}


handler = app  # Vercel entry point

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)