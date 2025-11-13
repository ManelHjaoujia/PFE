# PFE – AI Chatbot & NLP System  
**By Hjaoujia Manel**  
Data Scientist 
GitHub: [https://github.com/ManelHjaoujia](https://github.com/ManelHjaoujia)

---

## Table of Contents
1. [Project Overview](#project-overview)  
2. [Key Features](#key-features)  
3. [System Architecture](#system-architecture)  
4. [Technologies & Libraries](#technologies--libraries)  
5. [Modules & File Structure](#modules--file-structure)  
   - 5.1 CallCenterBancaire Module  
   - 5.2 DistilBERT Experiments  
   - 5.3 Django Web Application (Flask API)  
6. [Installation & Setup](#installation--setup)  
7. [Usage](#usage)  
8. [Models & Performance](#models--performance)  
9. [Deployment](#deployment)  
10. [Extending & Customization](#extending--customization)  
11. [Contributing](#contributing)         
12. [Contact](#contact)  

---

## Project Overview
This project is a comprehensive AI chatbot and NLP system designed for **banking call center operations**. Its goal is to improve service efficiency by analyzing, classifying, routing, and responding to customer calls or chat interactions.  

The system integrates:
- **Rasa**: For dialogue management, intent recognition, and entity extraction.  
- **DistilBERT**: Transformer-based NLP pipeline for semantic understanding and experimental benchmarking.  
- **Django Web Application + Flask API**: Provides a user interface, management dashboard, and API endpoints for integration with frontend, mobile, or call center systems.  

This project serves both as a **prototype for testing NLP approaches** and as a **deployable solution** for real-world call center operations.

---

## Key Features
- Intent classification and entity extraction for banking call transcripts  
- Routing engine for automated responses or agent escalations  
- Comparative analysis: Rasa vs. DistilBERT models  
- Web-based dashboard and management panel (Django)  
- Flask API endpoints for NLP module integration  
- Logging, analytics, and performance tracking  
- Modular and extensible architecture  

---

## System Architecture

Incoming Interaction (Call transcript / Chat)                            
↓                                 
Preprocessing Module                               
↓                                   
┌───────────────┐ ┌────────────────────────────┐                                  
│ Rasa Engine │ OR │ Transformer Pipeline │                                 
│ (Intent + │ │ (DistilBERT) │                                  
│ Entity) │ │ (Embeddings + Classification) │                              
└───────────────┘ └────────────────────────────┘                        
↓ ↓                         
Rasa Core / Policy & Tracker DistilBERT Logic                        
(Routing Engine / Dialogue Handler)                           
↓                               
Actions / Responses / Agent Escalation                       
↓                        
Logging & Analytics                     
↓                     
Flask API → Django Web Dashboard / Management Panel                              


---

## Technologies & Libraries
- Python 3.x  
- Rasa NLU + Core  
- Hugging Face Transformers (DistilBERT)  
- Scikit-learn, Pandas, NumPy  
- Jupyter Notebooks  
- Django + Flask API  
- Docker (optional)  
- Git & GitHub  

---

## Modules & File Structure

### 5.1 CallCenterBancaire Module
- Handles call transcript processing, intent classification, entity extraction, and routing logic.  
- Includes custom actions for account balance queries, transaction history, and PDF report generation.

### 5.2 DistilBERT Experiments
- Contains notebooks for **intent classification** and **named entity recognition (NER)**.  
- Fine-tuning and evaluation pipelines to benchmark transformer-based NLP models against Rasa.

### 5.3 Django Web Application (Flask API)
- **Django frontend:** Provides user-facing interface and admin panel.  
- **Flask API:** Handles communication between Rasa models and Django.  
- Each user has a **unique session ID** for conversation tracking.

## Installation & Setup

1. Clone the repository:

```bash
git clone https://github.com/ManelHjaoujia/PFE.git
cd PFE/Django
Install dependencies:
```

```bash
pip install -r requirements.txt
Apply Django migrations and create superuser:
```

```bash
python manage.py migrate
python manage.py createsuperuser
Configure API and dataset paths in config/ files.
```

## Usage

### CallCenterBancaire (Rasa)

Train, evaluate, and run your Rasa model:

```bash
# Train the model (NLU + Core)
rasa train

# Test NLU performance and get classification metrics
rasa test nlu --out results/nlu

# Test Core (stories / dialogue management)
rasa test core --out results/core

# Run the action server (for custom actions)
rasa run actions

# Start the Rasa server to interact via API
rasa run

# Optional interactive shell
rasa shell
```


 ### Flask API
```bash
POST /chat
Content-Type: application/json

{
  "message": "Bonjour, je souhaite consulter mon solde"
}
```
- API forwards messages to Rasa and returns bot responses.  
- Handles session management for multiple users.  

### Django Web Application

- Provides real-time chatbot interaction and admin dashboard.  
- Integrates Flask API and logs user conversations.  
- Supports dynamic Rasa actions and analytics tracking.  

### Models & Performance

| Pipeline       | Task                         | Accuracy | Micro F1 | Macro F1 | Weighted F1 | Notes                   |
|----------------|------------------------------|----------|----------|----------|-------------|------------------------|
| DistilBERT     | Intent Classification        | 0.9595   | 0.9589   | –        | –           | Benchmarking           |
| DistilBERT     | Entity Recognition (NER)     | 0.9795   | 0.9614   | 0.9645   | 0.9614      | Token classification   |
| Rasa           | Intent Classification        | 0.9854   | 0.9854   | 0.8849   | 0.9846      | Deployment model       |
| Rasa           | Entity Recognition (NER)     | 0.9788   | 0.9113   | 0.8694   | 0.9109      | Deployed with actions  |

**Summary:**  
- DistilBERT used for benchmarking; high F1 scores but limited to testing.  
- Rasa selected for deployment due to full **dialogue management, NLU, and custom actions**.  
- Custom actions allow **dynamic responses** and **PDF generation**.  

### Deployment

- Rasa runs as backend for NLU and dialogue management.  
- Flask API exposes `/chat` endpoint for message handling.  
- Django provides web interface and admin dashboard.  
- Can be deployed on **Docker** or cloud servers with proper configuration.  

### Extending & Customization

- Add new intents or entities in Rasa `domain.yml`.  
- Extend DistilBERT notebooks for additional NLP experiments.  
- Modify Django templates and views for custom dashboards.  
- Add extra API endpoints in Flask for advanced NLP integration.  

### Contributing

- Fork the repository  
- Create a feature branch (`git checkout -b feature-name`)  
- Commit changes (`git commit -m "Add feature"`)  
- Push to branch (`git push origin feature-name`)  
- Create a Pull Request  
 

### Contact

- Email: **manelhjawjia@gmail.com**  
- GitHub: [https://github.com/ManelHjaoujia](https://github.com/ManelHjaoujia)  
- LinkedIn: [[https://linkedin.com/in/hjaoujia-manel](https://linkedin.com/in/hjaoujia-manel](https://www.linkedin.com/in/manel-hjaoujia-35645734b/))
