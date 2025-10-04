#!/usr/bin/env python3

"""
Batch Resume Tailoring Script
Process multiple CVs against multiple job descriptions automatically.

Usage:
python batch_process.py --cvs-dir ./cvs --jobs-dir ./jobs --output-dir ./outputs
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict
import logging
from datetime import datetime

# Import the main system
try:
    from main import ResumeCustomizationSystem
except ImportError:
    print("❌ Error: main.py not found. Make sure it's in the same directory.")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BatchProcessor:
    """Batch process multiple resumes and job descriptions"""
    
    def __init__(self, api_key: str = None):
        self.system = ResumeCustomizationSystem(api_key=api_key)
        self.results = []
    
    def find_files(self, directory: str, extensions: List[str]) -> List[Path]:
        """Find all files with specified extensions in directory"""
        files = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            logger.warning(f"Directory not found: {directory}")
            return files
        
        for ext in extensions:
            pattern = f"*{ext}"
            found = list(dir_path.glob(pattern))
            files.extend(found)
        
        return sorted(files)
    
    def process_batch(self, cvs_dir: str, jobs_dir: str, output_dir: str, format_type: str = "docx") -> Dict:
        """Process all CV and job combinations"""
        print("🔄 BATCH RESUME TAILORING")
        print("=" * 40)
        
        # Find all CV files
        cv_files = self.find_files(cvs_dir, ['.pdf', '.docx', '.doc'])
        print(f"📄 Found {len(cv_files)} CV files in {cvs_dir}")
        
        # Find all job description files
        job_files = self.find_files(jobs_dir, ['.txt', '.md'])
        print(f"💼 Found {len(job_files)} job files in {jobs_dir}")
        
        if not cv_files:
            return {"success": False, "error": f"No CV files found in {cvs_dir}"}
        if not job_files:
            return {"success": False, "error": f"No job files found in {jobs_dir}"}
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        total_combinations = len(cv_files) * len(job_files)
        print(f"🎯 Processing {total_combinations} combinations...")
        print()
        
        successful = 0
        failed = 0
        
        # Process each combination
        for i, cv_file in enumerate(cv_files, 1):
            cv_name = cv_file.stem
            print(f"👤 CV {i}/{len(cv_files)}: {cv_name}")
            
            for j, job_file in enumerate(job_files, 1):
                job_name = job_file.stem
                print(f"  💼 Job {j}/{len(job_files)}: {job_name}")
                
                # Generate output filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_name = f"{cv_name}_for_{job_name}_{timestamp}"
                output_path = Path(output_dir) / output_name
                
                try:
                    # Process this combination
                    result = self.system.run(
                        cv_file=str(cv_file),
                        job_file=str(job_file),
                        output_name=str(output_path),
                        format_type=format_type
                    )
                    
                    if result["success"]:
                        successful += 1
                        print(f"    ✅ Created: {result['output_file']}")
                        
                        # Store result info
                        self.results.append({
                            "status": "success",
                            "cv_file": str(cv_file),
                            "job_file": str(job_file),
                            "output_file": result["output_file"],
                            "candidate": result.get("candidate_name", "Unknown"),
                            "job_title": result.get("job_title", "Unknown"),
                            "company": result.get("company", "Unknown")
                        })
                    else:
                        failed += 1
                        error_msg = result.get("error", "Unknown error")
                        print(f"    ❌ Failed: {error_msg}")
                        
                        self.results.append({
                            "status": "failed",
                            "cv_file": str(cv_file),
                            "job_file": str(job_file),
                            "error": error_msg
                        })
                        
                except Exception as e:
                    failed += 1
                    print(f"    💥 Exception: {str(e)}")
                    
                    self.results.append({
                        "status": "exception",
                        "cv_file": str(cv_file),
                        "job_file": str(job_file),
                        "error": str(e)
                    })
        
        # Final summary
        print()
        print("📊 BATCH PROCESSING COMPLETE")
        print("=" * 40)
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📁 Output directory: {output_dir}")
        
        return {
            "success": True,
            "total_processed": total_combinations,
            "successful": successful,
            "failed": failed,
            "results": self.results,
            "output_directory": output_dir
        }
    
    def save_report(self, output_dir: str):
        """Save detailed processing report"""
        report_file = Path(output_dir) / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("BATCH RESUME TAILORING REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total combinations: {len(self.results)}\n\n")
            
            successful_count = sum(1 for r in self.results if r["status"] == "success")
            f.write(f"Successful: {successful_count}\n")
            f.write(f"Failed: {len(self.results) - successful_count}\n\n")
            
            f.write("DETAILED RESULTS:\n")
            f.write("-" * 30 + "\n")
            
            for i, result in enumerate(self.results, 1):
                f.write(f"\n{i}. {result['status'].upper()}\n")
                f.write(f"   CV: {Path(result['cv_file']).name}\n")
                f.write(f"   Job: {Path(result['job_file']).name}\n")
                
                if result["status"] == "success":
                    f.write(f"   Candidate: {result.get('candidate', 'Unknown')}\n")
                    f.write(f"   Position: {result.get('job_title', 'Unknown')}\n")
                    f.write(f"   Company: {result.get('company', 'Unknown')}\n")
                    f.write(f"   Output: {Path(result['output_file']).name}\n")
                else:
                    f.write(f"   Error: {result.get('error', 'Unknown error')}\n")
        
        print(f"📋 Detailed report saved: {report_file}")

def main():
    """Main function for batch processing"""
    parser = argparse.ArgumentParser(description="Batch Resume Tailoring Processor")
    parser.add_argument("--cvs-dir", required=True, help="Directory containing CV files")
    parser.add_argument("--jobs-dir", required=True, help="Directory containing job description files")
    parser.add_argument("--output-dir", required=True, help="Output directory for generated resumes")
    parser.add_argument("--format", default="docx", choices=["docx", "pdf"], help="Output format")
    parser.add_argument("--api-key", help="Groq API key")
    parser.add_argument("--report", action="store_true", help="Save detailed processing report")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("⚠️ WARNING: No Groq API key provided!")
        print("Proceeding with embedded keys (if set)...")
    
    # Initialize processor
    processor = BatchProcessor(api_key=api_key)
    
    # Run batch processing
    try:
        result = processor.process_batch(
            cvs_dir=args.cvs_dir,
            jobs_dir=args.jobs_dir,
            output_dir=args.output_dir,
            format_type=args.format
        )
        
        if result["success"]:
            print("\n🎉 Batch processing completed successfully!")
            
            # Save report if requested
            if args.report:
                processor.save_report(args.output_dir)
        else:
            print(f"\n❌ Batch processing failed: {result['error']}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚡ Batch processing interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        logger.exception("Unexpected error in batch processing")
        sys.exit(1)

if __name__ == "__main__":
    main()