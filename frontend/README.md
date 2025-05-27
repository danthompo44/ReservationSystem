# Reservation System Application

## Overview
The Reservation System is a web application built using FastAPI for the backend and Next.js for the frontend. It allows users to manage reservations and topologies in a seamless manner.

## Prerequisites
To run this application, you need to have the following software installed on your machine:

- **Docker**: Ensure you have Docker installed to run the application in containers.
- **Docker Compose**: This is included with Docker Desktop installations, but if you are using Linux, you may need to install it separately.
- **Node.js**: Required for the frontend application. You can download it from [Node.js official website](https://nodejs.org/).
- **Python**: Required for the backend application. You can download it from [Python official website](https://www.python.org/).

## Running the Application
To run the application, follow these steps:

1. Clone the repository to your local machine:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Build and start the application using Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Access the frontend application at `http://localhost:3000` and the backend API at `http://localhost:8000`.

## Development Guidelines

### Python (Backend)
- Follow PEP 8 style guidelines for Python code.
- Use type hints for function signatures to improve code readability and maintainability.
- Ensure that all dependencies are listed in `requirements.txt`.
- Write unit tests for your code and ensure they pass before committing changes.

### JavaScript (Frontend)
- Follow the Airbnb JavaScript Style Guide for consistent code formatting.
- Use ES6+ features where applicable, such as arrow functions and destructuring.
- Ensure that all dependencies are listed in `package.json`.
- Write unit tests for your components and ensure they pass before committing changes.

## Conclusion
This README provides a basic overview of the Reservation System application, how to set it up, and guidelines for contributing to the project. For further information, please refer to the documentation within the codebase.
