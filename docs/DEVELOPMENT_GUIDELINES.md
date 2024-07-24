## 專案概述
歡迎參與本專案的開發！為了確保開發流程的順暢，請遵循以下指引和步驟。

在開始之前，請確保您了解專案的基本內容和目標: [專案內容](https://gitlab.smart-aging.tech/ds/infrastructure/jubo-nis-llm-data-interface/-/blob/add-official-auth/README.md)

  
## 開發指引

現在系統大概的模型出來了。往後的發展會建立在
<br>
(1) interface 的廣泛拓展
<br>
(2) 確保 LLM 的 prompts 跟 tools 是夠好的

<br>

已經有 vitalsigns 跟 patient_info 兩個 interfaces 。
現在就假設我們想新增一個全新的 interface 叫做 "fall_events"。用來查詢患者的跌倒紀錄 ⋯⋯

<br>

1. **一句人話進來@app.post("/main-processing") （不需任何動作👍👍👍）** 

<br>


2. **到 classify_query 加一個新的 interface type （現在設計就是先這樣）**
     
    ```python
    def classify_query(query):
    if any(keyword in query for keyword in ["血壓", "脈搏", "體溫", "血氧"]):
        return "vitalsigns"
    elif any(keyword in query for keyword in ["生日", "身高", "體重","醫院","血型"]):
        return "patients_info"
    else:
        return "default"
    ```
    
    所以我們將加上這個

    ```python
    elif any(keyword in query for keyword in ["跌倒","跌倒原因"]):
        return "fall_events"
    ```

<br>

3. **到 Postgres 的 llm_base_prompts 跟 llm_tools 加入此 usecase 自己的 prompts & tools**


llm_base_prompt
```
以下是可以使用的工具選項schema規定:
{tools}
###
question: {user_input}

output的結果請遵守下面規則，如果沒有符合的工具請output none：
- 將可以解決問題的工具選項輸出成名稱以及參數的json格式
- 從question之中取得定義的參數填入json之中
- 只能使用定義的參數，不可以自行增加
- 只寫json的部分，不要有多餘的描述
- 按照schema輸出json格式
- 將使用者的請求解析為全名（fullName）、需要檢索的欄位（retrieve）、以及條件（conditions）
- 只做我叫你做的事情
- 跌倒：fall

OUTPUT: json
```

llm_tools
```json
 {
    "interface_type": "fall_events",
    "patientName": "名字",
    "retrieve": ["所需關鍵字"],
    "conditions": {
        "duration": "持續時間（天）",
        "limit": "限制數量"
    }
}
```

<br>

4. **到 factory.py 新增一個新的 interface**

```python
    def get_interface(self, interface_type: str, query: Dict, projection: Dict = None, conditions: Optional[Dict] = None, token_data: TokenData = None) -> BaseInterface:
        if interface_type == "patients_info":
            return FindPatientInfoInterface(query, projection, conditions, token_data)
        elif interface_type == "vitalsigns":
            return FindVitalsignsInterface(query, projection, conditions, token_data)
        else:
            raise ValueError(f"Unknown interface type: {interface_type}")
```
    
所以我們將加上這個

```python
    elif interface_type == "fall_events":
            return FindFall_eventsInterface(query, projection, conditions, token_data)
```
     
<br>

5. **開一個新的 interface**

```python
    class FindPatientInfoInterface(BaseInterface):
    def __init__(self, query, projection, conditions=None, token_data: TokenData = None):
        self.query = query
        self.projection = projection
        self.conditions = conditions
        self.token_data = token_data
        self.fallevents_collection = get_mongo_collections()["fallevents"]
        self.db_connector = get_db_connector()

    def execute(self):
    ......#下面自行定義
```

<br>

6. **記得在 interface 裡設定專屬的 RBAC**

    ```python
    try:
        check_organization_permission(self.token_data, patient_organization_str)
    except HTTPException as e:
        if e.status_code == 403:
            try:
                check_patient_id_permission(self.token_data, patient_id_str)
            except HTTPException as e:
                if e.status_code == 403:
                    raise HTTPException(status_code=403, detail="Access denied")
                else:
                    logging.error(f"Unexpected error: {e.status_code}")
        else:
            logging.error(f"Unexpected error: {e.status_code}")
    ```
<br>

7. **最後到 Postgres 的 llm_base_prompts_2 跟 llm_tools_2 加入此 usecase 自己的 prompts & tools**

同 3

<br>

## 常見問題

如果在開發過程中遇到問題，請參考以下資源：
- [專案文檔](https://gitlab.com/username/repository/-/wikis/home)
- [技術支援](mailto:support@example.com)
- [常見問題解答](https://gitlab.com/username/repository/-/issues)

## 貢獻者

感謝以下貢獻者：
- 貢獻者 1
- 貢獻者 2
- 貢獻者 3

如有任何問題或建議，請隨時聯繫我們。謝謝您的貢獻！
