# afeyagroup
stock analysis dashboard for novice stock investor

.vscode/
    launch.json
    settings.json
backend/
    .env
    app/
    Dockerfile
    requirements.txt
    tests/
database/
    docker-entrypoint-initdb.d/
docker-compose.yml
frontend/
    .dockerignore
    .env
    .eslintrc.cjs
    .gitignore
    .prettierrc.json
    .vscode/
    Dockerfile
    env.d.ts
    index.html
    LICENSE
    nginx.conf
    package.json
    postcss.config.js
    public/
    README.md
    src/
    tailwind.config.js
    tsconfig.app.json
    tsconfig.json
    ...
package.json
README.md
stockVenv/
    bin/
    ...
websockets-server.py
websocketsClinet.py

Prerequisites
Docker
Docker Compose

Getting Started

Backend
Navigate to the backend directory:
cd backend

Build the Docker image:
docker build -t backend .

Run the backend container:
docker run -d --name backend -p 8000:8000 backend

Frontend
Navigate to the frontend directory:
cd frontend

Build the Docker image:
docker build -t frontend .

Run the frontend container:
docker run -d --name frontend -p 3000:80 frontend

Database
Navigate to the root directory:
cd ..

Start the database container using Docker Compose:
docker-compose up -d

This will start the backend, frontend, and database services.

Environment Variables
Backend
DB_HOST: Database host
DB_PORT: Database port
DB_USER: Database user
DB_PASSWORD: Database password
DB_NAME: Database name
Frontend
VITE_BACKEND_URL: URL of the backend service

Testing
Backend

Navigate to the backend directory:
cd backend

Run the tests:
pytest

License
This project is licensed under the MIT License. See the LICENSE file for details.

Contributing
Contributions are welcome! Please open an issue or submit a pull request for any changes.

Contact
For any questions or inquiries, please contact the project maintainer.

This README provides an overview of the project structure, setup instructions, and other relevant information to help you get started with the stock management system.