"""
Module 2: Job Description Parser using Groq API
Clean implementation for parsing job postings into structured data
"""

import json
import requests
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobDescriptionParser:
    """Parse job descriptions using Groq API with openai/gpt-oss-20b model"""
    
    def __init__(self, api_key: str = None):
        # Replace with your actual Groq API key
        self.api_key = api_key or "YOUR_GROQ_API_KEY_HERE"
        self.model = "openai/gpt-oss-20b"
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        logger.info(f"JobDescriptionParser initialized with model: {self.model}")
    
    def create_parsing_prompt(self, job_text: str) -> str:
        """Create prompt for extracting structured job data"""
        return f"""
You are an expert job posting analyzer. Extract structured information from this job description and return it as valid JSON.

JOB DESCRIPTION:
{job_text}

Extract the following information and return as JSON:

{{
  "job_title": "exact job title",
  "company_name": "company name",
  "location": "job location",
  "employment_type": "Full-time/Part-time/Contract/Internship",
  "remote_work": "Remote/Hybrid/On-site/Not specified",
  "salary_info": "salary range or compensation if mentioned",
  "required_skills": [
    "list of required technical skills, tools, technologies"
  ],
  "preferred_skills": [
    "list of preferred/nice-to-have skills"
  ],
  "education_requirements": [
    "education level and field requirements"
  ],
  "experience_required": "years of experience needed",
  "key_responsibilities": [
    "main job responsibilities and duties"
  ],
  "benefits": [
    "benefits, perks, and compensation details mentioned"
  ],
  "application_info": {{
    "deadline": "application deadline if mentioned",
    "contact": "contact information if provided",
    "process": "application process details"
  }}
}}

IMPORTANT: Return ONLY valid JSON. Extract ALL technical skills, programming languages, frameworks, and tools mentioned. Be comprehensive but accurate.
"""
    
    def parse_job_description(self, job_text: str) -> Dict[str, Any]:
        """Parse job description text using Groq API"""
        # Validate inputs
        if not job_text or not job_text.strip():
            return {
                "success": False,
                "error": "Job description text is empty"
            }
        
        if self.api_key == "YOUR_GROQ_API_KEY_HERE":
            return {
                "success": False,
                "error": "Please set your Groq API key. Replace YOUR_GROQ_API_KEY_HERE with your actual key."
            }
        
        try:
            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = self.create_parsing_prompt(job_text)
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert job posting analyzer. Extract structured information and return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 2000,
                "stream": False
            }
            
            logger.info(f"Sending request to Groq API...")
            
            # Make API call
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                content = response_data["choices"][0]["message"]["content"]
                logger.info(f"Received response from Groq API")
                
                # Extract and parse JSON
                json_data = self._extract_json_from_response(content)
                if json_data:
                    try:
                        parsed_data = json.loads(json_data)
                        return {
                            "success": True,
                            "data": parsed_data,
                            "model": self.model,
                            "timestamp": datetime.now().isoformat()
                        }
                    except json.JSONDecodeError as e:
                        return {
                            "success": False,
                            "error": f"Invalid JSON in response: {str(e)}",
                            "raw_response": content
                        }
                else:
                    return {
                        "success": False,
                        "error": "No valid JSON found in response",
                        "raw_response": content
                    }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code} - {response.text}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout - please try again"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _extract_json_from_response(self, content: str) -> Optional[str]:
        """Extract JSON from API response content"""
        # Method 1: Look for JSON in code blocks
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            if end != -1:
                return content[start:end].strip()
        
        # Method 2: Look for JSON between first { and last }
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end > start:
            return content[start:end]
        
        # Method 3: Try entire content if it looks like JSON
        content = content.strip()
        if content.startswith('{') and content.endswith('}'):
            return content
        
        return None
    
    def display_parsed_job(self, result: Dict[str, Any]) -> None:
        """Display parsed job description in a formatted way"""
        if not result["success"]:
            print(f"\n❌ PARSING FAILED:")
            print(f"   Error: {result['error']}")
            if "raw_response" in result:
                print(f"\n📄 Raw Response:")
                print(f"   {result['raw_response'][:300]}...")
            print(f"\n🔧 Troubleshooting:")
            print(f"   1. Check your Groq API key is set correctly")
            print(f"   2. Verify internet connection")
            print(f"   3. Ensure job description text is valid")
            return
        
        data = result["data"]
        model = result.get("model", "unknown")
        
        print(f"\n✅ JOB PARSING SUCCESS!")
        print(f"🤖 Model: {model}")
        print(f"⏰ Parsed at: {result.get('timestamp', 'unknown')}")
        print("=" * 50)
        
        # Basic job info
        print(f"\n💼 JOB DETAILS:")
        print(f"   Title: {data.get('job_title', 'N/A')}")
        print(f"   Company: {data.get('company_name', 'N/A')}")
        print(f"   Location: {data.get('location', 'N/A')}")
        print(f"   Type: {data.get('employment_type', 'N/A')}")
        print(f"   Remote: {data.get('remote_work', 'N/A')}")
        if data.get('salary_info'):
            print(f"   Salary: {data['salary_info']}")
        if data.get('experience_required'):
            print(f"   Experience: {data['experience_required']}")
        
        # Required skills
        required_skills = data.get('required_skills', [])
        if required_skills:
            print(f"\n🛠️ REQUIRED SKILLS ({len(required_skills)}):")
            for skill in required_skills:
                print(f"   • {skill}")
        
        # Preferred skills
        preferred_skills = data.get('preferred_skills', [])
        if preferred_skills:
            print(f"\n⭐ PREFERRED SKILLS ({len(preferred_skills)}):")
            for skill in preferred_skills[:5]:  # Show first 5
                print(f"   • {skill}")
            if len(preferred_skills) > 5:
                print(f"   ... and {len(preferred_skills) - 5} more")
        
        # Education
        education = data.get('education_requirements', [])
        if education:
            print(f"\n🎓 EDUCATION:")
            for edu in education:
                print(f"   • {edu}")
        
        # Responsibilities
        responsibilities = data.get('key_responsibilities', [])
        if responsibilities:
            print(f"\n📋 KEY RESPONSIBILITIES ({len(responsibilities)}):")
            for resp in responsibilities[:4]:  # Show first 4
                print(f"   • {resp}")
            if len(responsibilities) > 4:
                print(f"   ... and {len(responsibilities) - 4} more")
        
        # Benefits
        benefits = data.get('benefits', [])
        if benefits:
            print(f"\n🎁 BENEFITS ({len(benefits)}):")
            for benefit in benefits[:3]:  # Show first 3
                print(f"   • {benefit}")
            if len(benefits) > 3:
                print(f"   ... and {len(benefits) - 3} more")
        
        # Application info
        app_info = data.get('application_info', {})
        if any(app_info.values()):
            print(f"\n📧 APPLICATION INFO:")
            if app_info.get('deadline'):
                print(f"   Deadline: {app_info['deadline']}")
            if app_info.get('contact'):
                print(f"   Contact: {app_info['contact']}")
            if app_info.get('process'):
                print(f"   Process: {app_info['process']}")

