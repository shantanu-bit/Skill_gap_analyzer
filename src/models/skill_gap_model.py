from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum



class SkillPriority(str, Enum):
    """Skill priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SkillGapItem(BaseModel):
    """Individual skill gap with advanced metrics"""
    skill_name: str
    priority: SkillPriority
    learning_hours: int
    salary_impact: float
    difficulty: int  # 1-10
    market_demand: float  # 0-1
    roi: float  # salary_impact / learning_hours
    weeks_to_proficiency: float
    job_relevance: float  # 0-1
    recommended_resources: List[str] = []
    extraction_method: str  # "ner", "semantic", "graph"
    confidence_score: float  # 0-1


class MatchedSkill(BaseModel):
    """Skill the user already has"""
    skill_name: str
    proficiency_level: str  # beginner, intermediate, advanced
    required_level: str
    extraction_method: str


class SkillGapAnalysisResult(BaseModel):
    """Complete gap analysis with advanced metrics"""
    job_title: str
    user_skill_count: int
    required_skill_count: int
    match_percentage: float
    
    matched_skills: List[MatchedSkill]
    skill_gaps: List[SkillGapItem]  # Sorted by ROI
    
    total_learning_hours: int
    estimated_weeks: float
    potential_salary_increase: float
    
    # New metrics
    average_difficulty: float
    market_demand_score: float
    recommendation: str
    learning_roadmap: List[str]  # Recommended order
    
    # Analysis details
    analysis_details: Dict = {}