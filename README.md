# AI Resume Tailoring System 🚀

An intelligent system that customizes resumes for specific job descriptions using AI. Features both command-line interface and modern web application.

## ✨ Features

- **AI-Powered Resume Tailoring**: Uses Groq API to intelligently customize resumes for specific job requirements
- **Multiple Input Formats**: Supports PDF, DOCX for resumes; TXT, MD for job descriptions
- **Dual Interface**: Command-line tool for developers and web app for general users
- **Batch Processing**: Process multiple resumes against multiple job descriptions
- **ATS Optimization**: Generates resumes optimized for Applicant Tracking Systems
- **Multiple Output Formats**: Create tailored resumes in DOCX or PDF format

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/selvadevan/ai-resume-tailor.git
cd ai-resume-tailor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Groq API key:
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

Or edit the API key directly in the Python files.

## 🚀 Quick Start

### Command Line Interface

```bash
# Basic usage
python main.py resume.pdf job_description.txt

# Specify output format
python main.py my_cv.docx job.txt --format pdf

# Custom output filename
python main.py resume.pdf job.txt --output tailored_resume

# With API key
python main.py resume.pdf job.txt --api-key your_groq_key
```

### Web Application

```bash
# Launch Streamlit app (coming soon)
streamlit run streamlit_app.py
```

### Batch Processing

```bash
python batch_process.py --cvs-dir ./resumes --jobs-dir ./jobs --output-dir ./outputs
```

## 📁 Project Structure

```
ai-resume-tailor/
├── main.py                     # Main command-line application
├── batch_process.py            # Batch processing script
├── groq_resume_processor.py    # Resume data extraction
├── groq_resume_extractor.py    # AI-powered resume parsing
├── job_processor.py            # Job processing wrapper
├── job_description_parser.py   # Job description analysis
├── resume_generator.py         # Resume generation and formatting
├── document_converter_groq.py  # Document format conversion
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── examples/                   # Example files and usage
```

## 🎯 How It Works

1. **Document Processing**: Extracts text from PDF/DOCX resume files
2. **Data Extraction**: Uses AI to parse resume into structured data (skills, experience, education)
3. **Job Analysis**: Analyzes job descriptions to identify key requirements
4. **AI Tailoring**: Intelligently customizes resume content to match job requirements
5. **Output Generation**: Creates professionally formatted resume in desired format

## ⚙️ Configuration

The system uses Groq API with these models:
- **Extraction Model**: `openai/gpt-oss-20b` - for parsing resumes and job descriptions
- **Generation Model**: `qwen-3-32b` - for tailoring resume content

## 📝 Usage Examples

### Single Resume Processing

```python
from main import ResumeCustomizationSystem

# Initialize system
system = ResumeCustomizationSystem(api_key="your_groq_key")

# Process resume
result = system.run(
    cv_file="resume.pdf",
    job_file="job_description.txt",
    format_type="docx"
)

if result["success"]:
    print(f"✅ Tailored resume created: {result['output_file']}")
else:
    print(f"❌ Error: {result['error']}")
```

### Batch Processing

```python
from batch_process import BatchProcessor

processor = BatchProcessor(api_key="your_groq_key")
results = processor.process_directory(
    cvs_dir="./resumes",
    jobs_dir="./job_descriptions",
    output_dir="./tailored_resumes"
)
```

## 🔧 API Integration

The system integrates with Groq API for AI processing. You can:

1. Set API key via environment variable:
   ```bash
   export GROQ_API_KEY="your_key_here"
   ```

2. Pass API key as command line argument:
   ```bash
   python main.py resume.pdf job.txt --api-key your_key
   ```

3. Edit API keys directly in the Python files (for development)

## 📊 Output Formats

- **DOCX**: Microsoft Word format (default)
- **PDF**: Portable Document Format (requires additional setup)

## 🚨 Requirements

- Python 3.7+
- Groq API key
- Required Python packages (see requirements.txt)
- Optional: Pandoc (for PDF generation)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Include error logs and system information

## 🎉 Acknowledgments

- Built with Groq API for advanced AI capabilities
- Uses various open-source libraries for document processing
- Inspired by the need for ATS-optimized resume customization

---

**Made with ❤️ for job seekers everywhere**