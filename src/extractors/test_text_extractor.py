from src.extractors.text_extractor import TextExtractor

def test_pdf_extraction():
    extractor = TextExtractor()
    text = extractor.extract_from_pdf("test_resume.pdf")
    
    assert len(text) > 0, "No text extracted"
    assert isinstance(text, str), "Not a string"
    
    print("✓ PDF extraction works!")

def test_docx_extraction():
    extractor = TextExtractor()
    text = extractor.extract_from_docx("test_resume.docx")
    
    assert len(text) > 0, "No text extracted"
    
    print("✓ DOCX extraction works!")

if __name__ == "__main__":
    test_pdf_extraction()
    test_docx_extraction()