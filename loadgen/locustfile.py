import os
import sys
import time
import random
from locust import HttpUser, task, between, events

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "monitoring")))
try:
    import queue_manager
except Exception:
    queue_manager = None

# Read configuration from environment or defaults
ENABLED_VERDICTS = os.getenv("ENABLED_VERDICTS", "AC,WA,TLE,CE").split(",")
WAIT_INTERVAL = float(os.getenv("WAIT_INTERVAL", "2"))


class HeliumUser(HttpUser):
    """
    Locust User simulating Helium competitor workflow (Sanctum REST API + JSON Polling)
    """
    wait_time = between(max(0.5, WAIT_INTERVAL - 0.5), WAIT_INTERVAL + 0.5)

    def get_submission_file(self):
        """Pick a file based on enabled verdicts checklist"""
        verdicts = [v.strip().upper() for v in ENABLED_VERDICTS if v.strip()]
        if not verdicts:
            verdicts = ["AC"]
        
        chosen = random.choice(verdicts)
        lang = random.choice(["cpp", "py"])
        
        file_mapping = {
            "AC": f"ac_sum.{lang}",
            "WA": f"wa_sum.{lang}",
            "TLE": f"tle_loop.{lang}",
            "CE": f"ce_syntax.{lang}"
        }

        filename = file_mapping.get(chosen, f"ac_sum.{lang}")
        file_path = os.path.join(os.path.dirname(__file__), "submissions", lang, filename)
        return chosen, lang, filename, file_path

    def on_start(self):
        self.username = f"team{random.randint(1, 100)}"
        self.password = "team123_benchmark"
        res = self.client.post("/api/tokens", json={
            "login": self.username,
            "password": self.password,
            "device_name": "locust"
        }, name="Helium: API Login")
        
        if res.status_code in [200, 201] and "token" in res.json():
            token = res.json()["token"]
            self.client.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/json"})

    @task
    def submit_and_poll_run(self):
        chosen_verdict, lang, filename, file_path = self.get_submission_file()
        
        if not os.path.exists(file_path):
            return

        with open(file_path, "r", encoding="utf-8", errors="replace") as sf:
            source_code = sf.read()

        sub_id = None
        if queue_manager:
            sub_id = queue_manager.enqueue_submission(
                target="helium",
                team=getattr(self, "username", "team1"),
                problem="Problema 1",
                language=lang,
                filename=filename,
                source_code=source_code,
                status="pending"
            )

        start_time = time.time()

        # 1. HTTP POST multipart submission to API
        nonce = f"\n// t_{int(time.time()*1000)}" if lang == "cpp" else f"\n# t_{int(time.time()*1000)}"
        code_bytes = (source_code + nonce).encode("utf-8")
        response = self.client.post("/api/runs", data={
            "contest_id": 1,
            "problem_id": 1,
            "language_id": 1 if lang == "cpp" else 2
        }, files={
            "source_file": (filename, code_bytes, "text/plain")
        }, name="Helium: POST /api/runs")

        http_latency = (time.time() - start_time) * 1000.0

        run_id = None
        if response.status_code in [200, 201]:
            run_id = response.json().get("id")
            if sub_id and queue_manager:
                queue_manager.update_submission_status(sub_id, status="judging", run_id=run_id, http_latency_ms=http_latency)
        else:
            if sub_id and queue_manager:
                queue_manager.update_submission_status(sub_id, status="error", error_message=f"HTTP {response.status_code}: {response.text[:100]}", http_latency_ms=http_latency)
            return

        # 2. Polling for JSON verdict
        judge_start = time.time()
        verdict_found = False
        final_verdict = "PENDING"
        attempts = 0

        while not verdict_found and attempts < 25:
            time.sleep(1)
            attempts += 1
            res = self.client.get(f"/api/runs/{run_id}", name="Helium: GET /api/runs/{id}")
            if res.status_code == 200 and res.json().get("status") == "judged":
                verdict_found = True
                data = res.json()
                ans_id = str(data.get("answer_id") or "")
                result_text = str(data.get("auto_judge_result") or "").upper()
                stderr_text = str(data.get("auto_judge_stderr") or "").upper()
                if ans_id == "1" or "ACCEPT" in result_text or "YES" in result_text:
                    final_verdict = "AC"
                elif ans_id == "2" or "WRONG" in result_text or "WA" in result_text:
                    final_verdict = "WA"
                elif ans_id == "6" or "TIMEOUT" in stderr_text or "EXCEEDED THE TIMEOUT" in stderr_text or "TIME" in result_text:
                    final_verdict = "TLE"
                elif ans_id == "4" or "COMPILATION" in result_text or "CE" in result_text or "ERROR:" in stderr_text:
                    final_verdict = "CE"
                elif "JUDGING ERROR" in result_text:
                    final_verdict = "TLE" if "TIMEOUT" in stderr_text else "RE"
                else:
                    final_verdict = "AC"

        total_judge_time = (time.time() - judge_start) * 1000.0

        if sub_id and queue_manager:
            if verdict_found:
                queue_manager.update_submission_status(sub_id, status="judged", verdict=final_verdict, judge_latency_ms=total_judge_time)
            else:
                queue_manager.update_submission_status(sub_id, status="error", verdict="TIMEOUT", error_message="Tempo limite esgotado aguardando veredito do Helium", judge_latency_ms=total_judge_time)

        # Fire custom synthetic event for autojudge latency
        events.request.fire(
            request_type="JUDGE",
            name="Helium: submission_to_verdict",
            response_time=total_judge_time,
            response_length=0,
            exception=None,
            context=None
        )
