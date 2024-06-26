# NIS LLM Data Interface

## Overview
A FastAPI application that serves as a data interface for querying vital signs and patient information from MongoDB.

## Project Structure


## Quick Start

### Prerequisites
- Python 3.10
- MongoDB

### Setup

1. **Clone the repository:**
    ```bash
    git clone https://gitlab.com/your-username/nis-llm-data-interface.git
    cd nis-llm-data-interface
    ```

2. **Create a virtual environment and activate it:**
    ```bash
    python3.10 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure MongoDB connection in `database.py`:**

5. **Run the application:**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```

### Endpoints

#### GET `/home`
- **Description**: Returns a welcome message.
- **Response**:
    ```json
    {
      "message": "Welcome to the nis-llm-data-interface"
    }
    ```

#### POST `/initial-layer`
- **Description**: Executes complex queries to retrieve vital signs data.
- **Request Body**:
    ```json
    {
      "queries": [
        {
          "interface_type": "vitalsigns",
          "patientName": "憨斑斑",
          "retrieve": ["SYS"],
          "conditions": {
            "duration": 90,
            "sortby": {"SYS
