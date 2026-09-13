from locust import LoadTestShape

class BaselineShape(LoadTestShape):
    """
    Baseline Scenario: 1 constant user for 2 minutes
    Goal: Measure idle resource utilization and baseline latency without contention
    """
    time_limit = 120
    spawn_rate = 1
    users = 1

    def tick(self):
        run_time = self.get_run_time()
        if run_time < self.time_limit:
            return (self.users, self.spawn_rate)
        return None
