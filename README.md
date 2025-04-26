# 📄 Job Finder API

A **FastAPI-based** microservice that **fetches** and **filters** relevant job listings from **LinkedIn**, **Indeed**, and **Google Jobs**, using **AI-powered filtering** based on user-defined criteria.

---

## 🚀 Features
- 🔍 Multi-source job search (**LinkedIn, Indeed, Google Jobs**)
- 🤖 **AI-powered filtering** using LLMs (Hugging Face, HugChat)
- ⚡ Fast and lightweight **RESTful API** with JSON response format
- 🔧 Configurable search parameters (position, experience, salary, job nature, skills, location)
- 📄 Auto-generated API documentation with **FastAPI Swagger UI**

---

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/job-finder-api.git
   cd job-finder-api
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create account on Hugging Face to use Hugchat file**
   - Create a `.env` file in the project root.
   - Add your HugChat (Hugging Face) credentials inside it:

     Example :
     ```
     EMAIL=your-email@example.com
     PASSWORD=your-password
     ```

---

## 🚀 Usage

1. **Start the FastAPI server**
   ```bash
   uvicorn main:app --reload
   ```

2. **API will be available at:**
   - Server: [http://localhost:8000](http://localhost:8000)
   - Swagger UI (API Docs): [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔥 API Endpoints

| Method | Endpoint | Description |
|:------|:---------|:------------|
| `GET` | `/` | API root - Displays welcome message |
| `POST` | `/api/jobs/search` | Search for jobs based on user criteria |

---

## 📋 Example Request

**POST** `/api/jobs/search`

```json
{
  "position": "Python Developer",
  "experience": "3 years",
  "salary": "80000",
  "jobNature": "Remote",
  "location": "USA",
  "skills": "Python, FastAPI, SQL"
}
```

---

## 🛠 Deployment Instructions

You can deploy the API easily to platforms like **Render**, **Railway**, or **Fly.io**.

**Typical Deployment Setup:**
- Connect GitHub repository to Render.com
- Set the **Build Command**:
  ```bash
  pip install -r requirements.txt
  ```
- Set the **Start Command**:
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 10000
  ```
- Choose **Free Plan** for hobby projects

After deployment, your API will be accessible via a **public URL** like:

```
https://job-finder-api.onrender.com
```

and your Swagger docs will be at:

```
https://job-finder-api.onrender.com/docs
```

---

## 📌 Important Notes
- **LinkedIn job scraping** may require API alternatives due to their scraping restrictions.
- **HugChat credentials** should be kept safe — use `.env` files and avoid uploading sensitive information to GitHub.
- The service respects API rate limits and includes retry logic to avoid temporary bans.

---

## 🧐 Technologies Used

- **Python 3.10+**
- **FastAPI**
- **Uvicorn** (ASGI server)
- **JobSpy** (Job scraping)
- **HugChat / Hugging Face LLMs** (AI-powered filtering)
- **Pandas** (Data handling)
- **Requests / HTTPX** (Networking)

---

## 🤝 Contributions

Contributions are welcome!  
Feel free to submit issues, feature requests, or pull requests to improve the project.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🌟 Final Words

Job Finder API helps candidates **find better jobs faster** by combining **real-time scraping** and **AI-based matching** into a **simple REST API**.

> "Smart job hunting — powered by FastAPI and AI."

---

## ✅ To-Do

- [x] LinkedIn, Indeed, Google Jobs scraping
- [x] HugChat AI-based filtering
- [x] FastAPI endpoint with POST method
- [x] Swagger UI docs
- [ ] Deployment to public cloud (Render, Railway)

---

