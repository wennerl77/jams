import os
import sys
import sqlite3
import time

def log_event(msg):
    now_str = time.strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{now_str}] {msg}\n"
    sys.stdout.write(log_line)
    sys.stdout.flush()
    try:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        log_file = os.path.join(root_dir, "results", "dashboard.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception:
        pass

def get_db_path():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    queue_dir = os.path.join(root_dir, "results", "queue")
    os.makedirs(queue_dir, exist_ok=True)
    return os.path.join(queue_dir, "submissions.db")

def get_connection():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    return conn

def init_queue_db():
    conn = get_connection()
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL,
            run_id TEXT,
            team TEXT NOT NULL,
            problem TEXT NOT NULL,
            language TEXT NOT NULL,
            filename TEXT NOT NULL,
            source_code TEXT NOT NULL,
            status TEXT NOT NULL,
            verdict TEXT DEFAULT 'PENDING',
            http_latency_ms REAL DEFAULT 0.0,
            judge_latency_ms REAL DEFAULT 0.0,
            submitted_at REAL NOT NULL,
            judged_at REAL,
            error_message TEXT
        );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_target_status ON submissions(target, status);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_target_time ON submissions(target, submitted_at DESC);")
    conn.close()

def enqueue_submission(target, team, problem, language, filename, source_code, status="pending", verdict="PENDING", http_latency_ms=0.0):
    init_queue_db()
    conn = get_connection()
    now = time.time()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO submissions 
            (target, team, problem, language, filename, source_code, status, verdict, http_latency_ms, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (target, team, problem, language, filename, source_code, status, verdict, http_latency_ms, now))
        sub_id = cursor.lastrowid
    conn.close()
    log_event(f"[QUEUE] [ENQUEUE] ID={sub_id} Target={target.upper()} Team={team} Problem={problem} Lang={language} File={filename} Status={status}")
    return sub_id

def update_submission_status(submission_id, status, verdict=None, judge_latency_ms=None, http_latency_ms=None, run_id=None, error_message=None):
    if not submission_id:
        return
    conn = get_connection()
    now = time.time()
    
    updates = ["status = ?"]
    params = [status]
    
    if verdict is not None:
        updates.append("verdict = ?")
        params.append(verdict)
    if judge_latency_ms is not None:
        updates.append("judge_latency_ms = ?")
        params.append(judge_latency_ms)
        updates.append("judged_at = ?")
        params.append(now)
    if http_latency_ms is not None:
        updates.append("http_latency_ms = ?")
        params.append(http_latency_ms)
    if run_id is not None:
        updates.append("run_id = ?")
        params.append(str(run_id))
    if error_message is not None:
        updates.append("error_message = ?")
        params.append(error_message)

    params.append(submission_id)
    query = f"UPDATE submissions SET {', '.join(updates)} WHERE id = ?"

    with conn:
        conn.execute(query, params)
    conn.close()
    lat_str = f" JudgeLatency={judge_latency_ms:.1f}ms" if judge_latency_ms is not None else ""
    run_str = f" RunID={run_id}" if run_id is not None else ""
    err_str = f" Error={error_message}" if error_message is not None else ""
    log_event(f"[QUEUE] [UPDATE] ID={submission_id} Status={status} Verdict={verdict}{run_str}{lat_str}{err_str}")

def cleanup_stale_submissions(timeout_seconds=45):
    """Marks any submission that has been in judging/pending state longer than timeout_seconds as error."""
    init_queue_db()
    conn = get_connection()
    cutoff = time.time() - timeout_seconds
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE submissions 
            SET status = 'error', verdict = 'TIMEOUT', error_message = 'Tempo limite excedido na fila (execução abortada ou travada)'
            WHERE status IN ('pending', 'judging', 'queued') AND submitted_at < ?
        """, (cutoff,))
        if cursor.rowcount > 0:
            log_event(f"[QUEUE] [CLEANUP] Expired {cursor.rowcount} stale submission(s) older than {timeout_seconds}s")
    conn.close()

def fetch_queue(target, status_filter=None, lang_filter=None, search=None, limit=50):
    init_queue_db()
    cleanup_stale_submissions()
    conn = get_connection()
    
    where_clauses = ["target = ?"]
    params = [target]
    
    if status_filter and status_filter != "Todas":
        if status_filter == "Aguardando / Validando":
            where_clauses.append("status IN ('pending', 'judging', 'queued')")
        elif status_filter == "Já Validadas":
            where_clauses.append("status = 'judged'")
        elif status_filter == "Com Erro":
            where_clauses.append("(status = 'error' OR verdict IN ('CE', 'RE', 'ERR'))")
        elif status_filter in ["AC", "WA", "TLE", "CE"]:
            where_clauses.append("verdict = ?")
            params.append(status_filter)
            
    if lang_filter and lang_filter != "Todas":
        if "cpp" in lang_filter.lower() or "c++" in lang_filter.lower():
            where_clauses.append("language IN ('cpp', 'c++')")
        elif "python" in lang_filter.lower() or "py" in lang_filter.lower():
            where_clauses.append("language IN ('py', 'python')")

    if search:
        where_clauses.append("(team LIKE ? OR filename LIKE ? OR id LIKE ?)")
        term = f"%{search}%"
        params.extend([term, term, term])
        
    query = f"""
        SELECT * FROM submissions 
        WHERE {' AND '.join(where_clauses)}
        ORDER BY submitted_at DESC
        LIMIT ?
    """
    params.append(limit)
    
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_queue_summary(target):
    init_queue_db()
    cleanup_stale_submissions()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status IN ('pending', 'queued') THEN 1 ELSE 0 END) as pending_count,
            SUM(CASE WHEN status = 'judging' THEN 1 ELSE 0 END) as judging_count,
            SUM(CASE WHEN status = 'judged' THEN 1 ELSE 0 END) as judged_count,
            SUM(CASE WHEN status = 'error' OR verdict IN ('CE', 'RE', 'ERR') THEN 1 ELSE 0 END) as error_count
        FROM submissions
        WHERE target = ?
    """, (target,))
    
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "total": row["total"] or 0,
            "pending": row["pending_count"] or 0,
            "judging": row["judging_count"] or 0,
            "judged": row["judged_count"] or 0,
            "error": row["error_count"] or 0,
        }
    return {"total": 0, "pending": 0, "judging": 0, "judged": 0, "error": 0}

def clear_queue(target=None):
    db_path = get_db_path()
    if not os.path.exists(db_path):
        return
    conn = get_connection()
    with conn:
        if target:
            conn.execute("DELETE FROM submissions WHERE target = ?", (target,))
        else:
            conn.execute("DELETE FROM submissions")
    conn.close()
