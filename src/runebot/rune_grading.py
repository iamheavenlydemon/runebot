# rune_filter.py
# Rune filtering with efficiency + grading + full stat breakdown

from typing import Dict, List, Tuple

# --- Rune sets ---
RUNE_SETS = {
    1: "Energy", 2: "Guard", 3: "Swift", 4: "Blade", 5: "Rage",
    6: "Focus", 7: "Endure", 8: "Fatal", 10: "Despair", 11: "Vampire",
    13: "Violent", 14: "Nemesis", 15: "Will", 16: "Shield",
    17: "Revenge", 18: "Destroy", 19: "Fight", 20: "Determination",
    21: "Enhance", 22: "Accuracy", 23: "Tolerance"
}

# --- Stat IDs ---
STAT_NAMES = {
    1: "HP flat", 2: "HP%", 3: "ATK flat", 4: "ATK%",
    5: "DEF flat", 6: "DEF%", 8: "SPD", 9: "CRate",
    10: "CDmg", 11: "RES", 12: "ACC",
}

# --- Max sub values ---
MAX_SUBSTAT_VALUES = {
    1: 1875,  # HP flat
    2: 8,     # HP%
    3: 100,   # ATK flat
    4: 8,     # ATK%
    5: 100,   # DEF flat
    6: 8,     # DEF%
    8: 6,     # SPD
    9: 6,     # CRate
    10: 7,    # CDmg
    11: 8,    # RES
    12: 8,    # ACC
}

# --- Useful stats per set ---
USEFUL_STATS = {
    "Energy": {"HP%", "DEF%", "SPD"},
    "Guard": {"DEF%", "HP%", "SPD"},
    "Swift": {"SPD", "HP%", "DEF%", "ATK%"},
    "Blade": {"CRate", "ATK%", "SPD"},
    "Rage": {"CDmg", "CRate", "ATK%", "SPD"},
    "Focus": {"ACC", "SPD", "HP%", "DEF%"},
    "Endure": {"RES", "HP%", "DEF%", "SPD"},
    "Fatal": {"ATK%", "CRate", "SPD"},
    "Despair": {"ACC", "SPD", "CRate", "HP%"},
    "Vampire": {"CDmg", "CRate", "ATK%", "SPD"},
    "Violent": {"SPD", "HP%", "DEF%", "CRate", "CDmg"},
    "Nemesis": {"HP%", "SPD", "RES"},
    "Will": {"HP%", "DEF%", "SPD", "RES"},
    "Shield": {"HP%", "DEF%", "RES"},
    "Revenge": {"SPD", "CRate", "DEF%"},
    "Destroy": {"HP%", "DEF%", "ATK%"},
    "Fight": {"ATK%", "SPD"},
    "Determination": {"DEF%", "SPD"},
    "Enhance": {"HP%", "SPD"},
    "Accuracy": {"ACC", "SPD"},
    "Tolerance": {"RES", "SPD"}
}


# --- Efficiency calculation ---
def calc_efficiency(subs: List[Tuple[int, int]], prefix: Tuple[int, int] = None) -> float:
    total = 0.0
    max_total = 0.0

    for stat_id, val in subs:
        if stat_id in MAX_SUBSTAT_VALUES:
            max_val = MAX_SUBSTAT_VALUES[stat_id]
            total += val
            max_total += max_val

    if prefix and prefix[0] in MAX_SUBSTAT_VALUES:
        total += prefix[1]
        max_total += MAX_SUBSTAT_VALUES[prefix[0]]

    if max_total == 0:
        return 0.0

    return total / max_total  # 0–1


# --- Rune grader with reasons ---
def grade_rune(rune: Dict) -> Tuple[str, str]:
    set_name = RUNE_SETS.get(rune["set_id"], "Unknown")
    useful_stats = USEFUL_STATS.get(set_name, set())

    # Collect stats
    prefix = (rune["prefix_eff"][0], rune["prefix_eff"][1]) if rune.get("prefix_eff") else None
    subs = [(s[0], s[1]) for s in rune.get("sec_eff", [])]

    # Slot + main stat
    slot = rune.get("slot_no", "?")
    main_stat_name = STAT_NAMES.get(rune["pri_eff"][0], rune["pri_eff"][0])
    main_stat_val = rune["pri_eff"][1]
    main_display = f"{main_stat_name}+{main_stat_val}"

    # Human-readable stat breakdown
    breakdown = []
    for stat_id, val in subs:
        breakdown.append(f"{STAT_NAMES.get(stat_id, stat_id)}+{val}")
    if prefix and prefix[0] != 0:
        breakdown.append(f"Innate: {STAT_NAMES.get(prefix[0], prefix[0])}+{prefix[1]}")

    # For grading: just the stat names
    stat_names = [STAT_NAMES.get(stat_id, str(stat_id)) for stat_id, _ in subs]
    if prefix and prefix[0] != 0:
        stat_names.append(STAT_NAMES.get(prefix[0], str(prefix[0])))

    useful_count = sum(1 for s in stat_names if s in useful_stats)
    eff = calc_efficiency(subs, prefix)

    # --- Grading rules with reasons ---
    header = f"Slot {slot} {set_name} Rune — Main: {main_display}"
    statline = f"Stats: {', '.join(breakdown)}" if breakdown else "No substats"

    if eff < 0.60 and useful_count < 2:
        return "Trash", f"{header}\nReason: Low efficiency ({eff:.0%}) and only {useful_count} useful stat(s).\n{statline}"
    elif eff < 0.60:
        return "Trash", f"{header}\nReason: Efficiency too low ({eff:.0%}).\n{statline}"
    elif useful_count < 2:
        return "Trash", f"{header}\nReason: Only {useful_count} useful stat(s) for {set_name}.\n{statline}"
    elif eff < 0.75:
        return "Okay", f"{header}\nReason: Decent ({eff:.0%}) with {useful_count} useful stat(s).\n{statline}"
    elif eff < 0.85:
        return "Good", f"{header}\nReason: Solid ({eff:.0%}) with {useful_count} useful stat(s).\n{statline}"
    else:
        if useful_count >= 3:
            return "Godly", f"{header}\nReason: High efficiency ({eff:.0%}) and {useful_count} synergistic stats.\n{statline}"
        else:
            return "Good+", f"{header}\nReason: High efficiency ({eff:.0%}) but only {useful_count} useful stat(s).\n{statline}"


# --- Example usage ---
if __name__ == "__main__":
    sample_rune = {
        "set_id": 2,  # Guard
        "slot_no": 5,
        "pri_eff": [6, 15],  # DEF% +15
        "prefix_eff": [2, 8],  # HP% +8 innate
        "sec_eff": [[8, 5, 0, 0], [9, 5, 0, 0]]  # SPD+5, CRate+5
    }

    grade, reason = grade_rune(sample_rune)
    print(f"Rune grade: {grade}")
    print(reason)
