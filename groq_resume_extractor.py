"""
Resume Data Extraction System - Custom Groq Integration
Uses Groq API with openai/gpt-oss-20b model and embedded API key
"""

import json
import requests
from typing import Dict, Any, List, Optional
import re
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqResumeExtractor:
    """Extract structured data from resume text using Groq API with custom model"""
    
    def __init__(self, api_key: str = None):
        # ⚠️ REPLACE WITH YOUR ACTUAL GROQ API KEY
        self.api_key = api_key or "YOUR_GROQ_API_KEY_HERE"  # PUT YOUR KEY HERE
        # Specific model requested
        self.model = "openai/gpt-oss-20b"
        # Groq API endpoint
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        logger.info(f"Groq extractor initialized with model: {self.model}")
    
    def create_extraction_prompt(self, resume_text: str) -> str:
        """Create a structured prompt for resume extraction"""
        prompt = f"""
You are an expert resume parser. Extract structured information from the following resume text and return it as valid JSON.

RESUME TEXT:
{resume_text}

Extract and structure the information into this exact JSON format:

{{
  "personal_details": {{
    "name": "Full name of the person",
    "email": "Email address",
    "phone": "Phone number",
    "address": "Physical address",
    "linkedin": "LinkedIn profile URL",
    "github": "GitHub profile URL",
    "website": "Personal website URL"
  }},
  "education": [
    {{
      "degree": "Degree type and field",
      "institution": "School/University name",
      "graduation_year": "Year of graduation",
      "gpa": "GPA if mentioned",
      "location": "Location of institution"
    }}
  ],
  "work_experience": [
    {{
      "position": "Job title",
      "company": "Company name",
      "start_date": "Start date",
      "end_date": "End date or 'Present'",
      "location": "Work location",
      "description": "Job responsibilities and achievements",
      "technologies": ["List of technologies used"]
    }}
  ],
  "skills": {{
    "technical_skills": ["Programming languages, tools, frameworks"],
    "soft_skills": ["Communication, leadership, etc."],
    "languages": ["Spoken languages with proficiency level"]
  }},
  "achievements": [
    {{
      "title": "Achievement title",
      "description": "Description of achievement",
      "date": "Date or year"
    }}
  ],
  "projects": [
    {{
      "name": "Project name",
      "description": "Project description",
      "technologies": ["Technologies used"],
      "url": "Project URL if available",
      "date": "Project date"
    }}
  ],
  "certifications": [
    {{
      "name": "Certification name",
      "issuer": "Issuing organization",
      "date": "Issue date",
      "expiry": "Expiry date if applicable"
    }}
  ],
  "summary": "Brief professional summary"
}}

IMPORTANT RULES:
1. Return ONLY valid JSON
2. Use empty string "" for missing text fields
3. Use empty array [] for missing lists
4. Do not include any explanatory text outside the JSON
5. Ensure all JSON brackets are properly closed
"""
        return prompt
    
    def extract_with_groq(self, resume_text: str) -> Dict[str, Any]:
        """Extract resume data using Groq API with openai/gpt-oss-20b model"""
        try:
            if self.api_key == "YOUR_GROQ_API_KEY_HERE":
                return {
                    "success": False,
                    "error": "Please replace 'YOUR_GROQ_API_KEY_HERE' with your actual Groq API key in the code"
                }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = self.create_extraction_prompt(resume_text)
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert resume parser. Extract structured information from resumes and return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 2500,
                "stream": False
            }
            
            logger.info(f"Sending request to Groq API with model: {self.model}")
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                content = response_data["choices"][0]["message"]["content"]
                logger.info(f"Groq API response received, content length: {len(content)}")
                
                # Extract JSON from response
                json_text = self._extract_json_from_response(content)
                if json_text:
                    try:
                        result = json.loads(json_text)
                        logger.info(f"✅ Groq extraction completed successfully with {self.model}")
                        return {
                            "success": True,
                            "data": result,
                            "provider": f"groq-{self.model}",
                            "raw_response": content[:200] + "..." if len(content) > 200 else content
                        }
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {str(e)}")
                        logger.error(f"Problematic JSON: {json_text[:500]}...")
                        return {
                            "success": False,
                            "error": f"Invalid JSON response from Groq: {str(e)}",
                            "raw_response": content
                        }
                else:
                    return {
                        "success": False,
                        "error": "Could not extract valid JSON from Groq response",
                        "raw_response": content
                    }
            else:
                error_msg = f"Groq API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Groq API request timed out"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Groq API request failed: {str(e)}"}
        except Exception as e:
            logger.error(f"Groq extraction failed: {str(e)}")
            return {"success": False, "error": f"Groq extraction failed: {str(e)}"}
    
    def _extract_json_from_response(self, content: str) -> str:
        """Extract JSON from the response content"""
        # Try different patterns to find JSON
        
        # Pattern 1: JSON wrapped in code blocks
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            if json_end != -1:
                return content[json_start:json_end].strip()
        
        # Pattern 2: JSON wrapped in code blocks without language
        if "```" in content:
            first_code_block = content.find("```") + 3
            second_code_block = content.find("```", first_code_block)
            if second_code_block != -1:
                potential_json = content[first_code_block:second_code_block].strip()
                if potential_json.startswith("{") and potential_json.endswith("}"):
                    return potential_json
        
        # Pattern 3: Find JSON between first { and last }
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            return content[json_start:json_end]
        
        # Pattern 4: Try the entire content if it looks like JSON
        content = content.strip()
        if content.startswith("{") and content.endswith("}"):
            return content
        
        return ""
    
    def extract_resume_data(self, resume_text: str) -> Dict[str, Any]:
        """Main method to extract resume data"""
        return self.extract_with_groq(resume_text)

