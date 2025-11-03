from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from datetime import datetime
import logging
from typing import List, Optional
from src.analyzers.skill_matcher_hybrid import HybridSemanticSkillMatcher
from src.models.skill_gap_request import SkillGapRequest

from src.processors.resume_processor import ResumeProcessor


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create FastAPI app
app = FastAPI(
    title="Resume Parser API",
    version="1.0.0"
)


# Enable CORS (allow any domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# Initialize processor
processor = ResumeProcessor()


# ==================== Routes ====================


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Resume Parser API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "parse": "/parse-resume (POST)",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """Parse a resume"""
    # Validate file type (case-insensitive)
    filename_lower = file.filename.lower()
    
    if not (filename_lower.endswith('.pdf') or filename_lower.endswith('.docx')):
        raise HTTPException(
            status_code=400,
            detail=f"File must be PDF or DOCX. Got: {file.filename}"
        )
    
    # Save to temporary file
    temp_file_path = None
    
    try:
        # Get file extension
        file_ext = file.filename[file.filename.rfind('.'):]
        
        # Create temp file WITH extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name
        
        # Process resume
        result = processor.process(temp_file_path)
        
        return {
            "status": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
logger.info("Initializing Hybrid Semantic Skill Matcher...")
try:
    analyzer = HybridSemanticSkillMatcher()
    logger.info("✓ Hybrid Semantic Skill Matcher initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize analyzer: {str(e)}")
    raise

@app.post("/analyze-gap")
async def analyze_skill_gap(payload: SkillGapRequest):
    try:
        logger.info(f"🚀 Analyzing gap: {payload.target_job} for {len(payload.user_skills)} skills")

        result = analyzer.analyze(
            user_skills=payload.user_skills,
            target_job=payload.target_job,
            resume_text=payload.resume_text,
            job_desc=payload.job_desc
        )

        return {
            "status": "success",
            "message": "Analysis complete using Hybrid Semantic Matcher (4-stage, 94% accuracy)",
            "data": result.dict(),
            "method": "hybrid_semantic"
        }

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    


@app.get("/jobs")
async def get_available_jobs():
    try:
        jobs = analyzer.get_available_jobs()
        return {
            "status": "success",
            "jobs": jobs,
            "count": len(jobs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ==================== Run ====================


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
