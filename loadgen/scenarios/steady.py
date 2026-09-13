from locust import LoadTestShape

class SteadyShape(LoadTestShape):
    """
    Steady Scenario: Constant load of N users for 25 minutes
    Goal: Evaluate performance under sustained contest state
    """
    time_limit = 1500
    spawn_rate = 5
    users = 30

    def tick(self):
        run_time = self.get_run_time()
        if run_time < self.time_limit:
            return (self.users, self.spawn_rate)
        return None