if __name__ == "__main__":
    # Test the Groq extractor
    sample_text = """
Sarah Johnson
Senior Data Scientist

Email: sarah.johnson@email.com
Phone: (555) 123-4567
LinkedIn: linkedin.com/in/sarahjohnson
GitHub: github.com/sarahjohnson

EDUCATION
Master of Science in Data Science
Stanford University, 2021
GPA: 3.9/4.0

WORK EXPERIENCE
Senior Data Scientist
Google | March 2022 - Present | Mountain View, CA
• Developed ML models for search ranking improving CTR by 15%
• Led data science team of 4 engineers
• Technologies: Python, TensorFlow, BigQuery, Kubernetes

TECHNICAL SKILLS
Programming: Python, R, SQL, Java, Scala
ML/AI: TensorFlow, PyTorch, Scikit-learn, XGBoost
Big Data: Spark, Hadoop, Kafka, Airflow
Cloud: AWS, GCP, Azure, Kubernetes, Docker

PROJECTS
Movie Recommendation System (2021)
• Built end-to-end ML pipeline for movie recommendations
• Achieved 85% user satisfaction rate
• Technologies: Python, TensorFlow, Apache Beam, GCP

CERTIFICATIONS
Google Cloud Professional Data Engineer (2022)
AWS Certified Machine Learning - Specialty (2021)
"""
    
    print("🧪 Testing Groq API with openai/gpt-oss-20b model...")
    print("⚠️ Make sure to replace 'YOUR_GROQ_API_KEY_HERE' with your actual API key!")
    
    # Initialize extractor
    extractor = GroqResumeExtractor()
    
    # Test extraction
    result = extractor.extract_resume_data(sample_text)
    
    if result["success"]:
        print("\n✅ Groq extraction successful!")
        print(f"Provider: {result['provider']}")
        print(f"Name: {result['data']['personal_details']['name']}")
        print(f"Email: {result['data']['personal_details']['email']}")
        print(f"Skills found: {len(result['data']['skills']['technical_skills'])}")
        print(f"Experience: {len(result['data']['work_experience'])} positions")
    else:
        print(f"\n❌ Groq extraction failed: {result['error']}")
        if "raw_response" in result:
            print(f"Raw response: {result['raw_response'][:200]}...")