import math
import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

HEADERS = {
    "User-Agent": "taiwan-ai-agent/1.0"
}


CATEGORY_MAP = {
    "餐廳": {"key": "amenity", "value": "restaurant"},
    "咖啡廳": {"key": "amenity", "value": "cafe"},
    "咖啡店": {"key": "amenity", "value": "cafe"},
    "停車場": {"key": "amenity", "value": "parking"},
    "醫院": {"key": "amenity", "value": "hospital"},
    "診所": {"key": "amenity", "value": "clinic"},
    "便利商店": {"key": "shop", "value": "convenience"},
    "超商": {"key": "shop", "value": "convenience"},
    "ATM": {"key": "amenity", "value": "atm"},
    "atm": {"key": "amenity", "value": "atm"},
    "加油站": {"key": "amenity", "value": "fuel"},
    "景點": {"key": "tourism", "value": "attraction"},
    "飯店": {"key": "tourism", "value": "hotel"},
    "旅館": {"key": "tourism", "value": "hotel"},
}


def geocode(location: str) -> dict | None:
    """將地點名稱轉成經緯度。"""
    params = {
        "q": location,
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "tw",
    }

    try:
        response = requests.get(
            NOMINATIM_URL,
            params=params,
            headers=HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if not data:
            return None

        item = data[0]

        return {
            "name": item.get("display_name", location),
            "lat": float(item["lat"]),
            "lon": float(item["lon"]),
        }

    except Exception:
        return None


def haversine_distance(lat1, lon1, lat2, lon2) -> int:
    """計算兩個經緯度之間距離，單位：公尺。"""
    r = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return int(r * c)


def normalize_category(category: str) -> dict | None:
    """將中文類別轉成 OpenStreetMap tag。"""
    if not category:
        return None

    category = category.strip()

    if category in CATEGORY_MAP:
        return CATEGORY_MAP[category]

    for key in CATEGORY_MAP:
        if key in category:
            return CATEGORY_MAP[key]

    return None


def build_overpass_query(lat: float, lon: float, tag: dict, radius: int = 1500) -> str:
    """建立 Overpass 查詢語法。"""
    key = tag["key"]
    value = tag["value"]

    return f"""
    [out:json][timeout:25];
    (
      node["{key}"="{value}"](around:{radius},{lat},{lon});
      way["{key}"="{value}"](around:{radius},{lat},{lon});
      relation["{key}"="{value}"](around:{radius},{lat},{lon});
    );
    out center tags;
    """


def search_nearby(
    location: str,
    category: str,
    keyword: str = "",
    radius: int = 1500,
    limit: int = 5,
) -> str:
    """
    搜尋指定地點附近的店家或設施。

    location: 地點，例如 朝陽科技大學、阿里山、臺南火車站
    category: 類別，例如 咖啡廳、餐廳、停車場、醫院、ATM
    keyword: 關鍵字，例如 牛肉湯、拉麵、素食
    """
    place = geocode(location)

    if place is None:
        return f"找不到「{location}」的位置，請換一個更明確的地點名稱。"

    tag = normalize_category(category)

    if tag is None:
        return (
            f"目前不支援「{category}」這個類別。\n"
            f"可支援：餐廳、咖啡廳、停車場、醫院、診所、便利商店、ATM、加油站、景點、飯店。"
        )

    query = build_overpass_query(
        lat=place["lat"],
        lon=place["lon"],
        tag=tag,
        radius=radius,
    )

    try:
        response = requests.post(
            OVERPASS_URL,
            data={"data": query},
            headers=HEADERS,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

    except Exception as e:
        return f"OpenStreetMap 查詢失敗：{e}"

    elements = data.get("elements", [])

    results = []

    for item in elements:
        tags = item.get("tags", {})
        name = tags.get("name") or tags.get("name:zh") or tags.get("name:en")

        if not name:
            continue

        if keyword and keyword not in name:
            continue

        item_lat = item.get("lat")
        item_lon = item.get("lon")

        if item_lat is None or item_lon is None:
            center = item.get("center", {})
            item_lat = center.get("lat")
            item_lon = center.get("lon")

        if item_lat is None or item_lon is None:
            continue

        distance = haversine_distance(
            place["lat"],
            place["lon"],
            float(item_lat),
            float(item_lon),
        )

        address_parts = [
            tags.get("addr:city"),
            tags.get("addr:district"),
            tags.get("addr:street"),
            tags.get("addr:housenumber"),
        ]

        address = "".join([part for part in address_parts if part]) or "未提供地址"

        results.append(
            {
                "name": name,
                "distance": distance,
                "address": address,
                "lat": float(item_lat),
                "lon": float(item_lon),
            }
        )

    results = sorted(results, key=lambda x: x["distance"])[:limit]

    if not results:
        return f"在「{location}」附近 {radius} 公尺內，找不到符合「{keyword or category}」的結果。"

    output = [
        f"搜尋地點：{location}",
        f"定位結果：{place['name']}",
        f"搜尋類別：{category}",
        f"搜尋半徑：{radius} 公尺",
        "",
        "找到以下結果：",
    ]

    for i, result in enumerate(results, start=1):
        maps_url = (
            f"https://www.openstreetmap.org/?mlat={result['lat']}"
            f"&mlon={result['lon']}#map=18/{result['lat']}/{result['lon']}"
        )

        output.append(
            f"{i}. {result['name']}\n"
            f"距離：約 {result['distance']} 公尺\n"
            f"地址：{result['address']}\n"
            f"地圖：{maps_url}"
        )

    return "\n\n".join(output)


if __name__ == "__main__":
    print(search_nearby("朝陽科技大學", "咖啡廳"))