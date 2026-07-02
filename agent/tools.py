from langchain_core.tools import tool
from services.search import google_search

from services.weather import (
    get_weather,
    get_weather_alert,
    get_weather_report,
    normalize_location,
)

from services.maps import search_nearby

@tool
def google_search_tool(query: str) -> str:
    """
    使用 Gemini 內建 Google Search 查詢即時網路資訊。
    適合查詢最新新聞、餐廳推薦、景點、美食、店家資訊、近期事件。
    """
    print(f"[TOOL] google_search_tool 被呼叫，query={query}")
    return google_search(query)


@tool
def weather_tool(location: str) -> str:
    """
    查詢臺灣縣市的一般天氣資訊。
    location 必須是臺灣縣市名稱，例如：臺中市、臺南市、高雄市。
    """
    location = normalize_location(location)
    return get_weather(location)


@tool
def weather_alert_tool(location: str) -> str:
    """
    查詢臺灣縣市目前的天氣警特報。
    例如：大雨、豪雨、低溫、高溫、強風、颱風等。
    """
    location = normalize_location(location)
    return get_weather_alert(location)


@tool
def weather_report_tool(location: str) -> str:
    """
    同時查詢一般天氣與天氣警特報。
    適合回答天氣好不好、是否適合出門、是否要帶傘、穿搭建議等問題。
    """

    print(f"[TOOL] weather_report_tool 被呼叫，location={location}")
    location = normalize_location(location)
    return get_weather_report(location)


@tool
def map_search_tool(location: str, category: str, keyword: str = "") -> str:
    """
    搜尋指定地點附近的店家或設施。

    location 例如：朝陽科技大學、阿里山、臺南火車站。
    category 例如：咖啡廳、餐廳、停車場、醫院、ATM、加油站、景點。
    keyword 可選，例如：牛肉湯、拉麵、素食。
    """

    print(f"[TOOL] map_search_tool 被呼叫，location={location}, category={category}, keyword={keyword}")
    return search_nearby(
        location=location,
        category=category,
        keyword=keyword,
    )

def check_tool_result(state: AgentState):
    last_message = state["messages"][-1]
    retry_count = state.get("retry_count", 0)

    content = getattr(last_message, "content", "")

    if is_tool_failed(content) and retry_count < 2:
        retry_instruction = SystemMessage(
            content=(
                "剛才工具查詢失敗。請你自行判斷是否可能是地名錯字、簡稱、"
                "台/臺差異、地點過於模糊或類別不精確。"
                "請修正查詢參數後，再重新呼叫工具一次。"
                "不要直接回答失敗。"
            )
        )

        return {
            "messages": [retry_instruction],
            "retry_count": retry_count + 1,
        }

    return {
        "retry_count": retry_count,
    }


TOOLS = [
    weather_tool,
    weather_alert_tool,
    weather_report_tool,
    map_search_tool,
    google_search_tool,
]