import csv
import time
import http.client
import json




def split_json_objects(raw_text):
    import json

    decoder = json.JSONDecoder()
    pos = 0
    results = []

    while pos < len(raw_text):
        obj, index = decoder.raw_decode(raw_text, pos)
        results.append(obj)
        pos = index

    return results

def parse_openwebninja(raw_data):


    all_data = split_json_objects(raw_data)

    parsed = []

    for block in all_data:
        businesses = block.get("data", [])

        for b in businesses:
            parsed.append({
                "id": b.get("business_id"),
                "name": b.get("name"),
                "phone": b.get("phone_number"),
                "address": b.get("full_address") or b.get("address"),
                "city": b.get("city"),
                "state": b.get("state"),
                "country": b.get("country"),
                "lat": b.get("latitude"),
                "lng": b.get("longitude"),
                "rating": b.get("rating"),
                "reviews": b.get("review_count"),
                "type": b.get("type"),
                "subtypes": ", ".join(map(str, b.get("subtypes") or [])),
                "website": b.get("website"),
                "status": b.get("business_status"),
                "price_level": b.get("price_level"),

                # working hours (as a string)
                "working_hours": str(b.get("working_hours")),

                # Links
                "google_maps": b.get("place_link"),
                "reviews_link": b.get("reviews_link"),

                # Sample Photo
                "photo": (
                    b.get("photos_sample", [{}])[0].get("photo_url")
                    if b.get("photos_sample") else None
                ),

                # About
                "about": (
                    b.get("about", {}).get("summary")
                    if b.get("about") else None
                )
            })

    return parsed



def search_business(conn, query, location="Shiraz", limit=20):


    conn = http.client.HTTPSConnection("api.openwebninja.com")

    queries = [
        "لوازم یدکی خودرو شیراز",
        "نمایندگی فرش قطعات ایران خودرو",
        "نمایندگی فرش قطعات سایپا",
        "نمایندگی فروش قطعات یدکی خودروهای چینی",
    ]
    #language
    #region
    #coordinates
    #zoom
    payload = json.dumps({
        "queries": queries,
        "limit": 20,
        "language": "fa",
        "bottom_left": "29.563796,52.410282",
        "top_right": "29.698666,52.662450",
        "region": "IR",
        "dedup": True #Remove duplicates across queries
    })

    headers = {
        'Content-Type': "application/json",
        'x-api-key': "ak_klbxhdgy3ojicgeqnwanqyux87gjhhl4qtiez4l8y2f940z"
    }

    conn.request("POST", "/local-business-data/search", payload, headers)

    res = conn.getresponse()
    raw_data  = res.read().decode("utf-8")
    parsed_data = parse_openwebninja(raw_data)
    print(f"Parsed: {len(parsed_data)} businesses")
    for b in parsed_data[:3]:
        print(b)

    return parsed_data

def save_to_csv(data, filename="businesses_in_area.csv"):
    if not data:
        return

    keys = data[0].keys()

    with open(filename, "w", newline='', encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":

    conn = http.client.HTTPSConnection("api.openwebninja.com")

    query = "لوازم یدکی خودرو"
    location = "شیراز"

    print("Fetching data...")

    results = search_business(conn, query, location)

    print(f"Collected {len(results)} businesses")

    save_to_csv(results)

    print("Saved to CSV ✅")