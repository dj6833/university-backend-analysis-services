# University Management System - Backend Services (Analysis)

This repository contains server-side data analysis services for the University Management System. It currently handles the class-recommendation requests and cloud availability health monitoring, demonstrating a microservice pattern optimised across decoupled runtime languages and isolated service layers.

> [!NOTE]
>
> For an introduction and overview of the University Management System project, please first visit my **[Profile Page](https://github.com/dj6833)**

## 🛠️ Tech Stack

Python | FastAPI | Uvicorn

## 🏁 Getting Started
1. Clone this repository to your machine
2. Create an isolated Python virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   * **Windows:** `.venv\Scripts\activate`
   * **macOS/Linux:** `source .venv/bin/activate`
4. Install all required dependencies and framework packages: `pip install -r requirements.txt`
5. Configure your environment variables file by copying the `.env.example` 
file, rename the copy to `.env` and update it with your cross-service API credentials, frontend URL, and database connection string
6. Run the development server; the API endpoints will begin listening for requests

## 📜 Available Scripts

### Running the development server.

```bash
python -m uvicorn main:app --port 5000
```

## ⚖️ License

This project is published under the terms of the **GNU General Public License v3.0 (GPL-3.0)**.

For full license details, please see the accompanying `LICENSE` file included in the root directory of this repository.