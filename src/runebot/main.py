import mss
from PIL import Image, ImageDraw
import pygetwindow as gw
import pytesseract
import re
import sqlite3

DB_PATH = "monsterbox.db"

# 1. Get the game window
windows = gw.getWindowsWithTitle("Summoners War (Steam)")
if not windows:
    raise RuntimeError("Summoners War window not found")
win = windows[0]

# 2. Define rune capture relative to window
# Example offsets (adjust according to rune area in your window)

bbox = {
    'top': win.top + 40,
    'left': win.left + 850,
    'width': 420,
    'height': 275
}

rune_grade = {
    'top': win.top + 80,
    'left': win.left + 1180,
    'width': 100,
    'height': 35
}

title_bbox = {
    'top': win.top + 45,     # same offset_top as main
    'left': win.left + 920,  # same offset_left
    'width': 295,            # cropped width of title
    'height': 40             # cropped height of title
}

mainstat_bbox = {
    'top': win.top + 90,     # shifted down from top
    'left': win.left + 930,  # slightly inside left boundary
    'width': 180,            # cropped width for stat text
    'height': 70             # cropped height for stat block
}


substats_bbox = {
    'top': win.top + 160,    # below main stat
    'left': win.left + 840,  # aligned with left text
    'width': 220,            # cropped width for subs
    'height': 120             # cropped height for 3 lines
}

def normalize_rune_name(rune_text: str) -> str:
    # Collapse multiple spaces and strip
    clean = re.sub(r"\s+", " ", rune_text.strip())
    parts = clean.split(" ")
    
    # Ensure at least "X Rune"
    if len(parts) >= 2 and parts[-1].lower() == "rune":
        print(parts)
        return f"{parts[-2]}" #what is going on here
    return clean[0]  # fallback


# 3. Capture with mss
with mss.mss() as sct:
    rune_grade_ss = sct.grab(rune_grade)
    rune_grade_img = Image.frombytes('RGB', rune_grade_ss.size, rune_grade_ss.rgb)
    rune_grade_img.save("rune_grade_img.png")
    rune_grade_text = pytesseract.image_to_string(rune_grade_img)
    rune_grade_lines = [re.sub(r"\s+", " ", line.strip()) for line in rune_grade_text.split("\n") if line.strip()]
    # print(rune_grade_lines[0])

    title_ss = sct.grab(title_bbox)
    title_ss_img = Image.frombytes('RGB', title_ss.size, title_ss.rgb)
    title_ss_img.save("title_ss_img.png")
    title_ss_text = pytesseract.image_to_string(title_ss_img)
    title_ss_lines = [re.sub(r"\s+", " ", line.strip()) for line in title_ss_text.split("\n") if line.strip()]
    match = re.match(r"(.+?)\s*\((\d+)\)", title_ss_lines[0])
    if match:
        rune_name = normalize_rune_name(match.group(1))   # "Revenge Rune"
        slot = int(match.group(2))   # 3
        # print(rune_name)
        # print(slot)
   


    main_stat_ss = sct.grab(mainstat_bbox)
    main_stat_img = Image.frombytes('RGB', main_stat_ss.size, main_stat_ss.rgb)
    main_stat_img.save("main_stat_img.png")
    main_stat_text = pytesseract.image_to_string(main_stat_img)
    main_stat_lines = [re.sub(r"\s+", " ", line.strip()) for line in main_stat_text.split("\n") if line.strip()]
    main_stats = []
    pattern = re.compile(r"(.+?)\s*\+(\d+)(%?)")   # captures stat, number, optional %

    for line in main_stat_lines:
        match = pattern.match(line)
        if match:
            stat_name = match.group(1).strip()
            value = int(match.group(2))
            is_percent = match.group(3) == "%"

            if is_percent:
                stat_name = f"{stat_name}%"
            
            main_stats.append({
                "stat_name": stat_name,
                "amount_increase": value,
                "is_percent": is_percent
            })
    # print(main_stats)

    sub_stats_ss = sct.grab(substats_bbox)
    sub_stats_img = Image.frombytes('RGB', sub_stats_ss.size, sub_stats_ss.rgb)
    sub_stats_img.save("sub_stats_img.png")
    sub_stats_text = pytesseract.image_to_string(sub_stats_img)
    sub_stats_lines = [re.sub(r"\s+", " ", line.strip()) for line in sub_stats_text.split("\n") if line.strip()]
    sub_stats = {}
    pattern = re.compile(r"(.+?)\s*\+(\d+)(%?)")   # captures stat, number, optional %

    for line in sub_stats_lines:
        match = pattern.match(line)
        if match:
            stat_name = match.group(1).strip()
            value = int(match.group(2))
            is_percent = match.group(3) == "%"

            if is_percent:
                stat_name = f"{stat_name}%"

            sub_stats[stat_name] = value
    # print(sub_stats)


#################
#################

