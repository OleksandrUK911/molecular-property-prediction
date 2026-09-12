from backend.app import db


def test_init_db_is_idempotent():
    db.init_db()
    db.init_db()  # must not raise on second call


def test_insert_and_list_history_newest_first():
    db.init_db()
    db.insert_history("id-1", "CCO", -0.5, "0.1.0", "2026-01-01T00:00:00Z")
    db.insert_history("id-2", "CCC", -1.2, "0.1.0", "2026-01-02T00:00:00Z")

    rows = db.list_history()

    assert [r["id"] for r in rows] == ["id-2", "id-1"]
    assert rows[0]["smiles"] == "CCC"
    assert rows[0]["predicted_target"] == -1.2


def test_list_history_respects_limit():
    db.init_db()
    for i in range(5):
        db.insert_history(f"id-{i}", "CCO", -0.5, "0.1.0", f"2026-01-0{i + 1}T00:00:00Z")

    assert len(db.list_history(limit=3)) == 3


def test_list_history_empty():
    db.init_db()
    assert db.list_history() == []
