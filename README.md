# NIS LLM Data Interface

JuboAgent's data interface, implemented with FastAPI, is designed for processing JSON files exported from JuboAgent's LLM. It efficiently queries specific user-requested information from MongoDB, and returns.

## Quick Start

### 1. Endpoint 端點

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

### 2. 資料處理順序

1. **Endpoint 拿到資料:**
    ```python
    @router.post("/initial-layer")
    async def execute_queries(my_params: RequestParams):
        results = []
        try:
            for query in my_params.queries:  # 可能多個 query ，一個個處理
                query_dict, projection, conditions = parse_query(query)
                interface = DataInterfaceFactory().get_interface(
                    query.interface_type, query_dict, projection, conditions
                )  # 分類參數，送到 factory
                results.extend(interface.execute())
            return json.loads(json.dumps(results, default=str))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    ```

2. **Factory 分配應該去哪個 interface:**
    ```python
    class DataInterfaceFactory:
        def get_interface(self, interface_type: str, query: Dict, projection: Dict = None, conditions: Optional[Dict] = None):
            if interface_type == "patient_info":  # 直接比對 interface_type
                return FindPatientInfoInterface(query, projection)
            elif interface_type == "vitalsigns":  # 直接比對 interface_type
                return FindVitalsignsInterface(query, projection, conditions)
            else:
                raise ValueError(f"Unknown interface type: {interface_type}")
    ```

3. **Interface 到資料庫索取對應資料:**
    ```python
    class FindVitalsignsInterface(DataInterface):
        def execute(self):  # interface 內部找尋資料過程
            patient = self.patientFullName_collection.find_one({"fullName": self.query["patientName"]})
            if not patient:
                return []
            query = {"patient": patient["patient"]}  # 獲取 patient_id

            if self.conditions and self.conditions.get("duration"):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=int(self.conditions["duration"]))
                query["createdDate"] = {"$gte": start_date, "$lte": end_date}  # 獲取日期範圍

            cursor = self.vitalsigns_collection.find(query, self.projection)
            if self.conditions and self.conditions.get("sortby"):
                sort_fields = [(k, -1 if v.lower() == "descending" else 1) for k, v in self.conditions["sortby"].items()]
                cursor = cursor.sort(sort_fields)
            if self.conditions and self.conditions.get("limit"):
                cursor = cursor.limit(int(self.conditions["limit"]))  # 處理限定條件

            return [doc for doc in cursor if all(f in doc for f in self.projection.keys() if self.projection[f] == 1)]  # 回傳結果
    ```



## 以上為 JuboAgent data interface 初版設計概念，未完待續～～

## 未來規劃

### 1. Using Auth0 for User Management with RBAC

Leveraging Auth0 as the primary user management solution, integrating Role-Based Access Control (RBAC) for enhanced security and user permissions management.

#### Key Features:

- **Authentication**: Users can securely log in using Auth0 credentials.
- **Authorization**: RBAC ensures that users have appropriate access based on predefined roles.(Admin, Organization, Patient, Guest)
- **User Management**: Administrators can manage user accounts and roles through the Auth0 dashboard.
- **Secure APIs**: Integration with Auth0 ensures secure access to application APIs.

### 2. Retrieving Data from Database with Source Website Links

In addition to retrieving data from the database, this project also includes relevant website links that serve as the sources of the retrieved data.

#### Implementation Details:

- **Data Retrieval**: When querying data from the database, the application fetches associated website links.
- **Presentation**: Retrieved data and links are presented together in the application’s user interface or API responses.
- **User Benefits**: Users can access the source websites for verification or additional context related to the retrieved data.

 

