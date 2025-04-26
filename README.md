Job Finder API
A FastAPI-based API that fetches and filters relevant job listings from LinkedIn, Indeed, and Google Jobs.

Features
Multi-source job search (LinkedIn, Indeed, Google Jobs)
AI-powered filtering based on user criteria
RESTful API with JSON response format
Configurable search parameters
Installation
Clone this repository
Install dependencies:
pip install -r requirements.txt
Create .env file with your credentials (see .env.example)
Usage
Start the API server:

uvicorn main:app --reload
The API will be available at http://localhost:8000
fASTAPI: http://localhost:8000/docs

API Endpoints
GET / - API root, displays welcome message
POST /api/jobs/search - Search for jobs based on criteria
Example Request
json
{
  "position": "Python Developer",
  "experience": "3 years",
  "salary": "80000",
  "jobNature": "Remote",
  "location": "USA",
  "skills": "Python, FastAPI, SQL"
}
Deployment
