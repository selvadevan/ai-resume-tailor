#!/usr/bin/env python3

"""
Intelligent Resume Tailoring System - Main Application

This application takes user CVs (PDF/Word) and job descriptions (text files)
and generates customized resumes in DOCX or PDF format.

Usage:
python main.py [options]

Examples:
python main.py resume.pdf job_description.txt --format docx
python main.py my_cv.docx software_engineer_job.txt --format pdf --output custom_resume
python main.py resume.pdf job.txt --api-key your_groq_key --format docx
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Dict, Any
import json
import logging
from datetime import datetime

# Import our custom modules
try:
    from groq_resume_processor import GroqResumeProcessor
    from job_processor import JobProcessor
    from resume_generator import CommandLineResumeGenerator
except ImportError as e:
    print(f"❌ ERROR: Missing required module: {e}")
    print("\nMake sure all these files are in the same directory:")
    print("• document_converter_groq.py")
    print("• groq_resume_extractor.py")
    print("• groq_resume_processor.py")
    print("• job_description_parser.py")
    print("• job_processor.py")
    print("• resume_generator.py")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResumeCustomizationSystem:
    """Main system for customizing resumes based on job descriptions"""
    
    def __init__(self, api_key: str = None):
        """Initialize the system with Groq API key"""
        self.api_key = api_key
        self.resume_processor = GroqResumeProcessor(groq_api_key=api_key)
        self.job_processor = JobProcessor(api_key=api_key)
        self.resume_generator = CommandLineResumeGenerator(api_key=api_key)
        logger.info("Resume Customization System initialized")
    
    def validate_inputs(self, cv_file: str, job_file: str) -> Dict[str, Any]:
        """Validate input files"""
        errors = []
        
        # Check CV file
        if not os.path.exists(cv_file):
            errors.append(f"CV file not found: {cv_file}")
        else:
            cv_ext = Path(cv_file).suffix.lower()
            if cv_ext not in ['.pdf', '.docx', '.doc']:
                errors.append(f"Unsupported CV format: {cv_ext}. Use PDF or DOCX.")
        
        # Check job description file
        if not os.path.exists(job_file):
            errors.append(f"Job description file not found: {job_file}")
        else:
            job_ext = Path(job_file).suffix.lower()
            if job_ext not in ['.txt', '.md']:
                logger.warning(f"Job file format {job_ext} may not be optimal. Text files work best.")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def process_cv(self, cv_file: str) -> Dict[str, Any]:
        """Extract structured data from CV"""
        logger.info(f"Processing CV: {cv_file}")
        result = self.resume_processor.process_resume(cv_file)
        
        if not result["success"]:
            return {
                "success": False,
                "error": f"CV processing failed: {result['error']}"
            }
        
        # Convert to format expected by resume generator
        cv_data = result["extracted_data"]
        
        # Map fields from extractor format to generator format
        mapped_data = {
            "personal_info": {
                "name": cv_data["personal_details"].get("name", ""),
                "email": cv_data["personal_details"].get("email", ""),
                "phone": cv_data["personal_details"].get("phone", ""),
                "location": cv_data["personal_details"].get("address", ""),
                "linkedin": cv_data["personal_details"].get("linkedin", ""),
                "portfolio": cv_data["personal_details"].get("website", "")
            },
            "professional_summary": cv_data.get("summary", ""),
            "core_competencies": cv_data["skills"].get("technical_skills", []),
            "professional_experience": [],
            "education": cv_data.get("education", []),
            "technical_skills": {
                "programming_languages": [],
                "frameworks_tools": [],
                "databases": [],
                "other_technical": cv_data["skills"].get("technical_skills", [])
            },
            "projects": cv_data.get("projects", []),
            "certifications": cv_data.get("certifications", [])
        }
        
        # Convert work experience
        for exp in cv_data.get("work_experience", []):
            mapped_exp = {
                "position": exp.get("position", ""),
                "company": exp.get("company", ""),
                "location": exp.get("location", ""),
                "duration": f"{exp.get('start_date', '')} - {exp.get('end_date', '')}",
                "achievements": [exp.get("description", "")]
            }
            mapped_data["professional_experience"].append(mapped_exp)
        
        return {
            "success": True,
            "data": mapped_data,
            "metadata": result.get("extraction_metadata", {})
        }
    
    def process_job_description(self, job_file: str) -> Dict[str, Any]:
        """Parse job description into structured data"""
        logger.info(f"Processing job description: {job_file}")
        result = self.job_processor.process_file(job_file)
        
        if not result["success"]:
            return {
                "success": False,
                "error": f"Job processing failed: {result['error']}"
            }
        
        return result
    
    def generate_tailored_resume(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tailored resume using AI"""
        logger.info("Generating tailored resume with AI...")
        result = self.resume_generator.tailor_resume(cv_data, job_data["data"])
        
        if not result["success"]:
            return {
                "success": False,
                "error": f"Resume tailoring failed: {result['error']}"
            }
        
        return result
    
    def create_output_file(self, tailored_resume: Dict[str, Any], output_path: str, format_type: str) -> Dict[str, Any]:
        """Create final resume file"""
        logger.info(f"Creating {format_type.upper()} file: {output_path}")
        resume_data = tailored_resume["tailored_resume"]
        
        if format_type.lower() == "docx":
            return self.resume_generator.generate_docx(resume_data, output_path)
        elif format_type.lower() == "pdf":
            return self.resume_generator.generate_pdf(resume_data, output_path)
        else:
            return {
                "success": False,
                "error": f"Unsupported output format: {format_type}"
            }
    
    def run(self, cv_file: str, job_file: str, output_name: str = None, format_type: str = "docx") -> Dict[str, Any]:
        """Run the complete resume customization pipeline"""
        print("🚀 INTELLIGENT RESUME TAILORING SYSTEM")
        print("=" * 50)
        
        # Step 1: Validate inputs
        print("\n1️⃣ Validating input files...")
        validation = self.validate_inputs(cv_file, job_file)
        if not validation["valid"]:
            return {
                "success": False,
                "errors": validation["errors"]
            }
        print("✅ Input files validated")
        
        # Step 2: Process CV
        print("\n2️⃣ Extracting data from CV...")
        cv_result = self.process_cv(cv_file)
        if not cv_result["success"]:
            return cv_result
        print(f"✅ CV processed - extracted data for {cv_result['data']['personal_info']['name']}")
        
        # Step 3: Process job description
        print("\n3️⃣ Analyzing job description...")
        job_result = self.process_job_description(job_file)
        if not job_result["success"]:
            return job_result
        
        job_title = job_result["data"].get("job_title", "target position")
        company = job_result["data"].get("company_name", "target company")
        print(f"✅ Job analyzed - {job_title} at {company}")
        
        # Step 4: Generate tailored resume
        print("\n4️⃣ Tailoring resume with AI...")
        tailored_result = self.generate_tailored_resume(cv_result["data"], job_result)
        if not tailored_result["success"]:
            return tailored_result
        print("✅ Resume tailored successfully")
        
        # Step 5: Create output file
        print(f"\n5️⃣ Creating {format_type.upper()} file...")
        
        # Generate output filename if not provided
        if not output_name:
            cv_name = Path(cv_file).stem
            job_name = Path(job_file).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{cv_name}_tailored_for_{job_name}_{timestamp}"
        
        output_path = f"{output_name}.{format_type.lower()}"
        file_result = self.create_output_file(tailored_result, output_path, format_type)
        
        if not file_result["success"]:
            return file_result
        
        print(f"✅ Resume created: {output_path}")
        
        # Success summary
        print("\n🎉 SUCCESS! Resume customization completed")
        print(f"📄 Input CV: {cv_file}")
        print(f"💼 Target Job: {job_title} at {company}")
        print(f"📝 Output: {output_path} ({file_result.get('file_size_kb', 0):.1f} KB)")
        
        return {
            "success": True,
            "output_file": output_path,
            "job_title": job_title,
            "company": company,
            "candidate_name": cv_result["data"]["personal_info"]["name"],
            "file_info": file_result
        }

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(
        description="Intelligent Resume Tailoring System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s resume.pdf job_description.txt
  %(prog)s my_cv.docx software_job.txt --format pdf
  %(prog)s resume.pdf job.txt --output custom_resume --api-key your_key
"""
    )
    
    # Required arguments
    parser.add_argument("cv_file", help="Path to CV file (PDF or DOCX)")
    parser.add_argument("job_file", help="Path to job description file (TXT)")
    
    # Optional arguments
    parser.add_argument("--format", default="docx", choices=["docx", "pdf"],
                       help="Output format (default: docx)")
    parser.add_argument("--output", help="Output filename (without extension)")
    parser.add_argument("--api-key", help="Groq API key")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check for API key
    api_key = args.api_key or os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("⚠️ WARNING: No Groq API key provided!")
        print("Set your API key using:")
        print("• --api-key YOUR_KEY")
        print("• export GROQ_API_KEY=YOUR_KEY")
        print("• Edit the API keys in the Python files")
        print("\nProceeding with embedded keys (if set)...")
    
    # Initialize system
    try:
        system = ResumeCustomizationSystem(api_key=api_key)
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        sys.exit(1)
    
    # Run the pipeline
    try:
        result = system.run(
            cv_file=args.cv_file,
            job_file=args.job_file,
            output_name=args.output,
            format_type=args.format
        )
        
        if result["success"]:
            print("\n🎯 NEXT STEPS:")
            print(f"1. Review the generated resume: {result['output_file']}")
            print("2. Make any manual adjustments if needed")
            print("3. Submit your tailored application!")
        else:
            print("\n❌ PROCESS FAILED:")
            if "errors" in result:
                for error in result["errors"]:
                    print(f"• {error}")
            else:
                print(f"• {result.get('error', 'Unknown error')}")
                
            print("\n💡 TROUBLESHOOTING:")
            print("• Ensure all Python files are in the same directory")
            print("• Check that your Groq API key is valid")
            print("• Verify input file formats (PDF/DOCX for CV, TXT for job)")
            print("• Install required dependencies: pip install -r requirements.txt")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚡ Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        logger.exception("Unexpected error in main process")
        sys.exit(1)

if __name__ == "__main__":
    main()