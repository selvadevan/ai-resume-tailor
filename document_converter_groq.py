"""
Resume Data Extraction System - Document Converter Module
Converts PDF and Word documents to structured text for resume parsing
"""

import pdfplumber
import docx2txt
from docx import Document
import json
import re
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentConverter:
    """Convert PDF/Word documents to structured text for resume parsing"""
    
    def __init__(self):
        self.supported_formats = [".pdf", ".docx", ".doc"]
    
    def extract_from_pdf(self, filepath: str) -> Dict[str, Any]:
        """Extract text from PDF using pdfplumber"""
        try:
            with pdfplumber.open(filepath) as pdf:
                text_content = ""
                metadata = {
                    "total_pages": len(pdf.pages)
                }
                
                for page in pdf.pages:
                    page_text = page.extract_text(x_tolerance=3, y_tolerance=3)
                    if page_text:
                        cleaned_text = self.clean_pdf_text(page_text)
                        text_content += cleaned_text
                
                return {
                    "text": text_content.strip(),
                    "format": "pdf",
                    "metadata": metadata,
                    "extraction_method": "pdfplumber"
                }
                
        except Exception as e:
            logger.error(f"PDF extraction failed for {filepath}: {str(e)}")
            return {
                "text": "",
                "format": "pdf",
                "error": f"PDF extraction failed: {str(e)}"
            }
    
    def extract_from_docx(self, filepath: str) -> Dict[str, Any]:
        """Extract text from DOCX using python-docx and docx2txt"""
        try:
            # Method 1: Try docx2txt (simpler, preserves formatting better)
            text_content = docx2txt.process(filepath)
            
            if not text_content or len(text_content.strip()) < 50:
                # Method 2: Fallback to python-docx
                doc = Document(filepath)
                paragraphs = []
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        paragraphs.append(paragraph.text.strip())
                text_content = "\n".join(paragraphs)
            
            # Clean and structure the text
            cleaned_text = self.clean_docx_text(text_content)
            
            return {
                "text": cleaned_text,
                "format": "docx",
                "metadata": {
                    "extraction_method": "docx2txt + python-docx"
                }
            }
            
        except Exception as e:
            logger.error(f"DOCX extraction failed for {filepath}: {str(e)}")
            return {
                "text": "",
                "format": "docx", 
                "error": f"DOCX extraction failed: {str(e)}"
            }
    
    def extract_from_file(self, filepath: str) -> Dict[str, Any]:
        """Extract text from any supported document format"""
        path = Path(filepath)
        
        if not path.exists():
            return {
                "text": "",
                "error": f"File not found: {filepath}"
            }
        
        file_ext = path.suffix.lower()
        
        if file_ext not in self.supported_formats:
            return {
                "text": "",
                "error": f"Unsupported file format: {file_ext}. Supported: {self.supported_formats}"
            }
        
        logger.info(f"Extracting text from {file_ext.upper()}: {path.name}")
        
        if file_ext == ".pdf":
            return self.extract_from_pdf(filepath)
        elif file_ext in [".docx", ".doc"]:
            return self.extract_from_docx(filepath)
        else:
            return {
                "text": "",
                "error": f"Handler not implemented for {file_ext}"
            }
    
    def clean_pdf_text(self, text: str) -> str:
        """Clean and normalize PDF extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common PDF extraction issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between camelCase
        text = re.sub(r'(\w)(\d)', r'\1 \2', text)  # Space between word and number
        text = re.sub(r'(\d)(\w)', r'\1 \2', text)  # Space between number and word
        
        # Clean email and phone patterns
        text = re.sub(r'([a-zA-Z])(@)', r'\1 \2', text)  # Space before @
        text = re.sub(r'(\d)([-+()])', r'\1 \2', text)  # Space in phone numbers
        
        # Ensure newlines after common section headers
        section_patterns = [
            r'(EXPERIENCE|EDUCATION|SKILLS|PROJECTS|CERTIFICATIONS|SUMMARY)'
        ]
        for pattern in section_patterns:
            text = re.sub(f'({pattern})([A-Z])', r'\1\n\2', text)
        
        return text.strip()
    
    def clean_docx_text(self, text: str) -> str:
        """Clean and normalize DOCX extracted text"""
        if not text:
            return ""
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive empty lines (keep max 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Clean up spacing
        lines = []
        for line in text.split('\n'):
            cleaned_line = re.sub(r'\s+', ' ', line).strip()
            if cleaned_line:  # Only keep non-empty lines
                lines.append(cleaned_line)
            elif lines and lines[-1]:  # Keep one empty line as separator
                lines.append('')
        
        return '\n'.join(lines).strip()
    
    def get_document_info(self, filepath: str) -> Dict[str, Any]:
        """Get basic information about the document"""
        path = Path(filepath)
        
        info = {
            "filename": path.name,
            "file_size_kb": path.stat().st_size / 1024,
            "file_extension": path.suffix.lower(),
            "supported": path.suffix.lower() in self.supported_formats
        }
        
        return info

def main():
    """Command line interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Document Text Extraction")
    parser.add_argument("file", help="Path to document file")
    parser.add_argument("--output", help="Output file for extracted text")
    parser.add_argument("--info", action="store_true", help="Show document info only")
    
    args = parser.parse_args()
    
    converter = DocumentConverter()
    
    if args.info:
        # Show document info
        info = converter.get_document_info(args.file)
        print(json.dumps(info, indent=2))
    else:
        # Extract text
        result = converter.extract_from_file(args.file)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        text = result["text"]
        print(f"✅ Extracted {len(text)} characters from {result['format'].upper()} file")
        
        if args.output:
            # Save to file
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"📄 Text saved to: {args.output}")
        else:
            # Print preview
            preview = text[:500] + "..." if len(text) > 500 else text
            print(f"\n📝 Text Preview:\n{preview}")

if __name__ == "__main__":
    main()