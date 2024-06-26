
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
            "sortby": {"SYS": "descending"},
            "limit": 3
          }
        },
        {
          "interface_type": "vitalsigns",
          "patientName": "憨斑斑",
          "retrieve": ["SPO2"],
          "conditions": {
            "duration": 90,
            "sortby": {"SPO2": "descending"},
            "limit": 3
          }
        }
      ]
    }
    ```
- **Response**:
    ```json
    {
      "results": [...]
    }
    ```

#### GET `/test-gcp-credentials`
- **Description**: Tests GCP credentials access.
- **Response**:
    ```json
    {
      "message": "Successfully accessed secret",
      "secret_data": "..."
    }
    ```

### Usage

1. **Initialize MongoDB Collections:**
    ```python
    from app.db.database import startup_event
    startup_event()
    ```

2. **Execute Queries:**
    ```python
    from app.factory import DataInterfaceFactory

    factory = DataInterfaceFactory()
    interface = factory.get_interface("vitalsigns", query_dict, projection, conditions)
    results = interface.execute()
    ```

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for review.

## License
This project is licensed under the MIT License.
