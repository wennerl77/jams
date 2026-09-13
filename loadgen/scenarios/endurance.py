from locust import LoadTestShape

class EnduranceShape(LoadTestShape):
    """
    Endurance Scenario: Moderate constant load over hours
    Goal: Detect memory leaks, zombie processes, or degradation
    """
    time_limit = 3600
    spawn_rate = 2
    users = 20

    def tick(self):
        run_time = self.get_run_time()
        if run_time < self.time_limit:
            return (self.users, self.spawn_rate)
        return None
