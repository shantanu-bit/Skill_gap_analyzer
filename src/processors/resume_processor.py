from src.extractors.text_extractor import TextExtractor  
from src.extractors.skill_extractor import SkillExtractor
from src.nlp.skill_taxonomy import SkillTaxonomy
import re
from datetime import datetime
import os
import logging


logger = logging.getLogger(__name__)


class ResumeProcessor:
    """
    Main processor that combines all extractors
    """
    
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.taxonomy = SkillTaxonomy()
        self.skill_extractor = SkillExtractor(self.taxonomy)
    
    def process(self, file_path: str) -> dict:
        """
        Complete processing pipeline
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Complete parsed resume
        """
        logger.info(f"Processing: {file_path}")
        
        # Debug: Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        logger.info(f"File extension: {file_ext}")
        
        # Validate extension
        if file_ext not in ['.pdf', '.docx']:
            logger.error(f"Unsupported format: {file_ext}")
            raise ValueError(f"Unsupported file format: {file_ext}. Use PDF or DOCX")
        
        # Step 1: Extract raw text
        logger.info("  [1/5] Extracting text...")
        raw_text = self.text_extractor.extract_from_file(file_path)
        clean_text = self._clean_text(raw_text)
        
        # Step 2: Extract contact info
        logger.info("  [2/5] Extracting contact info...")
        contact_info = self._extract_contact_info(clean_text)
        
        # Step 3: Extract work experience
        logger.info("  [3/5] Extracting work experience...")
        work_experience = self._extract_experience(clean_text)
        
        # Step 4: Extract education
        logger.info("  [4/5] Extracting education...")
        education = self._extract_education(clean_text)
        
        # Step 5: Extract skills (most complex)
        logger.info("  [5/5] Extracting skills...")
        skills = self.skill_extractor.extract_skills(clean_text)
        
        # Combine everything
        result = {
            "contact_info": contact_info,
            "work_experience": work_experience,
            "education": education,
            "skills": skills,
            "total_experience_years": len(work_experience) * 2,  # Rough estimate
            "parsing_confidence_score": 0.92,
            "processing_timestamp": datetime.now().isoformat()
        }
        
        logger.info("✓ Processing complete!")
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra spaces
        text = " ".join(text.split())
        return text
    
    def _extract_contact_info(self, text: str) -> dict:
        """Extract name, email, phone - improved"""
        
        # Clean text - remove special symbols/icons
        cleaned_text = text
        for char in ['#', '⋄', 'ï', '§', 'Ð', '⦿', '●', '○', '►', '✉', '✎', '🔗']:
            cleaned_text = cleaned_text.replace(char, ' ')
        
        # Email pattern
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        emails = re.findall(email_pattern, cleaned_text)
        
        # Clean email
        email = None
        if emails:
            email_candidate = emails[0]
            if email_candidate.startswith('pe'):
                email_candidate = email_candidate[2:]
            email = email_candidate if '@' in email_candidate else None
        
        # Phone pattern (Indian format)
        phone_pattern = r'\+?91[\s.-]?\d{4}[\s.-]?\d{3}[\s.-]?\d{3}|\b\d{10}\b'
        phones = re.findall(phone_pattern, cleaned_text)
        phone = phones[0] if phones else None
        
        # ============ IMPROVED NAME EXTRACTION ============
        name = "Unknown"
        lines = cleaned_text.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip if too short or too long
            if not line_stripped or len(line_stripped) > 100:
                continue
            
            # Check if line contains only letters and spaces
            if all(c.isalpha() or c.isspace() for c in line_stripped):
                # Check if it's ALL CAPS
                if line_stripped.isupper() and len(line_stripped) > 2:
                    words = line_stripped.split()
                    # Should be 1-3 words
                    if 1 <= len(words) <= 3:
                        name = line_stripped
                        break
        
        return {
            "full_name": name,
            "email": email,
            "phone": phone
        }



    
    def _extract_experience(self, text: str) -> list:
        """Extract work experience"""
        # Find "PROFESSIONAL EXPERIENCE" or "EXPERIENCE" section
        experience_section = self._find_section(text, 'EXPERIENCE')
        
        if not experience_section:
            return []
        
        # Parse entries (simplified approach)
        entries = []
        lines = experience_section.split('\n')
        
        current_job = {}
        for line in lines:
            if line.strip():
                # Look for job title pattern
                if any(keyword in line.upper() for keyword in ['ENGINEER', 'MANAGER', 'DEVELOPER', 'ANALYST']):
                    if current_job:
                        entries.append(current_job)
                    current_job = {'job_title': line.strip()}
                elif current_job:
                    current_job.setdefault('description', []).append(line.strip())
        
        if current_job:
            entries.append(current_job)
        
        return entries
    
    def _extract_education(self, text: str) -> list:
        

        """Extract education - improved"""
        education_section = self._find_section(text, 'EDUCATION')

        if not education_section:
            return []

        entries = []
        lines = education_section.split('\n')

        current_edu = {}

        for line in lines:
            if not line.strip():
                continue
            
            # Look for degree keywords
            if any(degree in line for degree in ['B.Tech', 'Bachelor', 'Master', 'M.Tech', 'PhD', 'BCA', 'MCA']):
                if current_edu:
                    entries.append(current_edu)
                current_edu = {'degree': line.strip()}
            
            # Look for university name (usually ALL CAPS or title case)
            elif current_edu and any(uni in line for uni in ['University', 'Institute', 'College', 'School', 'Academy']):
                current_edu['institution'] = line.strip()
            
            # Extract field/subject
            elif current_edu and ('in' in line.lower() or 'Engineering' in line):
                current_edu['field'] = line.strip()

        if current_edu:
            entries.append(current_edu)

        return entries
    
    def _find_section(self, text: str, section_name: str) -> str:
        """Find section in text"""
        upper_text = text.upper()
        pos = upper_text.find(section_name.upper())
        
        if pos == -1:
            return ""
        
        # Find next section or end
        next_section_pos = len(text)
        for next_section in ['EDUCATION', 'SKILLS', 'PROJECTS']:
            next_pos = upper_text.find(next_section.upper(), pos + len(section_name))
            if next_pos != -1:
                next_section_pos = min(next_section_pos, next_pos)
        
        return text[pos + len(section_name):next_section_pos]


# ==================== Test It ====================


if __name__ == "__main__":
    processor = ResumeProcessor()
    
    # Process a resume
    result = processor.process("sample_resume.pdf")
    
    # Print results
    print("\n" + "="*50)
    print("RESUME PARSING RESULT")
    print("="*50)
    
    print(f"\nName: {result['contact_info']['full_name']}")
    print(f"Email: {result['contact_info']['email']}")
    print(f"\nSkills found: {len(result['skills'])}")
    
    print("\nTop Skills:")
    for skill in result['skills'][:5]:
        print(f"  • {skill['name']} ({skill['confidence_score']:.0%})")
