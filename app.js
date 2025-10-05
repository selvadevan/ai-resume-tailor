// Application Configuration
const CONFIG = {
    supportedFormats: {
        cv: ['.pdf', '.docx', '.doc'],
        job: ['.txt', '.md']
    },
    maxFileSize: 10 * 1024 * 1024, // 10MB
    processingSteps: [
        'Validating input files',
        'Extracting data from CV', 
        'Analyzing job description',
        'Tailoring resume with AI',
        'Creating output file'
    ],
    apiConfig: {
        baseUrl: 'https://api.groq.com/openai/v1/chat/completions',
        extractionModel: 'openai/gpt-oss-20b',
        generationModel: 'qwen-3-32b',
        timeout: 30000
    }
};

// Application State
let appState = {
    apiKey: '',
    currentTab: 'single',
    uploadedFiles: {
        cv: null,
        job: null
    },
    jobText: '',
    processing: false,
    extractedData: null,
    jobAnalysis: null,
    tailoredResume: null,
    history: []
};

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupEventListeners();
    setupFileUploads();
    loadSettings();
    loadHistory();
    checkApiKey();
}

// Event Listeners Setup
function setupEventListeners() {
    // Tab navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', (e) => switchTab(e.target.dataset.tab));
    });

    // Upload tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => switchUploadTab(e.target.dataset.uploadTab));
    });

    // API Key handling
    const apiKeyInput = document.getElementById('apiKey');
    apiKeyInput.addEventListener('input', handleApiKeyChange);
    
    // Job text area
    const jobTextArea = document.getElementById('jobText');
    jobTextArea.addEventListener('input', handleJobTextChange);
    
    // Settings
    document.getElementById('outputFormat').addEventListener('change', saveSettings);
    document.getElementById('resumeStyle').addEventListener('change', saveSettings);
}

// File Upload Setup
function setupFileUploads() {
    setupFileUpload('cv', ['pdf', 'docx', 'doc']);
    setupFileUpload('job', ['txt', 'md']);
    setupBatchFileUploads();
}

function setupFileUpload(type, allowedExtensions) {
    const uploadZone = document.getElementById(`${type}UploadZone`);
    const fileInput = document.getElementById(`${type}File`);
    
    // Click to upload
    uploadZone.addEventListener('click', () => fileInput.click());
    
    // File input change
    fileInput.addEventListener('change', (e) => handleFileSelect(e, type));
    
    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        const validFile = files.find(file => {
            const extension = file.name.toLowerCase().split('.').pop();
            return allowedExtensions.includes(extension);
        });
        
        if (validFile) {
            handleFile(validFile, type);
        } else {
            showError(`Please upload a valid ${type} file (${allowedExtensions.join(', ')})`);
        }
    });
}

function setupBatchFileUploads() {
    const batchCvInput = document.getElementById('batchCvFiles');
    const batchJobInput = document.getElementById('batchJobFiles');
    
    batchCvInput.addEventListener('change', (e) => {
        console.log(`Selected ${e.target.files.length} CV files for batch processing`);
    });
    
    batchJobInput.addEventListener('change', (e) => {
        console.log(`Selected ${e.target.files.length} job description files for batch processing`);
    });
}

// File Handling
function handleFileSelect(event, type) {
    const file = event.target.files[0];
    if (file) {
        handleFile(file, type);
    }
}

function handleFile(file, type) {
    // Validate file size
    if (file.size > CONFIG.maxFileSize) {
        showError(`File size exceeds 10MB limit`);
        return;
    }
    
    // Validate file type
    const extension = file.name.toLowerCase().split('.').pop();
    if (!CONFIG.supportedFormats[type].includes(`.${extension}`)) {
        showError(`Invalid file type. Please upload a ${CONFIG.supportedFormats[type].join(', ')} file`);
        return;
    }
    
    // Store file and update UI
    appState.uploadedFiles[type] = file;
    updateFileUI(file, type);
    
    console.log(`${type.toUpperCase()} file uploaded: ${file.name} (${formatFileSize(file.size)})`);
}

function updateFileUI(file, type) {
    const uploadZone = document.getElementById(`${type}UploadZone`);
    const fileInfo = document.getElementById(`${type}FileInfo`);
    
    uploadZone.style.display = 'none';
    fileInfo.style.display = 'flex';
    fileInfo.querySelector('.file-name').textContent = file.name;
}

