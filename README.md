# NIS LLM Data Interface

JuboAgent's data interface, implemented with FastAPI, is designed for processing JSON files exported from JuboAgent's LLM. It efficiently queries specific user-requested information from MongoDB.

## Quick Start

### 1. Endpoints

#### POST `/initial-layer`
- **Description**: The primary endpoint for receiving initial JSON data from the LLM.

- **Request Body**: 幫我回傳憨斑斑三個月內前三高的血壓 (SYS) 和當天日期。
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
    @router.post("/initial-layer")
    async def execute_queries(params: RequestParams):
        try:
            results = [DataInterfaceFactory().get_interface(q.interface_type, *parse_query(q)).execute() for q in params.queries]
            return json.loads(json.dumps(results, default=str))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    ```

2. **Factory distributes to interfaces:**
    ```python
    class DataInterfaceFactory:
        def get_interface(self, type, query, proj, cond):
            interfaces = {"patient_info": FindPatientInfoInterface, "vitalsigns": FindVitalsignsInterface}
            return interfaces.get(type, lambda *args: ValueError("Unknown type"))(query, proj, cond)
    ```

3. **Interfaces query and get data from the database:**
    ```python
    class FindVitalsignsInterface(DataInterface):
        def execute(self):
            patient = self.patientFullName_collection.find_one({"fullName": self.query["patientName"]})
            if not patient: return []
            query = {"patient": patient["patient"]}
            if "duration" in self.conditions:
                query["createdDate"] = {"$gte": datetime.now() - timedelta(days=self.conditions["duration"]), "$lte": datetime.now()}
            cursor = self.vitalsigns_collection.find(query, self.projection)
            if "sortby" in self.conditions: cursor = cursor.sort([(k, -1 if v == "desc" else 1) for k, v in self.conditions["sortby"].items()])
            if "limit" in self.conditions: cursor = cursor.limit(self.conditions["limit"])
            return list(cursor)
    ```


Feel free to modify and enhance this README file according to your project needs.
