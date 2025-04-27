from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import csv
import json
import datetime
import os
import time
import shutil
from jobspy import scrape_jobs
import pandas as pd
from hugchat import hugchat
from hugchat.login import Login


# Define API app
app = FastAPI(
    title="Job Finder API",
    description="API that fetches and filters relevant job listings from LinkedIn, Indeed, and Google Jobs",
    version="1.0.0"
)

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JobSearchCriteria(BaseModel):
    position: str
    experience: str
    salary: Optional[str] = None
    jobNature: Optional[str] = None
    location: str
    skills: str


class JobListing(BaseModel):
    job_title: str
    company: str
    experience: str
    jobNature: str
    location: str
    salary: str
    apply_link: str

class JobSearchResults(BaseModel):
    relevant_jobs: List[JobListing]


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)

def format_jobs(jobs_df, search_criteria):
    """Format jobs from raw data to required output structure"""
    formatted_jobs = []
    
    for _, job in jobs_df.iterrows():
     
        job_nature = "Remote" if job.get('is_remote', False) else "Onsite"
        
    
        min_amount = job.get('min_amount')
        max_amount = job.get('max_amount')
        currency = job.get('currency', 'PKR')
        
        if pd.notna(min_amount) and pd.notna(max_amount):
            salary = f"{min_amount} - {max_amount} {currency}"
        elif pd.notna(min_amount):
            salary = f"{min_amount} {currency}"
        elif pd.notna(max_amount):
            salary = f"{max_amount} {currency}"
        else:
            salary = "Not specified"
        
        formatted_job = {
            'job_title': job.get('title', 'N/A'),
            'company': job.get('company', 'N/A'),
            'experience': 'not found', 
            'jobNature': job_nature,
            'location': job.get('location', 'N/A'),
            'salary': salary,
            'apply_link': job.get('job_url', job.get('url', 'N/A'))
        }
        formatted_jobs.append(formatted_job)
    
    return formatted_jobs

def get_hugchat_bot():
    """Initialize and return HugChat bot with retry logic"""
    try:
        EMAIL = "betasoftlab@gmail.com"
        PASSWD = "Fast456@"
          
        cookie_path_dir = "./cookies/"
        
     
        if os.path.exists(cookie_path_dir):
            shutil.rmtree(cookie_path_dir)
        
        
        os.makedirs(cookie_path_dir, exist_ok=True)
        
        print("Creating new login session...")
        sign = Login(EMAIL, PASSWD)
        cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
        
      
        time.sleep(2)
        
      
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
        
       
        test_response = chatbot.chat("Hi").wait_until_done()
        print(f"Connection test successful. Response: {test_response[:30]}...")
        
        return chatbot
    except Exception as e:
        print(f"Error initializing HugChat: {e}")
        import traceback
        traceback.print_exc()
        return None

def filter_jobs_by_hugchat(formatted_jobs, search_criteria, max_retries=3):
    """Filter jobs based on relevance using HugChat with batch processing"""
    if not formatted_jobs:
        return []
    
    relevant_jobs = []
    chatbot = None
    
   
    for attempt in range(max_retries):
        print(f"HugChat initialization attempt {attempt + 1}/{max_retries}")
        chatbot = get_hugchat_bot()
        if chatbot:
            break
        
        time.sleep(2 ** attempt)
    
    if not chatbot:
        print("Failed to initialize HugChat after multiple attempts. Returning all jobs without filtering.")
        return formatted_jobs
    
    # Prepare the user criteria string
    user_criteria = f"""
    Position: {search_criteria.position}
    Experience: {search_criteria.experience}
    Salary: {search_criteria.salary if search_criteria.salary else 'Not specified'}
    Job Nature: {search_criteria.jobNature if search_criteria.jobNature else 'Not specified'}
    Location: {search_criteria.location}
    Skills: {search_criteria.skills}
    """
    
    print(f"Processing {len(formatted_jobs)} jobs for relevance...")
    
 
    base_delay = 2  
    current_delay = base_delay
    consecutive_rate_limits = 0
    
  
    batch_size = 2
    
    for batch_index in range(0, len(formatted_jobs), batch_size):
        # Get current batch of jobs
        batch_jobs = formatted_jobs[batch_index:batch_index + batch_size]
        
        print(f"\nBatch {batch_index // batch_size + 1} (jobs {batch_index + 1}-{min(batch_index + batch_size, len(formatted_jobs))})")
        
        
        if batch_index > 0 and batch_index % 10 == 0:
            pause_time = current_delay * 2
            print(f"Taking a break to avoid rate limits... (waiting {pause_time} seconds)")
            time.sleep(pause_time)
        
        
        batch_prompt = f"""
        I need to determine if these job listings are relevant to a user's criteria.
        
        User criteria:
        {user_criteria}
        
        For each job, respond with "Job X: Yes" if it's relevant or "Job X: No" if it's not relevant.
        
        """
        
        # Add each job to the batch prompt
        for i, job in enumerate(batch_jobs):
            job_info = f"""
            Job {i + 1}:
            Job Title: {job['job_title']}
            Company: {job['company']}
            Location: {job['location']}
            Job Nature: {job['jobNature']}
            Salary: {job['salary']}
            """
            batch_prompt += job_info
        
        batch_prompt += "\nFor each job, respond with ONLY 'Job X: Yes' or 'Job X: No'. One line per job."
        
      
        max_attempt_per_batch = 3
        batch_successful = False
        
        for job_attempt in range(max_attempt_per_batch):
            try:
                print(f"Sending batch request to HugChat... (Attempt {job_attempt+1}/{max_attempt_per_batch})")
             
                time.sleep(current_delay)
                
                response = chatbot.chat(batch_prompt).wait_until_done()
                print(f"HugChat batch response: {response}")
                
        
                consecutive_rate_limits = 0
                current_delay = base_delay
                batch_successful = True
                
              
                for i, job in enumerate(batch_jobs):
                    job_num = i + 1
                    print(f"Checking result for Job {batch_index + job_num}")
                    
                  
                    job_marker = f"Job {job_num}:"
                    job_result_line = None
                    
                   
                    for line in response.splitlines():
                        if job_marker in line:
                            job_result_line = line
                            break
                    
                    if job_result_line and "yes" in job_result_line.lower():
                        print(f"Job {batch_index + job_num} is relevant! Adding to results.")
                        relevant_jobs.append(job)
                    else:
                        print(f"Job {batch_index + job_num} is not relevant. Skipping.")
                
             
                break
                
            except Exception as e:
                error_str = str(e)
                print(f"Error processing batch with HugChat: {e}")
                
                if "429" in error_str:
                   
                    consecutive_rate_limits += 1
                    current_delay = base_delay * (2 ** consecutive_rate_limits)  
                    
                
                    if job_attempt == max_attempt_per_batch - 1:
                        print(f"Rate limit persists. Including all jobs in batch without filtering.")
                        relevant_jobs.extend(batch_jobs)
                    else:
                        wait_time = current_delay + (5 * job_attempt) 
                        print(f"Rate limited. Waiting {wait_time} seconds before retrying...")
                        time.sleep(wait_time)
                
                elif "401" in error_str:
                    
                    print("Authentication error. Attempting to reinitialize session...")
                    chatbot = get_hugchat_bot()
                    
              
                    if job_attempt == max_attempt_per_batch - 1:
                        print("Including all jobs in batch despite auth error.")
                        relevant_jobs.extend(batch_jobs)
                
                else:
               
                    print("Including all jobs in batch despite error.")
                    relevant_jobs.extend(batch_jobs)
                    break 
        
        
        if not batch_successful:
            print("Batch processing failed. Including all jobs in batch.")
            relevant_jobs.extend(batch_jobs)
    
    return relevant_jobs

