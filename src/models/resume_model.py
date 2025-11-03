
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

# Enums (Categories)

class SkillCategory(str, Enum):
    """What type of skill is it?"""
    TECHNICAL = "technical"      # Python, Java, etc.
    SOFT = "soft"                # Leadership, Communication
    DOMAIN = "domain"            # Healthcare, Finance

# Skill Data Model 

class Skill(BaseModel):
    """Represents a single skill"""
    name: str                              # "Python"
    category: SkillCategory                # "technical"
    confidence_score: float                # 0.95 (95% confident)
    mentioned_in: Optional[str] = None     # "Professional Experience"
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Python",
                "category": "technical",
                "confidence_score": 0.95,
                "mentioned_in": "Professional Experience"
            }
        }

# ==================== Work Experience Model ====================

class WorkExperience(BaseModel):
    """Represents a job"""
    company: str                           # "Google"
    job_title: str                         # "Senior Engineer"
    start_date: Optional[str] = None       # "2021-01"
    end_date: Optional[str] = None         # "2023-06"
    responsibilities: Optional[List[str]] = None

# ==================== Education Model ====================

class Education(BaseModel):
    """Represents education"""
    institution: str                       # "IIT Delhi"
    degree: str                            # "B.Tech"
    field_of_study: str                    # "Computer Science"
    start_date: Optional[str] = None
    end_date: Optional[str] = None

# ==================== Contact Info Model ====================

class ContactInfo(BaseModel):
    """Contact details extracted from resume"""
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None

# ==================== Final Resume Result ====================

class ResumeParsingResult(BaseModel):
    """Complete resume parsing result"""
    contact_info: ContactInfo
    work_experience: List[WorkExperience]
    education: List[Education]
    skills: List[Skill]
    total_experience_years: float
    parsing_confidence_score: float