MAX_ROLLS = {
    "HP%": 8,
    "ATK%": 8,
    "DEF%": 8,
    "SPD": 6,
    "CRI Rate%": 6,
    "CRI Dmg%": 7,
    "RES%": 8,
    "Accuracy%": 8,
    "HP": 375,
    "ATK": 20,
    "DEF": 20,
}


SET_MAIN_STATS = {
    "Guard": {
        1: {"HP", "DEF"},
        2: {"HP%", "DEF%"},
        3: {"HP", "DEF"},
        4: {"HP%", "DEF%", "RES%"},
        5: {"HP", "DEF"},
        6: {"HP%", "DEF%", "ACC%", "RES%"}
    },
    "Swift": {
        1: {"HP", "ATK", "DEF"},
        2: {"SPD"},
        3: {"HP", "ATK", "DEF"},
        4: {"CRIT RATE%", "CRIT DMG%", "ATK%"},
        5: {"HP", "ATK", "DEF"},
        6: {"HP%", "DEF%", "ATK%"}
    },
    "Violent": {
        1: {"HP", "ATK", "DEF"},
        2: {"SPD", "HP%", "ATK%"},
        3: {"HP", "ATK", "DEF"},
        4: {"CRIT RATE%", "CRIT DMG%", "ATK%", "HP%"},
        5: {"HP", "ATK", "DEF"},
        6: {"HP%", "DEF%", "ATK%"}
    },
    "Despair": {
        1: {"HP", "ATK", "DEF"},
        2: {"SPD", "HP%", "ATK%"},
        3: {"HP", "ATK", "DEF"},
        4: {"CRIT RATE%", "CRIT DMG%", "ATK%"},
        5: {"HP", "ATK", "DEF"},
        6: {"HP%", "DEF%", "ATK%", "ACC%"}
    },
    "Vampire": {
        1: {"HP", "ATK", "DEF"},
        2: {"SPD", "HP%", "ATK%"},
        3: {"HP", "ATK", "DEF"},
        4: {"CRIT RATE%", "CRIT DMG%", "ATK%", "HP%"},
        5: {"HP", "ATK", "DEF"},
        6: {"HP%", "DEF%", "ATK%"}
    },
    "Fatal": {
        1: {"ATK"},
        2: {"ATK%"},
        3: {"ATK"},
        4: {"CRIT RATE%", "CRIT DMG%", "ATK%"},
        5: {"ATK"},
        6: {"ATK%"}
    },
    "Energy": {
        1: {"HP"},
        2: {"HP%"},
        3: {"HP"},
        4: {"HP%", "DEF%", "RES%"},
        5: {"HP"},
        6: {"HP%", "DEF%"}
    },
    "Blade": {
        1: {"ATK"},
        2: {"SPD", "ATK%"},
        3: {"ATK"},
        4: {"CRIT RATE%", "CRIT DMG%", "ATK%"},
        5: {"ATK"},
        6: {"ATK%", "HP%"}
    },
    "Rage": {
        1: {"ATK"},
        2: {"ATK%"},
        3: {"ATK"},
        4: {"CRIT RATE%", "CRIT DMG%", "ATK%"},
        5: {"ATK"},
        6: {"CRIT DMG%"}
    },
    "Will": {
        1: {"HP", "DEF"},
        2: {"HP%", "DEF%"},
        3: {"HP", "DEF"},
        4: {"HP%", "DEF%", "RES%"},
        5: {"HP", "DEF"},
        6: {"HP%", "DEF%", "RES%"}
    },
    "Nemesis": {
        1: {"HP", "ATK", "DEF"},
        2: {"SPD"},
        3: {"HP", "ATK", "DEF"},
        4: {"HP%", "DEF%", "ATK%"},
        5: {"HP", "ATK", "DEF"},
        6: {"SPD"}
    },
    "Endure": {
        1: {"HP", "DEF"},
        2: {"HP%", "DEF%"},
        3: {"HP", "DEF"},
        4: {"HP%", "DEF%", "RES%"},
        5: {"HP", "DEF"},
        6: {"HP%", "DEF%"}
    },
    "Shield": {
        1: {"HP", "DEF"},
        2: {"HP%", "DEF%"},
        3: {"HP", "DEF"},
        4: {"HP%", "DEF%", "RES%"},
        5: {"HP", "DEF"},
        6: {"HP%", "DEF%"}
    },
    "Destroy": {
        1: {"ATK"},
        2: {"ATK%"},
        3: {"ATK"},
        4: {"CRIT RATE%", "CRIT DMG%", "ATK%"},
        5: {"ATK"},
        6: {"CRIT DMG%"}
    },
    "Fight": {
        1: {"ATK"},
        2: {"ATK%"},
        3: {"ATK"},
        4: {"CRIT RATE%", "CRIT DMG%", "ATK%"},
        5: {"ATK"},
        6: {"ATK%"}
    },
    "Determination": {
        1: {"HP"},
        2: {"HP%"},
        3: {"HP"},
        4: {"HP%", "DEF%", "ATK%"},
        5: {"HP"},
        6: {"ATK%"}
    },
    "Revenge": {
        1: {"HP", "ATK", "DEF"},
        2: {"SPD", "HP%", "ATK%"},
        3: {"HP", "ATK", "DEF"},
        4: {"CRIT RATE%", "CRIT DMG%", "ATK%", "HP%"},
        5: {"HP", "ATK", "DEF"},
        6: {"HP%", "DEF%", "ATK%"}
    },
    "Revenge": {
        1: {"HP", "ATK", "DEF"},
        2: {"SPD", "HP%", "ATK%"},
        3: {"HP", "ATK", "DEF"},
        4: {"CRIT RATE%", "CRIT DMG%", "ATK%", "HP%"},
        5: {"HP", "ATK", "DEF"},
        6: {"HP%", "DEF%", "ATK%"}
    },
    "Will": {
        1: {"HP", "DEF"},
        2: {"HP%", "DEF%"},
        3: {"HP", "DEF"},
        4: {"HP%", "DEF%", "RES%"},
        5: {"HP", "DEF"},
        6: {"HP%", "DEF%", "RES%"}
    },
    "Rage": {
        1: {"ATK"},
        2: {"ATK%"},
        3: {"ATK"},
        4: {"CRIT RATE%", "CRIT DMG%", "ATK%"},
        5: {"ATK"},
        6: {"CRIT DMG%"}
    }
    # You can add more sets if needed: Rage, Will, Nemesis, Endure, Shield, etc.
}

