# **Developer Productivity: Intelligent IDE**  

## **Overview**  
Developer Productivity: Intelligent IDE is an AI-powered assistant designed to enhance coding efficiency by automating problem analysis, code generation, testing, debugging, and optimization. Built using **OpenAI’s API with AutoGen**, it supports multiple programming languages and streamlines the development process.  

---

## **Features**  
✅ AI-driven problem breakdown and analysis  
✅ Code generation in multiple programming languages  
✅ Automated unit test generation and execution  
✅ Code optimization for performance improvement  
✅ User-friendly interface with Streamlit integration  
✅ CI/CD automation using GitHub Actions  

---

## **Installation & Setup**  

### **1. Clone the Repository**  
```bash
git clone [GitHub Repository URL]
cd [Repository Name]
```

### **2. Set Up a Virtual Environment**  
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows
```

### **3. Install Dependencies**  
```bash
pip install -r requirements.txt
```

### **4. Set Up API Key**  
Create a `.env` file in the project root and add your OpenAI API key:  
```
OPENAI_API_KEY=your_api_key_here
```

---

## **Usage**  

### **Run the AI Assistant (Streamlit Interface)**
```bash
streamlit run app.py
```
This will launch a web interface where users can input coding problems and receive AI-generated solutions.  

### **Run Locally (CLI Mode)**
```bash
python main.py
```
This will execute the AI-driven multi-agent system from the command line.  

---

## **Project Structure**  
```
📂 Developer-Productivity-IDE
│-- 📂 src                  # Core AI logic and multi-agent implementation  
│-- 📂 tests                # Unit tests for generated code  
│-- 📜 main.py              # Entry point for CLI mode  
│-- 📜 app.py               # Streamlit-based UI  
│-- 📜 requirements.txt     # Dependencies  
│-- 📜 README.md            # Documentation  
│-- 📜 .env.example         # Example file for API key setup  
```

---

## **Testing**  
The system includes automated unit testing to verify generated code. To run tests:  
```bash
pytest tests/
```
This ensures that all AI-generated solutions are properly validated before deployment.  

---

## **Deployment**  
The system uses **GitHub Actions for CI/CD** to automatically test and validate code before merging changes. For deployment:  
```bash
git push origin main
```
The pipeline will handle testing and validation automatically.
