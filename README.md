# 📈 AfeyaGroup - Stock Portfolio & Analytics Platform

AfeyaGroup is a full-stack web application for managing and analyzing stock portfolios. It includes:

- A FastAPI backend with PostgreSQL for storing user and stock data
- Kafka for real-time market updates
- Redis for rate limiting and caching
- A frontend UI (Vue or React-based)
- Docker-based development and deployment setup

---

## 🚀 Features

- User registration and authentication
- Add/update/delete tracked stocks
- Fetch live quotes from Finnhub
- Publish stock data to Kafka
- Redis-backed rate limiting
- Modular FastAPI API with Swagger docs

---

## 📦 Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Vue.js or React (TBD)
- **Messaging**: Kafka (via aiokafka)
- **Caching / Rate Limiting**: Redis
- **Containerization**: Docker, Docker Compose

---

## 🛠️ Setup Instructions

### 1. 🔧 Prerequisites

- Docker & Docker Compose installed
- Python 3.11+ installed locally (for non-Docker testing)
- Optional: PostgreSQL, Redis, Kafka CLI for local testing
- A **[Finnhub API Key](https://finnhub.io/)**

---

### 2. 📁 Project Structure

afeyagroup/ 
    ├── backend/ # FastAPI backend │ ├── app/ # Routes, models, db │ └── main.py # API entry point ├── frontend/ # UI (Vue/React) ├── database/ │ └── docker-entrypoint-initdb.d/init.sql ├── docker-compose.yml ├── .env # Environment variables └── README.md


---

### 3. 📄 .env Example

Create a `.env` file at the root:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=stock_db
DB_HOST=postgres
REDIS_HOST=redis
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
FINNHUB_API_KEY=your_actual_finnhub_api_key_here

# Start all services (Postgres, Redis, Kafka, Backend, Frontend)
docker-compose up --build
API available at: http://localhost:8000

Swagger UI: http://localhost:8000/docs

Frontend (if applicable): http://localhost:3000

cd backend
uvicorn main:app --reload
black .

🧰 Useful Docker Commands
docker-compose down           # Stop all containers
docker-compose down -v        # ⚠️ Stops containers and deletes volumes (data loss!)
docker volume ls              # See volumes
docker exec -it postgres psql -U postgres -d stock_db  # Access PostgreSQL CLI

🤝 Contributing
🛠 Local Dev Setup
git clone https://github.com/amirjaffery23/afeyagroup.git
cd afeyagroup
cp .env.example .env
docker-compose up --build

👣 Contribution Steps
Fork the repo and create your feature branch:

bash
Copy
Edit
git checkout -b feature/your-feature
Make your changes and commit:

bash
Copy
Edit
git commit -m "Add: Your feature summary"
Push to your branch:

bash
Copy
Edit
git push origin feature/your-feature
Open a Pull Request!

🔍 Code Style
Follow PEP8

Format Python with black

Write docstrings for new functions/classes

🧑‍💻 Maintainers
@amirjaffery23

📄 License
MIT License. See LICENSE file.
