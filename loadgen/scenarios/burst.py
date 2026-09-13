from locust import LoadTestShape

class BurstShape(LoadTestShape):
    """
    Burst Scenario: Instantaneous jump to 100% users in < 1 minute
    Goal: Simulate contest start / scoreboard freeze unfreeze spike
    """
    time_limit = 300
    spawn_rate = 50
    users = 50

    def tick(self):
        run_time = self.get_run_time()
        if run_time < self.time_limit:
            return (self.users, self.spawn_rate)
        return None