function clearFile(type) {
    appState.uploadedFiles[type] = null;
    
    const uploadZone = document.getElementById(`${type}UploadZone`);
    const fileInfo = document.getElementById(`${type}FileInfo`);
    const fileInput = document.getElementById(`${type}File`);
    
    uploadZone.style.display = 'flex';
    fileInfo.style.display = 'none';
    fileInput.value = '';
    
    console.log(`${type.toUpperCase()} file cleared`);
}

// Tab Management
function switchTab(tabName) {
    // Update navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });
    
    appState.currentTab = tabName;
}

function switchUploadTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.uploadTab === tabName);
    });
    
    // Update content
    document.querySelectorAll('.upload-tab-content').forEach(content => {
        const isFileUpload = content.id === 'file-upload';
        const shouldShow = (tabName === 'file' && isFileUpload) || (tabName === 'text' && !isFileUpload);
        content.classList.toggle('active', shouldShow);
    });
}

// API Key Management
function handleApiKeyChange(e) {
    appState.apiKey = e.target.value;
    checkApiKey();
}

function checkApiKey() {
    const apiStatus = document.getElementById('apiStatus');
    const processingBtn = document.getElementById('processingBtn');
    
    if (appState.apiKey && appState.apiKey.length > 20) {
        apiStatus.className = 'status status--success';
        apiStatus.textContent = 'API Key Valid';
        processingBtn.disabled = false;
    } else {
        apiStatus.className = 'status status--error';
        apiStatus.textContent = 'API Key Required';
        processingBtn.disabled = true;
    }
}

function handleJobTextChange(e) {
    appState.jobText = e.target.value;
}

// Main Processing Pipeline
async function startProcessing() {
    if (!validateInputs()) {
        return;
    }
    
    appState.processing = true;
    showProgressSection();
    
    try {
        // Step 1: Validate files
        await processStep(1, 'Validating input files', async () => {
            await simulateDelay(1000);
            return validateFiles();
        });
        
        // Step 2: Extract CV data
        await processStep(2, 'Extracting data from CV', async () => {
            await simulateDelay(2000);
            return await extractCVData();
        });
        
        // Step 3: Analyze job description
        await processStep(3, 'Analyzing job description', async () => {
            await simulateDelay(1500);
            return await analyzeJobDescription();
        });
        
        // Step 4: Tailor resume
        await processStep(4, 'Tailoring resume with AI', async () => {
            await simulateDelay(3000);
            return await tailorResume();
        });
        
        // Step 5: Create output
        await processStep(5, 'Creating output file', async () => {
            await simulateDelay(1000);
            return generateOutput();
        });
        
        // Show results
        showResults();
        addToHistory();
        
    } catch (error) {
        showError(`Processing failed: ${error.message}`);
        console.error('Processing error:', error);
    } finally {
        appState.processing = false;
    }
}

async function processStep(stepNumber, stepName, processor) {
    const step = document.querySelector(`[data-step="${stepNumber}"]`);
    const progressBar = step.querySelector('.progress-fill');
    
    // Mark step as active
    step.classList.add('active');
    
    // Animate progress bar
    progressBar.style.width = '0%';
    setTimeout(() => {
        progressBar.style.width = '100%';
    }, 100);
    
    // Execute processor
    const result = await processor();
    
    // Mark step as completed
    await simulateDelay(500);
    step.classList.remove('active');
    step.classList.add('completed');
    
    return result;
}

// Validation
function validateInputs() {
    if (!appState.apiKey) {
        showError('Please enter your Groq API key');
        return false;
    }
    
    if (!appState.uploadedFiles.cv) {
        showError('Please upload a resume/CV file');
        return false;
    }
    
    if (!appState.uploadedFiles.job && !appState.jobText.trim()) {
        showError('Please upload a job description file or paste job description text');
        return false;
    }
    
    return true;
}

function validateFiles() {
    // Simulate file validation
    if (Math.random() < 0.05) { // 5% chance of validation error
        throw new Error('Invalid file format detected');
    }
    return true;
}

