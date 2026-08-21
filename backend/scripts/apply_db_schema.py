import sqlite3

def apply_schema():
    conn = sqlite3.connect("data/workflow.db")
    cur = conn.cursor()

    columns_to_add = [
        ("video_assets", "r2_key", "TEXT"),
        ("video_assets", "url", "TEXT"),
        ("video_translation_jobs", "r2_key", "TEXT"),
        ("video_translation_jobs", "output_url", "TEXT"),
        ("video_translation_jobs", "is_cleaned", "INTEGER DEFAULT 0"),
        ("projects", "r2_key", "TEXT"),
        ("projects", "media_url", "TEXT"),
    ]

    for table, col, col_type in columns_to_add:
        try:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
            print(f"Added column '{col}' to table '{table}'")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                pass
            else:
                print(f"Note altering {table}.{col}:", e)

    conn.commit()
    conn.close()
    print("✓ Schema update complete!")

if __name__ == "__main__":
    apply_schema()
