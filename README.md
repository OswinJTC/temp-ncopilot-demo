# NIS LLM Data Interface
## Quick Start
JuboAgent's data interface, implemented with FastAPI, is designed for processing JSON files exported from JuboAgent's LLM. It efficiently queries specific user-requested information from MongoDB.

## Endpoints


#### POST `/initial-layer`
- **Description**: The primary endpoint for receiving initial JSON data from the LLM.

- **Request Body**: This JSON file stands for, getting 憨斑斑三個月內前三高的血壓 (SYS).
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




### Code Structure

1. **Endiont receive data:**
    ```python
    from app.db.database import startup_event
    startup_event()
    ```

2. **Send to factory witht parametr**
    ```python
    from app.factory import DataInterfaceFactory

    factory = DataInterfaceFactory()
    interface = factory.get_interface("vitalsigns", query_dict, projection, conditions)
    results = interface.execute()

3. **Factory distribute to interfaces**
    ```python
    from app.db.database import startup_event
    startup_event()
    ```

4. **Interfaces b egin to query and get data from db**
    ```python
    from app.factory import DataInterfaceFactory

    factory = DataInterfaceFactory()
    interface = factory.get_interface("vitalsigns", query_dict, projection, conditions)
    results = interface.execute()
    ```


