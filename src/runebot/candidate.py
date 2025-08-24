import sqlite3

DB_PATH = "monsterbox.db"

def get_candidate_monsters(rune_set_id, rune_slot, limit=5):
    """
    Return a list of monsters to consider for a given rune, filtered by priority
    and preferred rune sets.
    
    :param rune_set_id: int, the set ID of the rune
    :param rune_slot: int, slot number 1-6
    :param limit: int, max number of monsters to return
    :return: list of dicts with monster info
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us fetch results as dicts
    cur = conn.cursor()

    query = """
    SELECT *
    FROM monsters m
    WHERE EXISTS (
        SELECT 1
        FROM monster_rune_preferences p
        WHERE p.monster_id = m.id
          AND p.set_id = ?
          AND (p.slot = ? OR p.slot IS NULL)
    )
    ORDER BY m.priority_id ASC  -- smaller number = higher priority
    LIMIT ?
    """
    
    cur.execute(query, (rune_set_id, rune_slot, limit))
    results = cur.fetchall()
    conn.close()

    # Convert sqlite3.Row objects to dicts
    return [dict(row) for row in results]


# Example usage:
candidates = get_candidate_monsters(rune_set_id=1, rune_slot=2, limit=5)
for c in candidates:
    print(c["name"], c["priority_id"])