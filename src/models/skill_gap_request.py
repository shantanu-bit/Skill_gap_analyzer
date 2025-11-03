from pydantic import BaseModel
from typing import List, Optional

class SkillGapRequest(BaseModel):
    user_skills: List[str]
    target_job: str
    resume_text: Optional[str] = None
    job_desc: Optional[str] = None
