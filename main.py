import json
import random
import string
import requests
from datetime import datetime


class GremlinAttacks(object):
    def __init__(self):
        self.TEAM_ID = "97ae1e3d-9433-552c-8adf-eba9567e7fe5"
        self.API_KEY = "***REMOVED_GREMLIN_API_KEY***"
        self.URL = f"https://api.gremlin.com/v1/kubernetes/attacks/new?teamId={self.TEAM_ID}"


    def genrate_uuid(self):
        def helper(number):
            return ''.join(random.choices(string.ascii_lowercase + string.digits, k=number))

        return f"{helper(8)}-{helper(4)}-{helper(4)}-{helper(4)}-{helper(12)}"



    def cpuAttack(self):
        cpu_percentage = random.randint(50,100)
        seconds = random.randint(60,240)
        current_time = datetime.utcnow()
        uuid = self.genrate_uuid()
        current_datetime_stamp = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        payload = {'targetDefinition': {'strategy': {'labels': {},
                                                     'k8sObjects': [{
                                                         "clusterId": "intcloud-ccgf-eks-devci-usw2",
                                                         "createdAt": current_datetime_stamp,
                                                         "uid": uuid,
                                                         "namespace": "intcloud-qastaging-ccgf",
                                                         "name": "ccgf-ingestion-processor-production-1604987899047-exec-1",
                                                         "kind": "POD",
                                                         "labels": {},
                                                         "annotations": {},
                                                         "podPhase": "Running",

                                                         # make a fucntion to retrieve this information
                                                         "availableContainers": [{
                                                             "uid": "docker://ddf1ade1035a5af2d23a0ec06f792c7b6460464f251cb25bdd030e605d860ca1",
                                                             "unifiedUid": "ddf1ade1035a5af2d23a0ec06f792c7b6460464f251cb25bdd030e605d860ca1",
                                                             "name": "spark-kubernetes-executor",
                                                             "state": "RUNNING"
                                                         }]
                                                     }
                                                     ],
                                                     "percentage": 100}},
                   'impactDefinition': {'cliArgs': ["cpu", "-l", f"{seconds}", "-c","1", "-p", f"{cpu_percentage}"]}}
        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Authorization": f"Key {self.API_KEY}"
        }
        response = requests.post(url=self.URL,
                                 headers=headers,
                                 data=json.dumps(payload))
        print(response.text)


    def memoryAttack(self):
        uuid = self.genrate_uuid()
        gb = random.randint(1, 5)
        current_time = datetime.utcnow()
        seconds = random.randint(60, 240)
        current_datetime_stamp = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        payload = {'targetDefinition': {'strategy': {'labels': {},
                                                     'k8sObjects': [{
                                                         'clusterId': 'intcloud-ccgf-eks-devci-usw2',
                                                         'createdAt': current_datetime_stamp,
                                                         'uid': "4e5dea1b-39b1-42fa-9396-20af01be4f4e",
                                                         'namespace': 'intcloud-qastaging-ccgf',
                                                         'name': 'ccgf-content-1-0-0-79',
                                                         'kind': 'DEPLOYMENT',
                                                         'labels': {},
                                                         'annotations': {},
                                                         'availableContainers': []}],
                                                     "percentage": 100
                                                     }},
                   'impactDefinition': {'cliArgs': ['memory', '-l', f"{seconds}", '-g', f"{gb}", "1"]}}
        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Authorization": f"Key {self.API_KEY}"
        }
        print(payload)
        response = requests.post(url=self.URL,
                                 headers=headers,
                                 data=json.dumps(payload))
        print(response.text)


gremlin_obj = GremlinAttacks()
gremlin_obj.cpuAttack()
gremlin_obj.memoryAttack()






