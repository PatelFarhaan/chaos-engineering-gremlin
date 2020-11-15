import json
import time
import random
import requests


# Get logs and store to S3: Folder name would be current day and content would be all attacks in 3 folders
# Send notification of attacks to ramarao and me via aws sns

class GremlinAttacks(object):
    def __init__(self):
        self.SERVICES = ["ccgf-search"]
        self.ATTACKS = ["DEPLOYMENT", "POD"]
        self.SECONDS = random.randint(60, 240)
        self.PERCENTAGE = random.randint(90, 100)
        self.NAMESPACE = "intcloud-qastaging-ccgf"
        self.CLUSTER = "intcloud-ccgf-eks-devci-usw2"
        self.TEAM_ID = "97ae1e3d-9433-552c-8adf-eba9567e7fe5"
        self.HOSTS_URL = f"https://api.gremlin.com/v1/attacks/new?teamId={self.TEAM_ID}"
        self.API_KEY = "***REMOVED_GREMLIN_API_KEY***"
        self.KUBERNETS_URL = f"https://api.gremlin.com/v1/kubernetes/attacks/new?teamId={self.TEAM_ID}"

        self.HEADERS = {
            "Content-Type": "application/json;charset=utf-8",
            "Authorization": f"Key {self.API_KEY}"
        }

        self.KUBERNETES_PAYLOAD = {
            "targetDefinition": {
                "strategy": {
                    "labels": {},
                    "k8sObjects": [],
                    "percentage": 100
                }
            },
            "impactDefinition": {
                "cliArgs": []
            }
        }

        self.HOSTS_PAYLOAD = {
            "target": {
                "type": "Random",
                "hosts": {
                    "multiSelectTags": {
                        "instance-id": []
                    }
                },
                "percent": 100
            },
            "command": {}
        }

        self.CONTAINERS_PAYLOAD = {
            "target": {
                "type": "Random",
                "containers": {
                    "multiSelectLabels": {
                        "io.kubernetes.pod.name": []
                    }
                },
                "percent": 100
            },
            "command": {}
        }


    def dumpLogsInS3(self):
        pass

    def addTime(self):
        time.sleep(100)

    def runAllAttacksOnContainers(self, target_name):  # This is for single container, make it for all as a list
        self.ioAttackOnContainers(target_name)
        self.cpuAttackOnContainers(target_name)
        self.diskAttackOnContainers(target_name)
        self.memoryAttackOnContainers(target_name)
        self.dnsKillAttackOnContainers(target_name)
        self.processKillAttackOnContainers(target_name)
        self.latencyKillAttackOnContainers(target_name)
        self.shutDownKillAttackOnContainers(target_name)
        self.blackHoleKillAttackOnContainers(target_name)
        self.packetLossKillAttackOnContainers(target_name)

    def runAllAttacksOnKubernetes(self, target_name):  # This is for single container, make it for all as a list
        self.ioAttackOnKubernetes(target_name)
        self.cpuAttackOnKubernetes(target_name)
        self.diskAttackOnKubernetes(target_name)
        self.memoryAttackOnKubernetes(target_name)
        self.dnsKillAttackOnKubernetes(target_name)
        self.processKillAttackOnKubernetes(target_name)
        self.latencyKillAttackOnKubernetes(target_name)
        self.shutDownKillAttackOnKubernetes(target_name)
        self.blackHoleKillAttackOnKubernetes(target_name)
        self.packetLossKillAttackOnKubernetes(target_name)

    def runAllAttacksOnHost(self, target_name):  # This is for single container, make it for all as a list
        self.ioAttackOnHosts(target_name)
        self.cpuAttackOnHosts(target_name)
        self.diskAttackOnHosts(target_name)
        self.memoryAttackOnHosts(target_name)
        self.dnsKillAttackOnHosts(target_name)
        self.latencyKillAttackOnHosts(target_name)
        self.processKillAttackOnHosts(target_name)
        self.shutDownKillAttackOnHosts(target_name)
        self.blackHoleKillAttackOnHosts(target_name)
        self.packetLossKillAttackOnHosts(target_name)
        self.timeTravelKillAttackOnHosts(target_name)

    def getAllActiveContainers(self):
        url = "https://api.gremlin.com/v1/containers"
        payload = {}
        response = requests.get(url=url,
                                data=payload,
                                headers=self.HEADERS)
        if response.status_code == 200:
            result = []
            data = response.json()
            for object in data:
                if object.get("container_labels"):
                    if object["container_labels"].get("io.kubernetes.pod.namespace"):
                        if object["container_labels"]["io.kubernetes.pod.namespace"] == self.NAMESPACE:
                            pod_name = object["container_labels"]["io.kubernetes.pod.name"]
                            if pod_name:
                                for service in self.SERVICES:
                                    if service in pod_name:
                                        result.append(pod_name)
            return result
        else:
            return False

    def getAllAvailableKubernetesTargets(self):
        url = "https://api.gremlin.com/v1/kubernetes/targets"
        payload = {}
        response = requests.get(url,
                                data=payload,
                                headers=self.HEADERS)

        if response.status_code == 200:
            data = response.json()
            result = {}
            result["POD"] = []
            result["DEPLOYMENT"] = []

            for clusters in data:
                if clusters.get("clusterId") == self.CLUSTER:
                    if clusters.get("objects"):
                        for object in clusters.get("objects"):
                            if object.get("namespace") == self.NAMESPACE:

                                if object.get("kind") == "DEPLOYMENT":
                                    for service in self.SERVICES:
                                        if service in object.get("name"):
                                            result["DEPLOYMENT"].append(object)
                                elif object.get("kind") == "POD":
                                    for service in self.SERVICES:
                                        if service in object.get("name"):
                                            result["POD"].append(object)
            return result
        else:
            return False

    # 558bd13933363828ca968fb43207d3731fd545da for infa-mopatel

    def postAPIRequest(self, url, headers, payload):
        response = requests.post(url=url,
                                 headers=headers,
                                 data=json.dumps(payload))
        print(response.text)

    def cpuAttackOnKubernetes(self, target_object):
        cli_args = ["cpu", "-l", f"{self.SECONDS}", "-c", "1", "-p", f"{self.PERCENTAGE}"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = [target_object]
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD)
        self.addTime()

    def memoryAttackOnKubernetes(self, target_object):
        gb = random.randint(3, 5)
        cli_args = ['memory', '-l', f"{self.SECONDS}", '-g', f"{gb}", "1"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = [target_object]
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD)
        self.addTime()

    def diskAttackOnKubernetes(self, target_object):
        cli_args = ["disk", "-l", f"{self.SECONDS}", "-d", "/tmp", "-w", "1", "-b", "4", "-p", f"{self.PERCENTAGE}"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = [target_object]
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD)
        self.addTime()

    def ioAttackOnKubernetes(self, target_object):
        cli_args = ["io", "-l", f"{self.SECONDS}", "-d", "/tmp", "-w", "1", "-m", "rw", "-s", "4", "-c", "1"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = [target_object]
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD)
        self.addTime()

    def processKillAttackOnKubernetes(self, target_object):
        pod_process_name = target_object.get("name")
        cli_args = ["process_killer", "-l", f"{self.SECONDS}", "-i", "0", "-p", f"{pod_process_name}"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = [target_object]
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD)
        self.addTime()

    def shutDownKillAttackOnKubernetes(self, target_object):
        cli_args = ["shutdown", "-d", "0"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = [target_object]
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD)
        self.addTime()

    def blackHoleKillAttackOnKubernetes(self, target_object):
        cli_args = ["blackhole", "-l", f"{self.SECONDS}", "-h", "^api.gremlin.com", "-p", "^53"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["providers"] = []
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = [target_object]
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD)
        self.addTime()

    def latencyKillAttackOnKubernetes(self, target_object):
        milli_seconds = random.randint(500, 1000)
        cli_args = ["latency", "-l", f"{self.SECONDS}", "-m", f"{milli_seconds}", "-h", "^api.gremlin.com", "-p", "^53"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["providers"] = []
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = [target_object]
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD)
        self.addTime()

    def dnsKillAttackOnKubernetes(self, target_object):
        cli_args = ["dns", "-l", f"{self.SECONDS}"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["providers"] = []
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = [target_object]
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD)
        self.addTime()

    def packetLossKillAttackOnKubernetes(self, target_object):
        cli_args = ["packet_loss", "-l", f"{self.SECONDS}", "-h", "^api.gremlin.com", "-p", "^53", "-r", "1"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["providers"] = []
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = [target_object]
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD)
        self.addTime()

    def cpuAttackOnHosts(self, instance_id):
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = [instance_id]
        self.HOSTS_PAYLOAD["command"] = {
            "type": "cpu",
            "commandType": "CPU",
            "args": ["-l", f"{self.SECONDS}", "-p", f"{self.PERCENTAGE}", "-a"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD)
        self.addTime()

    def memoryAttackOnHosts(self, instance_id):
        gb = random.randint(100, 200)
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = [instance_id]
        self.HOSTS_PAYLOAD["command"] = {
            "type": "memory",
            "commandType": "Memory",
            "args": ["-l", f"{self.SECONDS}", "-g", f"{gb}"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD)
        self.addTime()

    def diskAttackOnHosts(self, instance_id):
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = [instance_id]
        self.HOSTS_PAYLOAD["command"] = {
            "type": "disk",
            "commandType": "Disk",
            "args": ["-l", f"{self.SECONDS}", "-d", "/tmp", "-w", "1", "-b", "4", "-p", f"{self.PERCENTAGE}"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD)
        self.addTime()

    def ioAttackOnHosts(self, instance_id):
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = [instance_id]
        self.HOSTS_PAYLOAD["command"] = {
            "type": "io",
            "commandType": "IO",
            "args": ["-l", f"{self.SECONDS}", "-d", "/tmp", "-w", "1", "-m", "rw", "-s", "4", "-c", "1"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD)
        self.addTime()

    def processKillAttackOnHosts(self, instance_id):
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = [instance_id]
        self.HOSTS_PAYLOAD["command"] = {
            "type": "process_killer",
            "commandType": "Process Killer",
            "args": ["-l", f"{self.SECONDS}", "-i", "0", "-p", f"{instance_id}"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD)
        self.addTime()

    def shutDownKillAttackOnHosts(self, instance_id):
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = [instance_id]
        self.HOSTS_PAYLOAD["command"] = {
            "type": "shutdown",
            "commandType": "Shutdown",
            "args": ["-d", "0", "-r"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD)
        self.addTime()

    def timeTravelKillAttackOnHosts(self, instance_id):
        time_travel_in_secs = random.randint(80000, 100000)
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = [instance_id]
        self.HOSTS_PAYLOAD["command"] = {
            "type": "time_travel",
            "commandType": "Time Travel",
            "args": ["-l", f"{self.SECONDS}", "-o", f"{time_travel_in_secs}"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD)
        self.addTime()

    def blackHoleKillAttackOnHosts(self, instance_id):
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = [instance_id]
        self.HOSTS_PAYLOAD["command"]["providers"] = []
        self.HOSTS_PAYLOAD["command"] = {
            "type": "blackhole",
            "commandType": "Blackhole",
            "args": ["-l", f"{self.SECONDS}", "-h", "^api.gremlin.com", "-p", "^53"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD)
        self.addTime()

    def latencyKillAttackOnHosts(self, instance_id):
        milli_seconds = random.randint(500, 1000)
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = [instance_id]
        self.HOSTS_PAYLOAD["command"]["providers"] = []
        self.HOSTS_PAYLOAD["command"] = {
            "type": "latency",
            "commandType": "Latency",
            "args": ["-l", f"{self.SECONDS}", "-m", f"{milli_seconds}", "-h", "^api.gremlin.com", "-p", "^53"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD)
        self.addTime()

    def dnsKillAttackOnHosts(self, instance_id):
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = [instance_id]
        self.HOSTS_PAYLOAD["command"]["providers"] = []
        self.HOSTS_PAYLOAD["command"] = {
            "type": "dns",
            "commandType": "DNS",
            "args": ["-l", f"{self.SECONDS}"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD)
        self.addTime()

    def packetLossKillAttackOnHosts(self, instance_id):
        percentage_of_packets_to_drop = random.randint(50, 70)
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = [instance_id]
        self.HOSTS_PAYLOAD["command"]["providers"] = []
        self.HOSTS_PAYLOAD["command"] = {
            "type": "packet_loss",
            "commandType": "Packet Loss",
            "args": ["-l", f"{self.SECONDS}", "-h", "^api.gremlin.com", "-p", "^53", "-r",
                     f"{percentage_of_packets_to_drop}"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD)
        self.addTime()

    def cpuAttackOnContainers(self, pod_name):
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"]["io.kubernetes.pod.name"] = [pod_name]
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "cpu",
            "commandType": "CPU",
            "args": ["-l", f"{self.SECONDS}", "-p", f"{self.PERCENTAGE}", "-a"]
        }

        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD)
        self.addTime()

    def memoryAttackOnContainers(self, pod_name):
        gb = random.randint(100, 200)
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"]["io.kubernetes.pod.name"] = [pod_name]
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "memory",
            "commandType": "Memory",
            "args": ["-l", f"{self.SECONDS}", "-g", f"{gb}"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD)
        self.addTime()

    def diskAttackOnContainers(self, pod_name):
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"]["io.kubernetes.pod.name"] = [pod_name]
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "disk",
            "commandType": "Disk",
            "args": ["-l", f"{self.SECONDS}", "-d", "/tmp", "-w", "1", "-b", "4", "-p", f"{self.PERCENTAGE}"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD)
        self.addTime()

    def ioAttackOnContainers(self, pod_name):
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"]["io.kubernetes.pod.name"] = [pod_name]
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "io",
            "commandType": "IO",
            "args": ["-l", f"{self.SECONDS}", "-d", "/tmp", "-w", "1", "-m", "rw", "-s", "4", "-c", "1"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD)
        self.addTime()

    def processKillAttackOnContainers(self, pod_name):
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"]["io.kubernetes.pod.name"] = [pod_name]
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "process_killer",
            "commandType": "Process Killer",
            "args": ["-l", f"{self.SECONDS}", "-i", "0", "-p", f"{pod_name}"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD)
        self.addTime()

    def shutDownKillAttackOnContainers(self, pod_name):
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"]["io.kubernetes.pod.name"] = [pod_name]
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "shutdown",
            "commandType": "Shutdown",
            "args": ["-d", "0", "-r"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD)
        self.addTime()

    def blackHoleKillAttackOnContainers(self, pod_name):
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"]["io.kubernetes.pod.name"] = [pod_name]
        self.CONTAINERS_PAYLOAD["command"]["providers"] = []
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "blackhole",
            "commandType": "Blackhole",
            "args": ["-l", f"{self.SECONDS}", "-h", "^api.gremlin.com", "-p", "^53"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD)
        self.addTime()

    def latencyKillAttackOnContainers(self, pod_name):
        milli_seconds = random.randint(500, 1000)
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"]["io.kubernetes.pod.name"] = [pod_name]
        self.CONTAINERS_PAYLOAD["command"]["providers"] = []
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "latency",
            "commandType": "Latency",
            "args": ["-l", f"{self.SECONDS}", "-m", f"{milli_seconds}", "-h", "^api.gremlin.com", "-p", "^53"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD)
        self.addTime()

    def dnsKillAttackOnContainers(self, pod_name):
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"]["io.kubernetes.pod.name"] = [pod_name]
        self.CONTAINERS_PAYLOAD["command"]["providers"] = []
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "dns",
            "commandType": "DNS",
            "args": ["-l", f"{self.SECONDS}"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD)
        self.addTime()

    def packetLossKillAttackOnContainers(self, pod_name):
        percentage_of_packets_to_drop = random.randint(50, 70)
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"]["io.kubernetes.pod.name"] = [pod_name]
        self.CONTAINERS_PAYLOAD["command"]["providers"] = []
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "packet_loss",
            "commandType": "Packet Loss",
            "args": ["-l", f"{self.SECONDS}", "-h", "^api.gremlin.com", "-p", "^53", "-r",
                     f"{percentage_of_packets_to_drop}"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD)
        self.addTime()


if __name__ == '__main__':
    print("This is working!")

    gremlin_obj = GremlinAttacks()
    container_targets = gremlin_obj.getAllActiveContainers()
    k8s_target = gremlin_obj.getAllAvailableKubernetesTargets()
    hosts = ["i-0ca726e746c7a0092", "i-0b14d33bee8a136c5", "i-0f80e09df9c560ce1", "i-09401e4b2cec98d8e",
             "i-0fe1ec19deb5a4e5a", "i-067318e06abc81cb8"]

    # Running Attacks on CONTAINERS:
    # if container_targets:
    #     target = container_targets[0]
    #     print(target)
    #     gremlin_obj.runAllAttacksOnContainers(target)

    # Running Attacks on KUBERNETES:
    # if k8s_target:
    #     if k8s_target["DEPLOYMENT"]:
    #         print(k8s_target["DEPLOYMENT"][0])
    #         gremlin_obj.runAllAttacksOnKubernetes(k8s_target["DEPLOYMENT"][0])
    #
    #     if k8s_target["POD"]:
    #         print(k8s_target["POD"][0])
    #         gremlin_obj.runAllAttacksOnKubernetes(k8s_target["POD"][0])
    #
    #
    # # Running Attacks on HOSTS:
    # gremlin_obj.runAllAttacksOnHost(hosts[0])