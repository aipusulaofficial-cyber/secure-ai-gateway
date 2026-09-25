from locust import HttpUser,task,between
class APIUser(HttpUser):
    wait_time=between(.1,.5)
    @task
    def domain(self):
        self.client.post("/v1/gateway",json={"key":"load","payload":{"text":"load","query":"load","version":"1","total":1,"successes":1,"target":.99}},name="/v1/gateway")