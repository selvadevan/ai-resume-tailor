"""
Resume Data Extraction System - Main Processor with Custom Groq
Uses Groq API with openai/gpt-oss-20b model and embedded API key
"""

import json
from pathlib import Path
from typing import Dict, Any
import logging
from datetime import datetime

# Import our modules
from document_converter_groq import DocumentConverter
from groq_resume_extractor import GroqResumeExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqResumeProcessor:
    """Complete Resume Data Extraction System using Custom Groq"""
    
    def __init__(self, groq_api_key: str = None):
        """
        Initialize the resume processor with custom Groq extractor
        
        Args:
            groq_api_key: Your Groq API key (will be embedded in code if not provided)
        """
        self.doc_converter = DocumentConverter()
        self.groq_extractor = GroqResumeExtractor(api_key=groq_api_key)
        logger.info("Resume processor initialized with custom Groq openai/gpt-oss-20b model")
    
    def process_resume(self, 
                      file_path: str, 
                      output_dir: str = "outputs",
                      save_json: bool = True) -> Dict[str, Any]:
        """
        Complete resume processing pipeline
        
        Args:
            file_path: Path to resume file (PDF/DOCX)
            output_dir: Directory to save outputs
            save_json: Whether to save extracted data as JSON
            
        Returns:
            Dict with success status, extracted data, and metadata
        """
        try:
            # Step 1: Convert document to text
            logger.info(f"Processing resume: {file_path}")
            
            doc_result = self.doc_converter.extract_from_file(file_path)
            if not doc_result.get("success", True):  # Assume success if key missing
                return {
                    "success": False,
                    "error": f"Document conversion failed: {doc_result.get('error', 'Unknown error')}",
                    "file_path": file_path
                }
            
            resume_text = doc_result["text"]
            if not resume_text or len(resume_text.strip()) < 50:
                return {
                    "success": False,
                    "error": "Extracted text is too short or empty",
                    "file_path": file_path,
                    "text_length": len(resume_text) if resume_text else 0
                }
            
            logger.info(f"✅ Document converted - {len(resume_text)} characters extracted")
            
            # Step 2: Extract structured data using Groq
            extraction_result = self.groq_extractor.extract_resume_data(resume_text)
            
            if not extraction_result["success"]:
                return {
                    "success": False,
                    "error": f"Data extraction failed: {extraction_result['error']}",
                    "file_path": file_path,
                    "raw_text": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
                }
            
            extracted_data = extraction_result["data"]
            logger.info("✅ Structured data extracted successfully")
            
            # Step 3: Prepare results
            result = {
                "success": True,
                "file_path": file_path,
                "extracted_data": extracted_data,
                "extraction_metadata": {
                    "processing_timestamp": datetime.now().isoformat(),
                    "file_format": doc_result.get("format", "unknown"),
                    "text_length": len(resume_text),
                    "extraction_method": "groq_openai_gpt_oss_20b",
                    "model_used": self.groq_extractor.model
                }
            }
            
            # Step 4: Save JSON if requested
            if save_json:
                self._save_results(result, output_dir)
            
            logger.info("🎉 Resume processing completed successfully")
            return result
            
        except Exception as e:
            logger.exception(f"Unexpected error processing {file_path}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "file_path": file_path
            }
    
    def _save_results(self, result: Dict[str, Any], output_dir: str) -> None:
        """Save extraction results to JSON file"""
        try:
            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate output filename
            input_name = Path(result["file_path"]).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = Path(output_dir) / f"{input_name}_extracted_{timestamp}.json"
            
            # Save results
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📄 Results saved: {output_file}")
            result["output_file"] = str(output_file)
            
        except Exception as e:
            logger.warning(f"Could not save results: {e}")
    
    def batch_process(self, 
                     input_dir: str, 
                     output_dir: str = "batch_outputs",
                     file_patterns: list = None) -> Dict[str, Any]:
        """
        Process multiple resume files in batch
        
        Args:
            input_dir: Directory containing resume files
            output_dir: Directory for outputs
            file_patterns: File extensions to process (default: ["*.pdf", "*.docx", "*.doc"])
            
        Returns:
            Dict with batch processing results
        """
        if file_patterns is None:
            file_patterns = ["*.pdf", "*.docx", "*.doc"]
        
        input_path = Path(input_dir)
        if not input_path.exists():
            return {
                "success": False,
                "error": f"Input directory not found: {input_dir}"
            }
        
        # Find all resume files
        resume_files = []
        for pattern in file_patterns:
            resume_files.extend(input_path.glob(pattern))
        
        if not resume_files:
            return {
                "success": False,
                "error": f"No resume files found in {input_dir}"
            }
        
        logger.info(f"🚀 Starting batch processing of {len(resume_files)} files")
        
        results = {
            "success": True,
            "total_files": len(resume_files),
            "processed_files": [],
            "failed_files": [],
            "summary": {}
        }
        
        # Process each file
        for file_path in resume_files:
            logger.info(f"Processing: {file_path.name}")
            
            result = self.process_resume(str(file_path), output_dir)
            
            if result["success"]:
                results["processed_files"].append({
                    "file": str(file_path),
                    "status": "success",
                    "candidate_name": result["extracted_data"].get("personal_details", {}).get("name", "Unknown")
                })
                logger.info(f"✅ Success: {file_path.name}")
            else:
                results["failed_files"].append({
                    "file": str(file_path),
                    "error": result["error"]
                })
                logger.error(f"❌ Failed: {file_path.name} - {result['error']}")
        
        # Generate summary
        results["summary"] = {
            "successful": len(results["processed_files"]),
            "failed": len(results["failed_files"]),
            "success_rate": len(results["processed_files"]) / len(resume_files) * 100
        }
        
        logger.info(f"🏁 Batch processing completed: {results['summary']['successful']}/{results['total_files']} successful")
        
        return results

def main():
    """Command line interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Resume Data Extraction System")
    parser.add_argument("input", help="Resume file or directory")
    parser.add_argument("--output", default="outputs", help="Output directory")
    parser.add_argument("--batch", action="store_true", help="Process directory in batch mode")
    parser.add_argument("--api-key", help="Groq API key")
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = GroqResumeProcessor(groq_api_key=args.api_key)
    
    if args.batch:
        # Batch processing
        result = processor.batch_process(args.input, args.output)
    else:
        # Single file processing
        result = processor.process_resume(args.input, args.output)
    
    # Print results
    if result["success"]:
        print("\n🎉 Processing completed successfully!")
        if "summary" in result:
            print(f"📊 Success rate: {result['summary']['success_rate']:.1f}%")
    else:
        print(f"\n❌ Processing failed: {result['error']}")

if __name__ == "__main__":
    main()