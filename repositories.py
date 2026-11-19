import json
from database.db import get_connection

def save_analysis(user_id, filename, result):
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO analyses(user_id,filename,result_json) VALUES(?,?,?)",
                           (user_id, filename, json.dumps(result)))
        return cur.lastrowid

def get_analysis_history(user_id):
    with get_connection() as conn:
        rows = conn.execute("SELECT id,filename,created_at FROM analyses WHERE user_id=? ORDER BY id DESC",
                            (user_id,)).fetchall()
    return [dict(r) for r in rows]

def get_analysis_by_id(user_id, analysis_id):
    with get_connection() as conn:
        row = conn.execute("SELECT result_json FROM analyses WHERE id=? AND user_id=?",
                           (analysis_id,user_id)).fetchone()
    return json.loads(row["result_json"]) if row else None


def delete_analysis(user_id, analysis_id):
    with get_connection() as conn:
        cur = conn.execute(
            "DELETE FROM analyses WHERE id=? AND user_id=?",
            (analysis_id, user_id)
        )
        return cur.rowcount > 0



def list_users():
    with get_connection() as conn:
        rows = conn.execute("SELECT id,username,email,role,status FROM users ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]

def set_user_status(user_id, status):
    if status not in {"pending","approved","rejected","suspended"}:
        raise ValueError("Invalid status")
    with get_connection() as conn:
        conn.execute("UPDATE users SET status=? WHERE id=? AND role!='admin'", (status,user_id))

def get_system_stats():
    with get_connection() as conn:
        users = conn.execute("SELECT COUNT(*) n FROM users").fetchone()["n"]
        pending = conn.execute("SELECT COUNT(*) n FROM users WHERE status='pending'").fetchone()["n"]
        analyses = conn.execute("SELECT COUNT(*) n FROM analyses").fetchone()["n"]
    return {"users":users,"pending":pending,"analyses":analyses}
