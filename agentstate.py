from typing import List, Optional, TypedDict, Annotated
from pydantic import BaseModel, Field
import operator


class ResumeMetadata(BaseModel):
    """Complete resume metadata extracted and generated"""
    name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    github: Optional[str] = Field(default=None, description="GitHub profile link")
    linkedin: Optional[str] = Field(default=None, description="LinkedIn profile link")
    
    # Experience section
    experiences: List[dict] = Field(description="List of work experiences with company, role, duration, and achievements")
    
    # Education section
    education: List[dict] = Field(description="List of educational qualifications")
    
    # Projects (AI-generated based on job description)
    projects: List[dict] = Field(description="List of relevant projects with descriptions")
    
    # Technical skills (AI-generated based on job description)
    technical_skills: dict = Field(description="Technical skills categorized by type")
    
    # Soft skills
    soft_skills: List[str] = Field(default_factory=list, description="List of soft skills")
    
    # Positions of responsibility
    positions_of_responsibility: List[dict] = Field(default_factory=list, description="Leadership positions held")
    
    # Certifications
    certifications: List[dict] = Field(default_factory=list, description="Professional certifications")
    
    # Coding profiles
    coding_stats: Optional[dict] = Field(default=None, description="Coding platform statistics")

# LangGraph State
class AgentState(TypedDict):
    resume_text: str
    job_description: str
    extracted_info: Optional[dict]
    generated_projects: Optional[List[dict]]
    generated_skills: Optional[dict]
    resume_metadata: Optional[ResumeMetadata]
    latex_code: Optional[str]
    messages: Annotated[list, operator.add]