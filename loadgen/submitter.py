import os
import sys
import time
import random
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "monitoring")))
import queue_manager

HELIUM_HOST = os.getenv("HELIUM_HOST", "http://127.0.0.10:8000")

def load_source_code(lang, filename, custom_code=None):
    if custom_code and custom_code.strip():
        return custom_code
    
    file_path = os.path.join(os.path.dirname(__file__), "submissions", lang, filename)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    
    if lang == "cpp":
        return '#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    if (cin >> a >> b) cout << a + b << endl;\n    else cout << "Hello World!" << endl;\n    return 0;\n}'
    else:
        return 'import sys\nlines = sys.stdin.read().split()\nif len(lines) >= 2:\n    print(int(lines[0]) + int(lines[1]))\nelse:\n    print("Hello World!")\n'

def submit_to_helium(team="team1", password="team123_benchmark", problem_id=1, lang="cpp", filename="ac_sum.cpp", source_code=None, sub_id=None):
    if not source_code:
        source_code = load_source_code(lang, filename)

    if not sub_id:
        sub_id = queue_manager.enqueue_submission(
            target="helium",
            team=team,
            problem=f"Problema {problem_id}",
            language=lang,
            filename=filename,
            source_code=source_code,
            status="pending"
        )

    session = requests.Session()
    try:
        start_t = time.time()
        # 1. API Login
        login_res = session.post(f"{HELIUM_HOST}/api/tokens", json={"login": team, "password": password, "device_name": "locust"}, timeout=5)
        if login_res.status_code not in [200, 201] or "token" not in login_res.json():
            queue_manager.update_submission_status(sub_id, status="error", error_message="Falha na autenticação da API Helium")
            return sub_id, "ERROR"
        
        token = login_res.json()["token"]
        session.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/json"})
        
        # 2. POST /api/runs
        lang_id = 1 if lang == "cpp" else 2
        nonce = f"\n// t_{int(time.time()*1000)}" if lang == "cpp" else f"\n# t_{int(time.time()*1000)}"
        code_to_send = source_code + nonce
        files = {"source_file": (filename, code_to_send.encode("utf-8"), "text/plain")}
        data = {"contest_id": 1, "problem_id": problem_id, "language_id": lang_id}
        
        post_res = session.post(f"{HELIUM_HOST}/api/runs", data=data, files=files, timeout=5)
        http_latency = (time.time() - start_t) * 1000.0
        
        run_id = None
        if post_res.status_code in [200, 201]:
            run_id = post_res.json().get("id")
            queue_manager.update_submission_status(sub_id, status="judging", run_id=run_id, http_latency_ms=http_latency)
        else:
            err_msg = f"HTTP {post_res.status_code}: {post_res.text[:120]}"
            queue_manager.update_submission_status(sub_id, status="error", error_message=err_msg, http_latency_ms=http_latency)
            return sub_id, "ERROR"

        # 3. Poll verdict
        judge_start = time.time()
        verdict = "PENDING"
        if run_id:
            for _ in range(25):
                time.sleep(1)
                poll_res = session.get(f"{HELIUM_HOST}/api/runs/{run_id}", timeout=5)
                if poll_res.status_code == 200:
                    data = poll_res.json()
                    status = data.get("status")
                    if status == "judged":
                        ans_id = str(data.get("answer_id") or "")
                        result_text = str(data.get("auto_judge_result") or "").upper()
                        stderr_text = str(data.get("auto_judge_stderr") or "").upper()
                        if ans_id == "1" or "ACCEPT" in result_text or "YES" in result_text:
                            verdict = "AC"
                        elif ans_id == "2" or "WRONG" in result_text or "WA" in result_text:
                            verdict = "WA"
                        elif ans_id == "6" or "TIMEOUT" in stderr_text or "EXCEEDED THE TIMEOUT" in stderr_text or "TIME" in result_text:
                            verdict = "TLE"
                        elif ans_id == "4" or "COMPILATION" in result_text or "CE" in result_text or "ERROR:" in stderr_text:
                            verdict = "CE"
                        elif "JUDGING ERROR" in result_text:
                            verdict = "TLE" if "TIMEOUT" in stderr_text else "RE"
                        else:
                            verdict = "AC"
                        break

        judge_latency = (time.time() - judge_start) * 1000.0
        if verdict != "PENDING":
            final_status = "judged"
            queue_manager.update_submission_status(sub_id, status=final_status, verdict=verdict, judge_latency_ms=judge_latency)
        else:
            final_status = "error"
            queue_manager.update_submission_status(sub_id, status="error", verdict="TIMEOUT", error_message="Tempo limite esgotado aguardando veredito do Helium", judge_latency_ms=judge_latency)
        return sub_id, verdict

    except Exception as e:
        queue_manager.update_submission_status(sub_id, status="error", error_message=str(e))
        return sub_id, "ERROR"

def submit_test_run(filename="ac_sum.cpp", custom_code=None, team=None, problem_id=1, lang="cpp", target="helium", **kwargs):
    if not team:
        team = f"team{random.randint(1, 100)}"
    return submit_to_helium(team=team, problem_id=problem_id, lang=lang, filename=filename, source_code=custom_code)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Submit test run to Helium")
    parser.add_argument("--target", default="helium", help="Target system (default: helium)")
    parser.add_argument("--file", default="ac_sum.cpp")
    parser.add_argument("--lang", choices=["cpp", "py"], default="cpp")
    parser.add_argument("--team", default=None)
    args = parser.parse_args()
    
    print(f"Submitting test run to Helium ({args.file}) as {args.team}...")
    res = submit_test_run(filename=args.file, lang=args.lang, team=args.team)
    print("Result:", res)
