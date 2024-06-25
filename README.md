# NIS LLM Data Interface

## Overview
This repository contains a FastAPI application that serves as a data interface for querying vital signs and other related data. The application provides endpoints for executing complex queries and listing vital signs for a specified patient.

## Table of Contents
- [Setup](#setup)
- [Running the Application](#running-the-application)
- [Endpoints](#endpoints)
- [Usage](#usage)
- [Testing with Postman](#testing-with-postman)
- [Contributing](#contributing)
- [License](#license)

## Setup

### Prerequisites
- Python 3.10
- Docker and Docker Compose (optional, for containerization)
- MongoDB

### Installation

1. Clone the repository:
    ```bash
    git clone https://gitlab.com/your-username/nis-llm-data-interface.git
    cd nis-llm-data-interface
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3.10 -m venv venv
    source venv/bin/activate
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Ensure MongoDB is running and accessible. Update the MongoDB connection details in your application if necessary.

## Running the Application

### Using Uvicorn

Run the FastAPI application using Uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