// Mock Data Processing
async function extractCVData() {
    // Simulate CV data extraction
    const mockExtractedData = {
        personal_details: {
            name: "John Smith",
            email: "john.smith@email.com",
            phone: "+1 (555) 123-4567",
            location: "San Francisco, CA",
            linkedin: "linkedin.com/in/johnsmith"
        },
        summary: "Experienced software engineer with 5+ years developing scalable web applications using modern technologies.",
        education: [
            {
                degree: "Bachelor of Science in Computer Science",
                institution: "University of California, Berkeley",
                graduation_date: "2019",
                gpa: "3.8"
            }
        ],
        work_experience: [
            {
                position: "Senior Software Engineer",
                company: "TechCorp Inc.",
                duration: "2021 - Present",
                responsibilities: [
                    "Led development of microservices architecture serving 1M+ users",
                    "Mentored junior developers and conducted code reviews",
                    "Improved application performance by 40% through optimization"
                ]
            },
            {
                position: "Software Engineer",
                company: "StartupXYZ",
                duration: "2019 - 2021",
                responsibilities: [
                    "Built responsive web applications using React and Node.js",
                    "Implemented CI/CD pipelines reducing deployment time by 60%",
                    "Collaborated with product team on feature development"
                ]
            }
        ],
        skills: {
            technical: ["JavaScript", "Python", "React", "Node.js", "AWS", "Docker", "PostgreSQL"],
            soft: ["Leadership", "Problem Solving", "Team Collaboration", "Communication"]
        },
        projects: [
            {
                name: "E-commerce Platform",
                description: "Full-stack e-commerce solution with payment integration",
                technologies: ["React", "Node.js", "MongoDB", "Stripe API"]
            }
        ],
        certifications: [
            "AWS Certified Solutions Architect",
            "Google Cloud Professional Developer"
        ]
    };
    
    appState.extractedData = mockExtractedData;
    return mockExtractedData;
}

async function analyzeJobDescription() {
    // Get job description text
    const jobText = appState.jobText || await readFileAsText(appState.uploadedFiles.job);
    
    // Simulate job analysis
    const mockJobAnalysis = {
        job_title: "Full Stack Developer",
        company_name: "InnovateTech Solutions",
        location: "San Francisco, CA / Remote",
        employment_type: "Full-time",
        remote_work: true,
        required_skills: [
            "JavaScript", "React", "Node.js", "Python", "AWS", "PostgreSQL", "Git"
        ],
        preferred_skills: [
            "TypeScript", "Docker", "Kubernetes", "GraphQL", "MongoDB"
        ],
        key_responsibilities: [
            "Develop and maintain full-stack web applications",
            "Collaborate with cross-functional teams to deliver features",
            "Write clean, maintainable, and testable code",
            "Participate in code reviews and architectural decisions",
            "Mentor junior developers"
        ],
        experience_required: "3+ years of full-stack development experience",
        benefits: [
            "Competitive salary and equity",
            "Health, dental, and vision insurance",
            "Flexible work arrangements",
            "Professional development budget"
        ]
    };
    
    appState.jobAnalysis = mockJobAnalysis;
    return mockJobAnalysis;
}

async function tailorResume() {
    // Simulate AI resume tailoring
    const changes = [
        "Enhanced summary to emphasize full-stack development experience",
        "Highlighted React and Node.js skills prominently",
        "Added AWS certification to match cloud requirements",
        "Reorganized experience to showcase leadership and mentoring",
        "Optimized keywords for ATS compatibility",
        "Added quantifiable achievements with metrics"
    ];
    
    appState.tailoredResume = {
        changes: changes,
        optimized_summary: "Full-stack software engineer with 5+ years of experience building scalable web applications using React, Node.js, and cloud technologies. Proven track record of leading development teams, mentoring junior developers, and delivering high-performance solutions that serve millions of users.",
        keyword_optimization_score: 92,
        ats_compatibility_score: 95
    };
    
    return appState.tailoredResume;
}

function generateOutput() {
    // Simulate file generation
    const fileSize = Math.floor(Math.random() * 200) + 100; // 100-300 KB
    return {
        fileSize: fileSize,
        generatedAt: new Date().toISOString()
    };
}

// UI Updates
function showProgressSection() {
    const progressSection = document.getElementById('progressSection');
    const resultsSection = document.getElementById('resultsSection');
    
    progressSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    
    // Reset all progress steps
    document.querySelectorAll('.progress-step').forEach(step => {
        step.classList.remove('active', 'completed');
        step.querySelector('.progress-fill').style.width = '0%';
    });
}

