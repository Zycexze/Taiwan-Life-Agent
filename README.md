# 🇹🇼 Taiwan Life Agent

An AI-powered personal assistant for Taiwan built with **LangGraph**, **Gemini**, and multiple external tools.

The agent can understand user requests, automatically choose the appropriate tools, and provide practical responses related to weather, travel, and local information.

> 🚧 This project is under active development.  
> Current version: **v1.0**

---

# Features

- 🌤️ Taiwan Weather Query (Central Weather Administration API)
- ⚠️ Weather Alerts
- 🗺️ Nearby Places Search (OpenStreetMap)
- 🔍 Google Search (Gemini Search)
- 🧠 Multi-turn Conversation Memory
- 🤖 Gemini Tool Calling
- 🔄 LangGraph StateGraph Workflow

---

# Demo

### Weather

```text
User:
今天臺中天氣如何？

Assistant:
臺中市今天晴時多雲，
氣溫 27~35°C，
降雨機率 10%。

目前沒有任何天氣警特報，
適合戶外活動，
建議注意防曬並補充水分。
```

---

### Travel Recommendation

```text
User:
我想去高美濕地玩

Assistant:
✔ 查詢臺中天氣
✔ 搜尋高美濕地旅遊資訊

今天適合前往高美濕地，
建議下午前往欣賞夕陽，
並注意海風較強。
```

---

### Nearby Search

```text
User:
朝陽科技大學附近有什麼餐廳？

Assistant:
• 采舍食堂
• ...
```

---

# Tech Stack

- Python
- LangGraph
- LangChain
- Google Gemini 2.5 Flash
- Google Search
- OpenStreetMap
- Taiwan CWA OpenData API
- python-dotenv

---

# Project Structure

```text
.
├── agent/
│   ├── graph.py
│   ├── memory.py
│   ├── prompts.py
│   └── tools.py
│
├── services/
│   ├── weather.py
│   ├── maps.py
│   └── search.py
│
├── config.py
├── main.py
├── requirements.txt
└── .env
```

---

# Installation

Clone this repository

```bash
git clone https://github.com/<your-name>/taiwan-life-agent.git

cd taiwan-life-agent
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create your `.env`

```env
gemini_key=YOUR_GEMINI_API_KEY
weather_key=YOUR_CWA_API_KEY
```

Run

```bash
python main.py
```

---

# Example

```text
AI：
你好，我是臺灣生活助理。

你：
今天臺中天氣如何？

AI：
...
```

---

# Current Workflow (v1.0)

```text
User
   │
   ▼
Gemini
   │
   ▼
Tool Calling
   │
   ├── Weather API
   ├── Google Search
   └── OpenStreetMap
   │
   ▼
Response
```

---

# Roadmap

## ✅ v1.0

- LangGraph StateGraph
- Gemini Tool Calling
- Taiwan Weather API
- Weather Alerts
- Google Search
- OpenStreetMap
- Conversation Memory

## 🚧 v2.0

- Planner Node
- Task Decomposition
- Multi-tool Execution
- Result Merge
- Travel Planning Agent

## 🚀 Future

- RAG
- Gmail Integration
- Google Calendar
- AQI
- Earthquake API
- Streamlit Web UI

---

# License

MIT License
