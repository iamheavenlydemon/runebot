# import requests
# import json

# API_URL = "https://swarfarm.com/api/v2/monsters/?page={}"

# def build_id_name_map():
#     mapping = {}
#     page = 1
#     while True:
#         resp = requests.get(API_URL.format(page))
#         resp.raise_for_status()
#         data = resp.json()

#         for monster in data.get('results', []):
#             com2us_id = monster.get('com2us_id')
#             name = monster.get('name')
#             if com2us_id and name:
#                 mapping[str(com2us_id)] = name

#         # stop when no next page
#         if not data.get('next'):
#             break
#         page += 1

#     return mapping

# if __name__ == "__main__":
#     monster_map = build_id_name_map()
#     with open("monster_id_name_map.json", "w", encoding="utf-8") as f:
#         json.dump(monster_map, f, ensure_ascii=False, indent=2)

#     print(f"Saved {len(monster_map)} monsters to monster_id_name_map.json")



import requests
import json

API_URL = "https://swarfarm.com/api/v2/monsters/?page={}"

def build_id_name_element_map():
    mapping = {}
    page = 1

    while True:
        print(f"Fetching page {page}...")
        resp = requests.get(API_URL.format(page))
        resp.raise_for_status()
        data = resp.json()

        for monster in data.get("results", []):
            com2us_id = monster.get("com2us_id")
            name = monster.get("name")
            element = monster.get("element")
            if com2us_id and name:
                mapping[str(com2us_id)] = {
                    "name": name,
                    "element": element
                }

        if not data.get("next"):
            break
        page += 1

    return mapping


if __name__ == "__main__":
    monster_map = build_id_name_element_map()
    with open("monster_id_name_element_map.json", "w", encoding="utf-8") as f:
        json.dump(monster_map, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(monster_map)} monsters to monster_id_name_element_map.json")
