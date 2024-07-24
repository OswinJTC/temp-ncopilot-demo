 # NIS LLM Data Interface

JuboAgent 的後端, 使用 Python FastAPI 框架. 其運作順序如下： LLM 根據 NL 生成一個 JSON 查詢格式 -> Data Interface 根據該 JSON 到資料庫拿資料 -> LLM 將得到的資料翻譯回自然語言。

基於這個設計理念，後續的開發可以按照 docs 裡 md 的步驟進行～

## Quick Start （共三個步驟）
