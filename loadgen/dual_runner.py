import os
import sys
import time
import random
import signal
import argparse
import concurrent.futures

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "monitoring")))
import queue_manager
import submitter

running = True

def handle_signal(sig, frame):
    global running
    running = False

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

def get_submission_file(verdicts_list, rng):
    verdicts = [v.strip().upper() for v in verdicts_list if v.strip()]
    if not verdicts:
        verdicts = ["AC"]
    
    chosen = rng.choice(verdicts)
    lang = rng.choice(["cpp", "py"])
    
    file_mapping = {
        "AC": f"ac_sum.{lang}",
        "WA": f"wa_sum.{lang}",
        "TLE": f"tle_loop.{lang}",
        "CE": f"ce_syntax.{lang}"
    }
    filename = file_mapping.get(chosen, f"ac_sum.{lang}")
    return chosen, lang, filename

def run_user_worker(user_id, interval, verdicts_list, seed, duration):
    global running
    rng = random.Random(seed + user_id * 1000)
    team_name = f"team{user_id}"
    start_time = time.time()
    
    while running:
        if duration > 0 and (time.time() - start_time) >= duration:
            break

        chosen, lang, filename = get_submission_file(verdicts_list, rng)
        problem_id = 1

        try:
            sub_id, verdict = submitter.submit_test_run(
                filename=filename,
                team=team_name,
                problem_id=problem_id,
                lang=lang
            )
            print(f"[HELIUM-RUNNER] [User {user_id}] Dispatched run '{filename}' -> Helium: sub_id={sub_id}, verdict={verdict}", flush=True)
        except Exception as e:
            print(f"[HELIUM-RUNNER] [User {user_id}] Error in Helium submission: {e}", flush=True)

        if not running:
            break
            
        time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description="Synchronous Runner for Helium")
    parser.add_argument("-u", "--users", type=int, default=int(os.getenv("USERS", "5")), help="Number of concurrent Helium users")
    parser.add_argument("-i", "--interval", type=float, default=float(os.getenv("WAIT_INTERVAL", "2")), help="Wait interval between submissions in seconds")
    parser.add_argument("-v", "--verdicts", type=str, default=os.getenv("ENABLED_VERDICTS", "AC,WA,TLE,CE"), help="Comma-separated list of enabled verdicts")
    parser.add_argument("-t", "--duration", type=int, default=int(os.getenv("DURATION", "0")), help="Duration limit in seconds (0 = continuous)")
    parser.add_argument("-s", "--seed", type=int, default=int(os.getenv("RANDOM_SEED", "42")), help="Random seed for deterministic workload")
    args = parser.parse_args()

    verdicts_list = args.verdicts.split(",")
    print(f"=== Starting Synchronous Helium Runner ===")
    print(f"Users: {args.users} | Interval: {args.interval}s | Verdicts: {verdicts_list} | Duration: {args.duration}s | Seed: {args.seed}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.users) as executor:
        futures = [
            executor.submit(run_user_worker, user_id, args.interval, verdicts_list, args.seed, args.duration)
            for user_id in range(1, args.users + 1)
        ]
        try:
            for fut in concurrent.futures.as_completed(futures):
                fut.result()
        except KeyboardInterrupt:
            global running
            running = False
            print("[HELIUM-RUNNER] Stopping execution...")

if __name__ == "__main__":
    main()
