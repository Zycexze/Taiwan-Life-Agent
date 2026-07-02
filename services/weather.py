import requests
import urllib3
from config import WEATHER_API_KEY
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

params = {
    "Authorization": WEATHER_API_KEY,
}


CWA_BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"


CITY_MAP = {
    "台北": "臺北市",
    "臺北": "臺北市",
    "台北市": "臺北市",
    "臺北市": "臺北市",
    "新北": "新北市",
    "新北市": "新北市",
    "桃園": "桃園市",
    "桃園市": "桃園市",
    "台中": "臺中市",
    "臺中": "臺中市",
    "台中市": "臺中市",
    "臺中市": "臺中市",
    "台南": "臺南市",
    "臺南": "臺南市",
    "台南市": "臺南市",
    "臺南市": "臺南市",
    "高雄": "高雄市",
    "高雄市": "高雄市",
    "基隆": "基隆市",
    "基隆市": "基隆市",
    "新竹": "新竹市",
    "新竹市": "新竹市",
    "新竹縣": "新竹縣",
    "苗栗": "苗栗縣",
    "苗栗縣": "苗栗縣",
    "彰化": "彰化縣",
    "彰化縣": "彰化縣",
    "南投": "南投縣",
    "南投縣": "南投縣",
    "雲林": "雲林縣",
    "雲林縣": "雲林縣",
    "嘉義": "嘉義市",
    "嘉義市": "嘉義市",
    "嘉義縣": "嘉義縣",
    "屏東": "屏東縣",
    "屏東縣": "屏東縣",
    "宜蘭": "宜蘭縣",
    "宜蘭縣": "宜蘭縣",
    "花蓮": "花蓮縣",
    "花蓮縣": "花蓮縣",
    "台東": "臺東縣",
    "臺東": "臺東縣",
    "台東縣": "臺東縣",
    "臺東縣": "臺東縣",
    "澎湖": "澎湖縣",
    "澎湖縣": "澎湖縣",
    "金門": "金門縣",
    "金門縣": "金門縣",
    "連江": "連江縣",
    "連江縣": "連江縣",
    "馬祖": "連江縣",
}


def normalize_location(location: str) -> str:
    """將使用者輸入的地名轉成中央氣象署 API 使用的縣市名稱。"""
    if not location:
        return ""

    location = location.strip()
    location = location.replace("台", "臺")

    if location in CITY_MAP:
        return CITY_MAP[location]

    if not location.endswith(("市", "縣")):
        if location in CITY_MAP:
            return CITY_MAP[location]

    return location


def cwa_get(dataset_id: str, params: dict | None = None) -> dict:
    """呼叫中央氣象署 Open Data API。"""
    url = f"{CWA_BASE_URL}/{dataset_id}"

    if params is None:
        params = {}

    params["Authorization"] = WEATHER_API_KEY

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {
            "error": f"API 連線失敗：{e}"
        }

    except ValueError:
        return {
            "error": "API 回傳格式錯誤，無法解析 JSON。"
        }


def get_weather(location: str) -> str:
    """查詢一般天氣預報。"""
    location = normalize_location(location)

    data = cwa_get(
        "F-C0032-001",
        {
            "locationName": location
        }
    )

    if "error" in data:
        return data["error"]

    try:
        locations = data["records"]["location"]

        if len(locations) == 0:
            return f"找不到「{location}」的天氣資料，請確認是否為臺灣縣市名稱。"

        location_data = locations[0]
        weather = location_data["weatherElement"]

        wx = weather[0]["time"][0]["parameter"]["parameterName"]
        pop = weather[1]["time"][0]["parameter"]["parameterName"]
        min_t = weather[2]["time"][0]["parameter"]["parameterName"]
        comfort = weather[3]["time"][0]["parameter"]["parameterName"]
        max_t = weather[4]["time"][0]["parameter"]["parameterName"]

        return f"""地區：{location}
天氣：{wx}
降雨機率：{pop}%
氣溫：{min_t}～{max_t}°C
舒適度：{comfort}"""

    except Exception as e:
        return f"天氣資料解析失敗：{e}"


def get_weather_alert(location: str) -> str:
    """查詢天氣警特報。"""
    location = normalize_location(location)

    data = cwa_get("W-C0033-001")

    if "error" in data:
        return data["error"]

    try:
        records = data.get("records", {})
        dataset = records.get("record", [])

        if not dataset:
            return f"{location} 目前沒有查詢到天氣警特報。"

        matched_alerts = []

        for item in dataset:
            alert_title = item.get("datasetInfo", {}).get("datasetDescription", "天氣警特報")
            contents = item.get("contents", {})

            content_list = contents.get("content", [])

            if isinstance(content_list, dict):
                content_list = [content_list]

            for content in content_list:
                text = str(content)

                if location in text:
                    matched_alerts.append(alert_title)

        if not matched_alerts:
            return f"{location} 目前沒有明顯天氣警特報。"

        alert_text = "\n".join(f"- {alert}" for alert in set(matched_alerts))

        return f"""地區：{location}
目前查詢到以下天氣警特報：
{alert_text}"""

    except Exception as e:
        return f"警特報資料解析失敗：{e}"


def get_weather_report(location: str) -> str:
    """整合一般天氣與警特報，給生活建議用。"""
    location = normalize_location(location)

    weather = get_weather(location)
    alert = get_weather_alert(location)

    return f"""【一般天氣】
{weather}

【天氣警特報】
{alert}

請根據以上資料，判斷是否適合出門、是否需要帶傘，以及需要注意的安全事項。"""