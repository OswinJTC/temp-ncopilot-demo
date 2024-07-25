# Role-Based Access Control (RBAC) Implementation

Data Interface 抓取資料時，必須確認使用者的身份和權限。否則我們的系統將失去隱私性和其價值，因為任何人都能隨意獲取想要的特定資料。為此，我們利用 Auth0 來輔助實現 RBAC。當使用者登入並嘗試查詢特定資料（如病患個資）時，我們將確認他是否具備相應的權限。

這個權限檢查的動作會在各個 interface 的 execute 函數中執行。根據每個接口的初始定義不同，會有相應的權限檢查標準。

## 1. check_organization_permission

我們使用 check_organization_permission 函式，驗證使用者是否用有權限的機構。

```python
def check_organization_permission(token_data: TokenData, patient_organization_str: str):
    
    if not token_data or not token_data.app_metadata:
        raise HTTPException(status_code=403, detail="你沒有 metadata")

    user_organization = token_data.app_metadata.get('organization')
    if not user_organization or user_organization != patient_organization_str:
        raise HTTPException(status_code=403, detail="掰掰: 機構錯誤")
     
    logging.info(f"給過 機構存取～: {user_organization}")
```

    
## 2. check_organization_permission

我們使用 check_patient_id_permission 函式，驗證使用者是否是病患的家屬。

```python
def check_patient_id_permission(token_data: TokenData, patient_id_str: str):
    if not token_data or not token_data.app_metadata:
        raise HTTPException(status_code=403, detail="你沒有 metadata")

    user_patient_id = token_data.app_metadata.get('patient_id')
    if not user_patient_id or user_patient_id != patient_id_str:
        raise HTTPException(status_code=403, detail="掰掰: 並非家屬")

    logging.info(f"給過 家屬存取～: {user_patient_id}")
```