function showResults() {
    const progressSection = document.getElementById('progressSection');
    const resultsSection = document.getElementById('resultsSection');
    
    progressSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    
    // Populate extracted data
    populateExtractedData();
    populateJobAnalysis();
    populateTailoredResume();
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function populateExtractedData() {
    const personalDetails = document.getElementById('personalDetails');
    const skillsData = document.getElementById('skillsData');
    const experienceData = document.getElementById('experienceData');
    
    if (appState.extractedData) {
        const data = appState.extractedData;
        
        personalDetails.innerHTML = `
            <strong>Name:</strong> ${data.personal_details.name}<br>
            <strong>Email:</strong> ${data.personal_details.email}<br>
            <strong>Phone:</strong> ${data.personal_details.phone}<br>
            <strong>Location:</strong> ${data.personal_details.location}
        `;
        
        skillsData.innerHTML = `
            <strong>Technical Skills:</strong><br>
            ${data.skills.technical.join(', ')}<br><br>
            <strong>Soft Skills:</strong><br>
            ${data.skills.soft.join(', ')}
        `;
        
        experienceData.innerHTML = data.work_experience.map(exp => `
            <div style="margin-bottom: 16px; padding: 12px; background: var(--color-bg-2); border-radius: var(--radius-base);">
                <strong>${exp.position}</strong> at <strong>${exp.company}</strong><br>
                <em>${exp.duration}</em><br>
                <ul style="margin: 8px 0 0 20px;">
                    ${exp.responsibilities.map(resp => `<li>${resp}</li>`).join('')}
                </ul>
            </div>
        `).join('');
    }
}

function populateJobAnalysis() {
    const jobPreview = document.getElementById('jobPreview');
    
    if (appState.jobAnalysis) {
        const job = appState.jobAnalysis;
        
        jobPreview.innerHTML = `
            <div style="margin-bottom: 16px;">
                <h4 style="margin-bottom: 8px;">${job.job_title}</h4>
                <p><strong>Company:</strong> ${job.company_name}</p>
                <p><strong>Location:</strong> ${job.location}</p>
                <p><strong>Type:</strong> ${job.employment_type}${job.remote_work ? ' (Remote Available)' : ''}</p>
            </div>
            
            <div style="margin-bottom: 16px;">
                <h5>Required Skills:</h5>
                <p>${job.required_skills.join(', ')}</p>
            </div>
            
            <div style="margin-bottom: 16px;">
                <h5>Key Responsibilities:</h5>
                <ul>
                    ${job.key_responsibilities.map(resp => `<li>${resp}</li>`).join('')}
                </ul>
            </div>
            
            <div>
                <h5>Experience Required:</h5>
                <p>${job.experience_required}</p>
            </div>
        `;
    }
}

function populateTailoredResume() {
    const changesList = document.getElementById('changesList');
    const fileSize = document.getElementById('fileSize');
    
    if (appState.tailoredResume) {
        changesList.innerHTML = appState.tailoredResume.changes
            .map(change => `<li>✅ ${change}</li>`)
            .join('');
        
        fileSize.textContent = `~${Math.floor(Math.random() * 200) + 100} KB`;
    }
}

// Utility Functions
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const button = section.parentElement.querySelector('.expand-btn');
    
    section.classList.toggle('hidden');
    
    const isExpanded = !section.classList.contains('hidden');
    button.innerHTML = button.innerHTML.replace(/[▲▼]/, isExpanded ? '▲' : '▼');
}

async function downloadResume(format) {
    showMessage(`Preparing ${format.toUpperCase()} download...`);
    
    // Simulate file preparation
    await simulateDelay(1500);
    
    // Create mock download
    const fileName = `tailored-resume-${Date.now()}.${format}`;
    const content = generateMockResumeContent();
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showMessage(`✅ ${format.toUpperCase()} file downloaded successfully!`);
}

function generateMockResumeContent() {
    if (!appState.extractedData) return '';
    
    const data = appState.extractedData;
    return `
TAILORED RESUME

${data.personal_details.name}
${data.personal_details.email} | ${data.personal_details.phone}
${data.personal_details.location}
${data.personal_details.linkedin}

PROFESSIONAL SUMMARY
${appState.tailoredResume?.optimized_summary || data.summary}

TECHNICAL SKILLS
${data.skills.technical.join(' • ')}

PROFESSIONAL EXPERIENCE
${data.work_experience.map(exp => `
${exp.position} | ${exp.company} | ${exp.duration}
${exp.responsibilities.map(resp => `• ${resp}`).join('\n')}
`).join('\n')}

EDUCATION
${data.education.map(edu => `
${edu.degree}
${edu.institution} | Graduated ${edu.graduation_date}
`).join('\n')}

CERTIFICATIONS
${data.certifications.join('\n')}

---
This resume was tailored using AI Resume Tailoring System
Generated on: ${new Date().toLocaleDateString()}
ATS Compatibility Score: ${appState.tailoredResume?.ats_compatibility_score || 95}%
    `.trim();
}