GOOD_SUBS = {
    "SPD", "CRIT RATE%", "CRIT DMG%",
    "ATK%", "HP%", "DEF%",
    "RES%", "ACC%"
}

BAD_SUBS = {
    "ATK", "HP", "DEF"  # flat stats
}

def calc_efficiency(substats):
    """
    substats = dict { "SPD": 5, "CRIT RATE%": 4, ... }
    Returns efficiency %, e.g. 75.3
    """
    total = 0
    max_total = 0
    for stat, val in substats.items():
        # print(f"Looking at {stat}")
        if stat not in MAX_ROLLS:
            print(f"{stat} with value {val} not in max rolls")
            continue
        max_val = MAX_ROLLS[stat]
        total += val
        # print(f"Adding to total: {total}")
        max_total += max_val
        # print(f"Adding to max_total: {max_total}")
    if max_total == 0:
        return 0
    return round((total / max_total) * 100, 1)


def should_keep_rune(rune_set, slot, main_stat, substats, min_eff=60):
    """
    rune_set: e.g. "Violent"
    slot: int (1–6)
    main_stat: str (e.g. "HP%", "CRIT DMG%")
    substats: dict { "SPD": 5, "CRIT RATE%": 6 }
    min_eff: efficiency threshold (default 60%)
    """
    print("--in check--")
    # Step 1: Check main stat validity
    set_prefs = SET_MAIN_STATS.get(rune_set, {})
    good_mains = set_prefs.get(slot, set())

    if good_mains and main_stat not in good_mains:
        return False

    # Step 2: Check sub stat validity
    good_substats_total = 0
    for stat in substats:
        if stat in SET_MAIN_STATS[rune_set][slot]:
            good_substats_total += 1

    print(f"Total good substat: {good_substats_total}")

    # Step 3: Calculate efficiency
    eff = calc_efficiency(substats)
    substats_threshold = good_substats_total/len(substats)
    print(f"Efficiency: {eff}")
    print(f"Substat threshold: {substats_threshold}")

    # Step 4: Compare against threshold
    return (eff >= min_eff) and (substats_threshold>0.5)


def get_candidate_monsters(rune_set_id, rune_slot, limit=5):
    """
    Return a list of monsters to consider for a given rune, filtered by priority
    and preferred rune sets.
    
    :param rune_set_id: int, the set ID of the rune
    :param rune_slot: int, slot number 1-6
    :param limit: int, max number of monsters to return
    :return: list of dicts with monster info
    """

    #TODO: add in p.slot so we can also filter for specfic rune slot requirements on monsters

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us fetch results as dicts
    cur = conn.cursor()

    query = """
    SELECT *
    FROM monsters m
    WHERE EXISTS (
        SELECT 1
        FROM monster_preferred_sets p
        WHERE p.monster_id = m.id
          AND p.rune_set_id = ?
    )
    ORDER BY m.priority_id ASC  -- smaller number = higher priority
    LIMIT ?
    """
    
    cur.execute(query, (rune_set_id, limit))
    results = cur.fetchall()
    conn.close()

    # Convert sqlite3.Row objects to dicts
    return [dict(row) for row in results]




# result = should_keep_rune(rune_name, slot, main_stats[0]["stat_name"], sub_stats)
# print(result)

# Example usage:
candidates = get_candidate_monsters(rune_set_id=17, rune_slot=2, limit=5)
print(candidates)
for c in candidates:
    print(c["name"], c["priority_id"])
