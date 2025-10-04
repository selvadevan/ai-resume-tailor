"""
Module 2: Job Description Processor
Handles multiple input sources with safe file reading
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List
import logging
from datetime import datetime
from job_description_parser import JobDescriptionParser

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobProcessor:
    """Process job descriptions from various sources"""
    
    def __init__(self, api_key: str = None):
        self.parser = JobDescriptionParser(api_key=api_key)
        logger.info("JobProcessor initialized")
    
    def process_text(self, job_text: str, source: str = "text_input") -> Dict[str, Any]:
        """Process job description from text"""
        if not job_text or not job_text.strip():
            return {
                "success": False,
                "error": "Job description text is empty",
                "source": source
            }
        
        logger.info(f"Processing job text from: {source}")
        
        # Clean the text
        cleaned_text = self._clean_text(job_text)
        
        # Parse with Groq
        result = self.parser.parse_job_description(cleaned_text)
        result["source"] = source
        result["original_length"] = len(job_text)
        result["cleaned_length"] = len(cleaned_text)
        
        return result
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process job description from file with safe reading"""
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "source": f"file:{file_path}"
            }
        
        try:
            logger.info(f"Reading file: {file_path}")
            
            # Safe file reading
            job_text = self._read_file_safely(file_path)
            if not job_text:
                return {
                    "success": False,
                    "error": "File is empty or could not be read",
                    "source": f"file:{file_path}"
                }
            
            # Process the text
            return self.process_text(job_text, source=f"file:{file_path}")
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading file: {str(e)}",
                "source": f"file:{file_path}"
            }
    
    def _read_file_safely(self, file_path: str) -> str:
        """Read file with safe encoding handling"""
        # Try different encodings in order of preference
        encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                logger.info(f"Successfully read file with {encoding} encoding")
                return content
            except UnicodeDecodeError:
                logger.debug(f"Failed to read with {encoding} encoding")
                continue
            except Exception as e:
                logger.debug(f"Error with {encoding}: {str(e)}")
                continue
        
        # Last resort: read with error replacement
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            logger.warning("Read file with character replacement")
            return content
        except Exception as e:
            logger.error(f"Could not read file: {str(e)}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize job description text"""
        if not text:
            return ""
        
        # Basic text cleaning
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove HTML tags if present
        text = re.sub(r'<[^>]+>', '', text)
        
        # Clean up line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def batch_process(self, jobs: List[Dict[str, str]]) -> Dict[str, Any]:
        """Process multiple jobs in batch"""
        results = {
            "total": len(jobs),
            "successful": 0,
            "failed": 0,
            "results": []
        }
        
        for i, job_input in enumerate(jobs):
            job_type = job_input.get("type", "text")
            source = job_input.get("source", "")
            
            logger.info(f"Processing job {i+1}/{len(jobs)} - Type: {job_type}")
            
            if job_type == "text":
                result = self.process_text(source, f"batch_{i+1}")
            elif job_type == "file":
                result = self.process_file(source)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown job type: {job_type}",
                    "source": source
                }
            
            if result["success"]:
                results["successful"] += 1
                job_title = result["data"].get("job_title", "Unknown")
                company = result["data"].get("company_name", "Unknown")
                results["results"].append({
                    "index": i + 1,
                    "status": "success",
                    "title": job_title,
                    "company": company
                })
            else:
                results["failed"] += 1
                results["results"].append({
                    "index": i + 1,
                    "status": "failed",
                    "error": result["error"]
                })
        
        return results
    
    def save_result(self, result: Dict[str, Any], output_dir: str = "parsed_jobs") -> str:
        """Save parsing result to JSON file"""
        if not result["success"]:
            logger.error("Cannot save failed parsing result")
            return ""
        
        try:
            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            data = result["data"]
            job_title = data.get("job_title", "job")
            company = data.get("company_name", "company")
            
            # Clean filename
            safe_title = "".join(c for c in job_title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_company = "".join(c for c in company if c.isalnum() or c in (' ', '-', '_')).strip()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_company}_{safe_title}_{timestamp}.json"
            output_path = Path(output_dir) / filename
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Result saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error saving result: {str(e)}")
            return ""

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Job Description Processor")
    parser.add_argument("input", help="Job description text or file path")
    parser.add_argument("--type", default="auto", choices=["text", "file", "auto"],
                       help="Input type (auto detects if file exists)")
    parser.add_argument("--api-key", help="Groq API key")
    parser.add_argument("--save", action="store_true", help="Save result to file")
    parser.add_argument("--output-dir", default="parsed_jobs", help="Output directory")
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = JobProcessor(api_key=args.api_key)
    
    # Determine input type
    if args.type == "auto":
        input_type = "file" if os.path.exists(args.input) else "text"
    else:
        input_type = args.type
    
    # Process job
    if input_type == "file":
        result = processor.process_file(args.input)
    else:
        result = processor.process_text(args.input)
    
    # Display results
    processor.parser.display_parsed_job(result)
    
    # Save if requested
    if args.save and result["success"]:
        output_path = processor.save_result(result, args.output_dir)
        if output_path:
            print(f"\n💾 Result saved to: {output_path}")
    
    # Show usage examples
    if result["success"]:
        print(f"\n🎉 SUCCESS! Job description processed successfully")
    else:
        print(f"\n❌ PROCESSING FAILED")
    
    print(f"\n🔧 Usage examples:")
    print(f'   python job_processor.py "job description text here"')
    print(f'   python job_processor.py job.txt --type file --save')

if __name__ == "__main__":
    main()