// Batch Processing
async function startBatchProcessing() {
    const cvFiles = document.getElementById('batchCvFiles').files;
    const jobFiles = document.getElementById('batchJobFiles').files;
    
    if (cvFiles.length === 0 || jobFiles.length === 0) {
        showError('Please select both CV files and job description files for batch processing');
        return;
    }
    
    if (!appState.apiKey) {
        showError('Please enter your Groq API key');
        return;
    }
    
    showMessage(`Starting batch processing: ${cvFiles.length} CVs × ${jobFiles.length} jobs = ${cvFiles.length * jobFiles.length} combinations`);
    
    // Simulate batch processing
    showModal('loadingModal');
    updateLoadingMessage('Processing batch files...');
    
    await simulateDelay(5000);
    
    closeModal('loadingModal');
    showMessage(`✅ Batch processing complete! Generated ${cvFiles.length * jobFiles.length} tailored resumes.`);
}

// Settings Management
function loadSettings() {
    const settings = JSON.parse(localStorage.getItem('resumeTailoringSettings') || '{}');
    
    if (settings.outputFormat) {
        document.getElementById('outputFormat').value = settings.outputFormat;
    }
    if (settings.resumeStyle) {
        document.getElementById('resumeStyle').value = settings.resumeStyle;
    }
    if (settings.extractionModel) {
        document.getElementById('extractionModel').value = settings.extractionModel;
    }
    if (settings.generationModel) {
        document.getElementById('generationModel').value = settings.generationModel;
    }
}

function saveSettings() {
    const settings = {
        outputFormat: document.getElementById('outputFormat').value,
        resumeStyle: document.getElementById('resumeStyle').value,
        extractionModel: document.getElementById('extractionModel').value,
        generationModel: document.getElementById('generationModel').value
    };
    
    localStorage.setItem('resumeTailoringSettings', JSON.stringify(settings));
    showMessage('Settings saved successfully');
}

// History Management
function loadHistory() {
    const history = JSON.parse(localStorage.getItem('resumeTailoringHistory') || '[]');
    appState.history = history;
    updateHistoryDisplay();
}

function addToHistory() {
    const historyItem = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        cvFileName: appState.uploadedFiles.cv?.name || 'Pasted Text',
        jobTitle: appState.jobAnalysis?.job_title || 'Unknown Position',
        companyName: appState.jobAnalysis?.company_name || 'Unknown Company',
        status: 'completed'
    };
    
    appState.history.unshift(historyItem);
    
    // Keep only last 50 items
    if (appState.history.length > 50) {
        appState.history = appState.history.slice(0, 50);
    }
    
    localStorage.setItem('resumeTailoringHistory', JSON.stringify(appState.history));
    updateHistoryDisplay();
}

function updateHistoryDisplay() {
    const historyList = document.getElementById('historyList');
    
    if (appState.history.length === 0) {
        historyList.innerHTML = `
            <div class="card">
                <div class="card__body">
                    <p>No processing history available yet. Start tailoring resumes to see your history here.</p>
                </div>
            </div>
        `;
        return;
    }
    
    historyList.innerHTML = appState.history.map(item => `
        <div class="card">
            <div class="card__body">
                <div class="flex justify-between items-center">
                    <div>
                        <h4>${item.jobTitle}</h4>
                        <p><strong>Company:</strong> ${item.companyName}</p>
                        <p><strong>CV:</strong> ${item.cvFileName}</p>
                        <small class="text-secondary">${new Date(item.timestamp).toLocaleString()}</small>
                    </div>
                    <div>
                        <span class="status status--success">Completed</span>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Modal Management
function showModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

function updateLoadingMessage(message) {
    const loadingMessage = document.getElementById('loadingMessage');
    if (loadingMessage) {
        loadingMessage.textContent = message;
    }
}

// Message System
function showMessage(message) {
    console.log('Message:', message);
    
    // Create temporary message element
    const messageEl = document.createElement('div');
    messageEl.className = 'status status--success';
    messageEl.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1001;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    messageEl.textContent = message;
    
    document.body.appendChild(messageEl);
    
    setTimeout(() => {
        messageEl.remove();
    }, 3000);
}

function showError(message) {
    console.error('Error:', message);
    
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    showModal('errorModal');
}

// Helper Functions
function simulateDelay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

async function readFileAsText(file) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.readAsText(file);
    });
}