from asyncio.windows_events import INFINITE
from urllib import parse
from locust import HttpUser, task, between
import logging
import json
import time
import urllib3
from faker import Faker
fake = Faker()
urllib3.disable_warnings()

'''
* Run below command to run the load test

pip install locust
locust -f app/tests/locustfile.py
'''

class User(HttpUser):
    wait_time = between(1, 2)
    
    def on_start(self):
        self.client.verify = False
        

        
    # @task
    # def toggle_bookmark(self):
    #     for id in range(5):
    #         with self.client.rename_request(f"/bookmark/listing/toggle-{id}"):
    #             query = {
    #                 "plusId": id,
    #                 "listingId": fake.random_int(1,5)
    #                 }
    #             res = self.client.post(f"/bookmark/listing/toggle",json=query)
    
    @task
    def toggle_bookmark(self):
        id = fake.random_int(1,10000)
        with self.client.rename_request(f"/user/login"):
            query = {
                "plusId": id,
                "userType": fake.random_element(["admin","personal","master"]) 
                }
            res = self.client.post(f"/user/login",json=query)