# Alternative filtering using OpenAI API 
def filter_jobs_by_openai(formatted_jobs, search_criteria):
    """Filter jobs using OpenAI as a fallback option"""
    try:
        import openai
        
     
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        
        if not openai.api_key:
            print("OpenAI API key not found. Returning all jobs without filtering.")
            return formatted_jobs
            
        relevant_jobs = []
        
       
        user_criteria = f"""
        Position: {search_criteria.position}
        Experience: {search_criteria.experience}
        Salary: {search_criteria.salary if search_criteria.salary else 'Not specified'}
        Job Nature: {search_criteria.jobNature if search_criteria.jobNature else 'Not specified'}
        Location: {search_criteria.location}
        Skills: {search_criteria.skills}
        """
        
        # Process in batches
        batch_size = 3
        for batch_index in range(0, len(formatted_jobs), batch_size):
            batch_jobs = formatted_jobs[batch_index:batch_index + batch_size]
            
          
            batch_prompt = f"""
            I need to determine if these job listings are relevant to a user's criteria.
            
            User criteria:
            {user_criteria}
            
            For each job, respond with "Job X: Yes" if it's relevant or "Job X: No" if it's not relevant.
            """
            
           
            for i, job in enumerate(batch_jobs):
                job_info = f"""
                Job {i + 1}:
                Job Title: {job['job_title']}
                Company: {job['company']}
                Location: {job['location']}
                Job Nature: {job['jobNature']}
                Salary: {job['salary']}
                """
                batch_prompt += job_info
                
            batch_prompt += "\nFor each job, respond with ONLY 'Job X: Yes' or 'Job X: No'. One line per job."
            
           
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful job matching assistant. Respond with only Job X: Yes or Job X: No for each job."},
                    {"role": "user", "content": batch_prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
         
            response_text = response.choices[0].message.content
            
          
            for i, job in enumerate(batch_jobs):
                job_num = i + 1
                job_marker = f"Job {job_num}:"
                
             
                for line in response_text.splitlines():
                    if job_marker in line and "yes" in line.lower():
                        relevant_jobs.append(job)
                        break
            
           
            time.sleep(1)
            
        return relevant_jobs
        
    except Exception as e:
        print(f"OpenAI filtering failed: {e}")
       
        return formatted_jobs

# Define API routes
@app.get("/")
def read_root():
    return {"message": "Welcome to Job Finder API", "version": "1.0.0"}

@app.post("/api/jobs/search", response_model=JobSearchResults)
async def search_jobs(search_criteria: JobSearchCriteria):
    try:
        print(f"Searching for: {search_criteria.position} in {search_criteria.location}")
        
      
        raw_jobs = scrape_jobs(
            site_name=["indeed", "linkedin", "google"],
            search_term=search_criteria.position,
            location=search_criteria.location,
            results_wanted=20,  
            hours_old=72,  
            country_indeed='pakistan' if 'pakistan' in search_criteria.location.lower() else None
        )
        
        print(f"Found {len(raw_jobs)} raw job listings")
        
    
        formatted_jobs = format_jobs(raw_jobs, search_criteria)
        
     
        try:
            filtered_jobs = filter_jobs_by_hugchat(formatted_jobs, search_criteria)
        except Exception as e:
            print(f"HugChat filtering failed: {e}")
           
            filtered_jobs = filter_jobs_by_openai(formatted_jobs, search_criteria)
        
     
        if not filtered_jobs:
            print("No jobs passed relevance filtering. Returning top jobs without filtering.")
            filtered_jobs = formatted_jobs[:10] 
        
        return {"relevant_jobs": filtered_jobs}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching for jobs: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
