# Industrial Equipment Analytics: Hybrid Full-Stack System
### FOSSEE Internship Screening Task - 2026
A robust, cross-platform ecosystem designed for industrial equipment monitoring. This project integrates a central Django REST API with a React-based Web Dashboard and a PyQt5 Desktop Client.

## 🛠️ Tech Stack

->Backend: Python, Django, Django REST Framework

->Web Frontend: React.js, Axios, Chart.js

->Desktop Frontend: Python, PyQt5

->Data & Reports: Pandas (CSV Analysis), ReportLab (PDF Generation)

## 📂 Project Structure

->chemical_backend/: Django project housing the API and core logic.

->analytics/: Django app for data processing, PDF generation, and CSV handling.

->chemical_frontend/: React source code for the interactive web dashboard.

->desktop_app/: Python PyQt5 source code for the desktop monitoring client.

## ⚙️ Setup & Installation

1. Backend Setup

  # Clone the repository
  
  git clone https://github.com/Gadi-Satwika/Hybrid-App-Framework.git
  
  cd Hybrid-App-Framework
  
  # Create and activate virtual environment
  
  python -m venv venv
  
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  
  # Install dependencies
  
  pip install -r requirements.txt
  
  # Run migrations and start server
  
  python manage.py migrate
  
  python manage.py runserver

2. Web Frontend Setup

  cd chemical_frontend
  
  npm install
  
  npm start

3. Desktop App Setup
   
  cd desktop_app
  
  python main.py
  
## ✨ Features

->Cross-Platform Integration: Unified API serving both Web and Desktop clients.

->Secure Authentication: Implements Basic Authentication for industrial data security.

->Automated Analytics: Processes CSV equipment data using Pandas to detect anomalies.

->Professional Reporting: Generates downloadable PDF reports using ReportLab.


### Developed by: Gadi Satwika 3rd Year B.Tech CSE Student, RGUKT RK Valley

