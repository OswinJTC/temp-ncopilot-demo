# NIS LLM Data Interface

JuboAgent's data interface, implemented with FastAPI, is designed for processing JSON files exported from JuboAgent's LLM. It efficiently queries specific user-requested information from MongoDB.

## Quick Start

### 1. Endpoints

#### POST `/initial-layer`
- **Description**: The primary endpoint for receiving initial JSON data from the LLM.

- **Request Body**: This JSON file requests the highest three systolic blood pressure (SYS) readings for 憨斑斑 within the past three months.
    ```json
    {
      "queries": [
        {
          "interface_type": "vitalsigns",
          "patientName": "憨斑斑",
          "retrieve": ["SYS", "createdDate"],
          "conditions": {
            "duration": 90,
            "sortby": {"SYS": "descending"},
            "limit": 3
          }
        }
      ]
    }
    ```

- **Response**:
    ```json
    [
      {
        "SYS": 140,
        "createdDate": "2024-05-02T09:02:10Z"
      },
      {
        "SYS": 138,
        "createdDate": "2024-04-14T10:04:34Z"
      },
      {
        "SYS": 131,
        "createdDate": "2024-06-22T07:31:25Z"
      }
    ]
    ```

### 2. Code Structure

1. **Endpoint receives data:**
    ```python
    from app.db.database import startup_event
    startup_event()
    ```

2. **Send to factory with parameters:**
    ```python
    from app.factory import DataInterfaceFactory

    factory = DataInterfaceFactory()
    interface = factory.get_interface("vitalsigns", query_dict, projection, conditions)
    results = interface.execute()
    ```

3. **Factory distributes to interfaces:**
    ```python
    from app.factory import DataInterfaceFactory

    factory = DataInterfaceFactory()
    interface = factory.get_interface("vitalsigns", query_dict, projection, conditions)
    results = interface.execute()
    ```

4. **Interfaces begin to query and get data from the database:**
    ```python
    from app.factory import DataInterfaceFactory

    factory = DataInterfaceFactory()
    interface = factory.get_interface("vitalsigns", query_dict, projection, conditions)
    results = interface.execute()
    ```

Feel free to modify and enhance this README file according to your project needs.
