import json
import sqlite3

DB_PATH = "monsterbox.db"
JSON_PATH = "my_monsters.json"
MONSTER_DATA_PATH = "monster_id_name_element_map.json"  # your JSON mapping file

ELEMENTS = {
    1: "Water",
    2: "Fire",
    3: "Wind",
    4: "Light",
    5: "Dark"
}

def import_monsters():
    # Load raw monster list
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    monsters = data.get("unit_list", [])

    # Load readable names mapping
    with open(MONSTER_DATA_PATH, "r", encoding="utf-8") as f:
        monster_data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for m in monsters:
        # Get readable name from nested JSON, fallback to "Unknown"
        # readable_name = monster_data["monster"]["names"].get(str(m["unit_master_id"]), "Unknown")
        readable_name = monster_data[str(m["unit_master_id"])]["name"]

        cur.execute("""
            INSERT OR REPLACE INTO monsters (
                id, name, element, role, priority_id
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            m["unit_master_id"],           # original identifier
            readable_name,                 # readable name from JSON mapping
            ELEMENTS.get(m["attribute"], "Unknown"),
            None,                          # role (to be assigned later)
            2                              # default = medium priority
        ))

    conn.commit()
    conn.close()
    print(f"Imported {len(monsters)} monsters.")

if __name__ == "__main__":
    import_monsters()
