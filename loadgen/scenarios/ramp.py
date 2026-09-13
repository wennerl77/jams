from locust import LoadTestShape

class RampShape(LoadTestShape):
    """
    Ramp Scenario: Stepwise increase (10 -> 25 -> 50 -> 100 users)
    Goal: Identify inflection point and hardware saturation limit
    """
    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 2},
        {"duration": 180, "users": 25, "spawn_rate": 5},
        {"duration": 300, "users": 50, "spawn_rate": 10},
        {"duration": 420, "users": 100, "spawn_rate": 20},
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
        return None
