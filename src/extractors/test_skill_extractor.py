from src.nlp.skill_taxonomy import SkillTaxonomy
from src.nlp.skill_extractor import SkillExtractor


def test_skill_extraction():
    taxonomy = SkillTaxonomy()
    extractor = SkillExtractor(taxonomy)
    
    sample_text = "I have 5 years of Python and Java experience. Expert in Django and React."
    
    skills = extractor.extract_skills(sample_text)
    
    # Should find at least 4 skills
    assert len(skills) >= 4, f"Expected 4+ skills, got {len(skills)}"
    
    # Check specific skills found
    skill_names = [s['name'] for s in skills]
    assert 'Python' in skill_names, "Should find Python"
    assert 'Java' in skill_names, "Should find Java"
    assert 'Django' in skill_names, "Should find Django"
    assert 'React' in skill_names, "Should find React"
    
    print("✓ Skill extraction works!")
    print(f"  Found {len(skills)} skills:")
    for skill in skills:
        print(f"    • {skill['name']} ({skill['confidence_score']:.0%})")

if __name__ == "__main__":
    test_skill_extraction()