def main():
    """Main function for testing the job parser"""
    # Sample job description for testing
    sample_job = """
Senior Data Scientist - Machine Learning
Netflix | Los Gatos, CA | Full-time

About the Role:
We are seeking a Senior Data Scientist to join our ML team and build recommendation systems that delight our 200+ million members worldwide.

Responsibilities:
• Develop and deploy machine learning models for content recommendation
• Analyze large-scale user behavior data to drive product insights
• Design and execute A/B tests to measure model performance
• Collaborate with engineering teams to productionize ML models
• Present findings to leadership and stakeholders

Requirements:
• Master's or PhD in Computer Science, Statistics, or related field
• 5+ years of experience in data science and machine learning
• Expert proficiency in Python, SQL, and statistical modeling
• Experience with ML frameworks: TensorFlow, PyTorch, or scikit-learn
• Knowledge of big data tools: Spark, Hadoop, or similar
• Strong communication and collaboration skills

Preferred Qualifications:
• Experience with recommendation systems
• Knowledge of deep learning and neural networks
• Publications in ML/AI conferences
• Experience with cloud platforms (AWS, GCP)

What We Offer:
• Competitive salary: $160,000 - $240,000
• Comprehensive healthcare coverage
• Unlimited vacation policy
• Stock options and performance bonuses
• Professional development budget
• Free Netflix subscription

Apply by: December 15, 2024
Send resume to: datascience-jobs@netflix.com
"""
    
    print("🧪 TESTING JOB DESCRIPTION PARSER")
    print("=" * 40)
    
    # Initialize parser
    parser = JobDescriptionParser()
    
    # Parse the sample job
    result = parser.parse_job_description(sample_job)
    
    # Display results
    parser.display_parsed_job(result)
    
    if result["success"]:
        print(f"\n🎉 SUCCESS! Job parsing completed with Groq {parser.model}")
        print(f"\n📝 Usage:")
        print(f"   from job_description_parser import JobDescriptionParser")
        print(f"   parser = JobDescriptionParser(api_key='your_groq_key')")
        print(f"   result = parser.parse_job_description('job text here')")
        print(f"   parser.display_parsed_job(result)")
    else:
        print(f"\n❌ SETUP REQUIRED:")
        print(f"   1. Set your Groq API key in the code")
        print(f"   2. Install requests: pip install requests")
        print(f"   3. Get API key from: https://console.groq.com/keys")

if __name__ == "__main__":
    main()