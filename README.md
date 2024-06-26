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
    async def execute_queries(my_params: RequestParams):
        results = []
        try:
            for query in my_params.queries:
                query_dict, projection, conditions = parse_query(query)
                interface = DataInterfaceFactory().get_interface(query.interface_type, query_dict, projection, conditions)
                results.extend(interface.execute())
            return json.loads(json.dumps(results, default=str))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    ```

2. **Factory distributes to interfaces:**
    ```python
    class DataInterfaceFactory:
        def get_interface(self, interface_type: str, query: Dict, projection: Dict = None, conditions: Optional[Dict] = None):
            if interface_type == "patient_info":
                return FindPatientInfoInterface(query, projection)
            elif interface_type == "vitalsigns":
                return FindVitalsignsInterface(query, projection, conditions)
            else:
                raise ValueError(f"Unknown interface type: {interface_type}")
    ```

3. **Interfaces query and get data from the database:**
    ```python
    class FindVitalsignsInterface(DataInterface):
        def execute(self):
            patient = self.patientFullName_collection.find_one({"fullName": self.query["patientName"]})
            if not patient:
                return []
            query = {"patient": patient["patient"]}
            if self.conditions and self.conditions.get("duration"):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=int(self.conditions["duration"]))
                query["createdDate"] = {"$gte": start_date, "$lte": end_date}
            cursor = self.vitalsigns_collection.find(query, self.projection)
            if self.conditions and self.conditions.get("sortby"):
                sort_fields = [(k, -1 if v.lower() == "descending" else 1) for k, v in self.conditions["sortby"].items()]
                cursor = cursor.sort(sort_fields)
            if self.conditions and self.conditions.get("limit"):
                cursor = cursor.limit(int(self.conditions["limit"]))
            return [doc for doc in cursor if all(f in doc for f in self.projection.keys() if self.projection[f] == 1)]
    ```


Feel free to modify and enhance this README file according to your project needs.
