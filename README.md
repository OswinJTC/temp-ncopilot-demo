 # NIS LLM Data Interface

JuboAgent 的後端, 使用 Python FastAPI 框架. 其運作順序如下： LLM 根據 NL 生成一個 JSON 查詢格式 -> Data Interface 根據該 JSON 到資料庫拿資料 -> LLM 將得到的資料翻譯回自然語言。

基於這個設計理念，後續的開發可以按照 docs 裡 md 的步驟進行～

## Quick Start （共三個步驟）


### 1. 第一個 LLM （一段話 -> JSON）

#### def `Service(...):`


- **參數 (str)**:
  
      "user_input": "幫我回傳憨斑斑三個月內前三高的血壓 (SYS) 。"

<br>

### 2. Data Interface 主函式 （JSON -> 抓到的資料）

#### def `execute_query(...):`
 

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
        }
      ]
    }
    ```

<br>

### 3. 第二個 LLM （抓到的資料 -> 一句話）

#### def `Service2(...):`

- **Request Body**: 
    ```json
    {
      "input_text": "幫我回傳憨斑斑三個月內前三高的血壓 (SYS) 。",
      "dboutput": {
        "DbOutput": [
          {
            "SYS": 120
          },
          {
            "SYS": 100.2
          },
          {
            "SYS": 93.4
          }
        ]
      }
    }
    ```

#### 最後輸出:
 
  
      "你好，憨斑斑三個月內前三高的血壓是 120, 100.2 和 93.4～謝謝！"
 
程式碼詳細描述請見 doc ～
##

 
<br>

#### 未來規劃

#### 1. DB version control
#### 2. LLM tuning
#### 3. Larger scaling

 
 
 
 

