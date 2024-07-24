### （一） LLM1 資料處理順序
### （二） Data Interface 資料處理順序

1. **Function 拿到資料:**
    ```python
    async def execute_query(my_params: RequestParams):
        results = []
        try:
            query_dict, projection, conditions = parse_query(query)
            interface = DataInterfaceFactory().get_interface(query["interface_type"], query_dict, projection, conditions, token_data)
            result = interface.execute()
            return json.loads(json.dumps(result, default=str))
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

### （三） LLM2 資料處理順序
