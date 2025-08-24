import json
import sqlite3

# --- CONFIG ---
DB_PATH = "monsterbox.db"
JSON_PATH = "my_monsters.json"

# --- STAT ID mapping (must match stats table in schema) ---
STAT_MAP = {
    1: "HP flat",
    2: "HP%",
    3: "ATK flat",
    4: "ATK%",
    5: "DEF flat",
    6: "DEF%",
    8: "SPD",
    9: "CRI Rate",
    10: "CRI Dmg",
    11: "Resistance",
    12: "Accuracy"
}

def import_runes():
    # Load JSON
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    runes = data.get("runes", [])
    for rune in runes:
        rune_id = rune["rune_id"]

        # Insert into runes
        cur.execute("""
            INSERT OR REPLACE INTO runes (
                id, slot, set_id, rank, class, level, upgrade_limit,
                base_value, sell_value, equipped_to, innate_stat_id, innate_value
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rune_id,
            rune["slot_no"],
            rune["set_id"],
            rune.get("rank"),
            rune.get("class"),
            rune.get("upgrade_curr"),
            rune.get("upgrade_limit"),
            rune.get("base_value"),
            rune.get("sell_value"),
            rune.get("occupied_id") if rune.get("occupied_type") == 2 else None,
            rune["prefix_eff"][0] if rune.get("prefix_eff") and rune["prefix_eff"][0] > 0 else None,
            rune["prefix_eff"][1] if rune.get("prefix_eff") and rune["prefix_eff"][0] > 0 else None
        ))

        # Insert main stat
        pri_eff = rune.get("pri_eff", [])
        if pri_eff and pri_eff[0] in STAT_MAP:
            cur.execute("""
                INSERT OR REPLACE INTO rune_main_stats (rune_id, stat_id, value)
                VALUES (?, ?, ?)
            """, (
                rune_id,
                pri_eff[0],
                pri_eff[1]
            ))

        # Insert substats
        for sub in rune.get("sec_eff", []):
            stat_id, value, add_val, enchant = sub
            if stat_id in STAT_MAP:
                cur.execute("""
                    INSERT OR REPLACE INTO rune_substats
                    (rune_id, stat_id, value, grind_value, enchant)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    rune_id,
                    stat_id,
                    value,
                    add_val or 0,
                    enchant or 0
                ))

    conn.commit()
    conn.close()
    print(f"Imported {len(runes)} runes into database.")

if __name__ == "__main__":
    import_runes()
