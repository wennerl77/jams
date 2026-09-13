import os
import time
import random
from bs4 import BeautifulSoup
from locust import HttpUser, task, between, events, DynamicResponse

# Read configuration from environment or defaults
ENABLED_VERDICTS = os.getenv("ENABLED_VERDICTS", "AC,WA,TLE,CE").split(",")
TARGET_SYSTEM = os.getenv("TARGET_SYSTEM", "boca")

class BaseJudgeUser(HttpUser):
    abstract = True
    wait_time = between(1, 3)

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

class BocaUser(BaseJudgeUser):
    """
    Locust User simulating BOCA competitor workflow (Cookie Auth + HTML forms + Polling)
    """
    def on_start(self):
        self.username = f"team{random.randint(1, 100)}"
        self.password = "team123_benchmark"
        self.client.post("/index.php", data={
            "user": self.username,
            "password": self.password,
            "site": 1
        }, name="BOCA: Login")

    @task
    def submit_and_poll_run(self):
        chosen_verdict, lang, filename, file_path = self.get_submission_file()
        
        if not os.path.exists(file_path):
            return

        start_time = time.time()
        
        # 1. HTTP POST multipart submission
        with open(file_path, "rb") as f:
            response = self.client.post("/run.php", data={
                "problem": 1,
                "language": 1 if lang == "cpp" else 2,
                "form_submission": "Submit"
            }, files={
                "sourcefile": (filename, f, "text/plain")
            }, name="BOCA: POST /run.php")

        http_latency = (time.time() - start_time) * 1000

        # 2. Polling for verdict (JUDGE synthetic event measurement)
        judge_start = time.time()
        verdict_found = False
        attempts = 0

        while not verdict_found and attempts < 10:
            time.sleep(1)
            attempts += 1
            res = self.client.get("/run.php", name="BOCA: Poll /run.php")
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                # Look for verdict in table
                if "YES" in res.text or "NO" in res.text or "ACCEPTED" in res.text:
                    verdict_found = True

        total_judge_time = (time.time() - judge_start) * 1000

        # Fire custom synthetic event for autojudge latency
        events.request.fire(
            request_type="JUDGE",
            name="BOCA: submission_to_verdict",
            response_time=total_judge_time,
            response_length=0,
            exception=None,
            context=None
        )


class HeliumUser(BaseJudgeUser):
    """
    Locust User simulating Helium competitor workflow (Sanctum REST API + JSON Polling)
    """
    def on_start(self):
        self.username = f"team{random.randint(1, 100)}"
        self.password = "team123_benchmark"
        res = self.client.post("/api/login", json={
            "username": self.username,
            "password": self.password
        }, name="Helium: API Login")
        
        if res.status_code == 200 and "token" in res.json():
            token = res.json()["token"]
            self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task
    def submit_and_poll_run(self):
        chosen_verdict, lang, filename, file_path = self.get_submission_file()
        
        if not os.path.exists(file_path):
            return

        start_time = time.time()

        # 1. HTTP POST multipart submission to API
        with open(file_path, "rb") as f:
            response = self.client.post("/api/runs", data={
                "contest_id": 1,
                "problem_id": 1,
                "language_id": 1 if lang == "cpp" else 2
            }, files={
                "source_file": (filename, f, "text/plain")
            }, name="Helium: POST /api/runs")

        # 2. Polling for JSON verdict
        judge_start = time.time()
        verdict_found = False
        attempts = 0

        if response.status_code in [200, 201]:
            run_id = response.json().get("id", 1)
            while not verdict_found and attempts < 10:
                time.sleep(1)
                attempts += 1
                res = self.client.get(f"/api/runs/{run_id}", name="Helium: GET /api/runs/{id}")
                if res.status_code == 200 and res.json().get("status") == "judged":
                    verdict_found = True

        total_judge_time = (time.time() - judge_start) * 1000

        # Fire custom synthetic event for autojudge latency
        events.request.fire(
            request_type="JUDGE",
            name="Helium: submission_to_verdict",
            response_time=total_judge_time,
            response_length=0,
            exception=None,
            context=None
        )
