import os
import json
import time
import random
import logging
import requests
from datetime import datetime


class GremlinAttacks(object):
    def __init__(self):
        self.ATTACKS = ["DEPLOYMENT", "POD"]
        self.SECONDS = random.randint(60, 120)
        self.PERCENTAGE = random.randint(90, 100)
        self.NAMESPACE = "intcloud-qastaging-ccgf"
        self.SERVICES = ["ccgf-model", "ccgf-search"]
        self.CLUSTER = "intcloud-ccgf-eks-devci-usw2"
        self.TEAM_ID = "97ae1e3d-9433-552c-8adf-eba9567e7fe5"
        self.DT_STAMP = datetime.utcnow().strftime("%d %b %Y")
        self.HOSTS_URL = "https://api.gremlin.com/v1/attacks/new?teamId={}".format(self.TEAM_ID)
        self.API_KEY = "***REMOVED_GREMLIN_API_KEY***"
        self.KUBERNETS_URL = "https://api.gremlin.com/v1/kubernetes/attacks/new?teamId={}".format(self.TEAM_ID)

        dts = datetime.utcnow().strftime("%d-%m-%Y")
        logging.basicConfig(filemode='a',
                            level=logging.DEBUG,
                            datefmt='%m-%d-%Y %H:%M:%S',
                            filename="{}/{}.log".format(os.getcwd(), dts),
                            format="[%(asctime)s] %(levelname)s: %(message)s")
        self.LOGGER = logging.getLogger(__name__)

        self.HEADERS = {
            "Content-Type": "application/json;charset=utf-8",
            "Authorization": "Key {}".format(self.API_KEY)
        }

        self.RESULTS = {
            "hosts": {
                "process_kill": []
            },
            "containers": {
                "process_kill": []
            },
            "kubernetes": {
                "process_kill": []
            }
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
                        "io.kubernetes.container.name": []
                    }
                },
                "percent": 100
            },
            "command": {}
        }

    def addTime(self, is_process_killer=False):
        if is_process_killer:
            time.sleep(5)
        else:
            time.sleep(self.SECONDS + 20)

    def runAllAttacksOnContainers(self, target_name):
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

    def runAllAttacksOnKubernetes(self, target_name):
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

    def runAllAttacksOnHost(self, target_name):
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
            result = set()
            data = response.json()
            for object in data:
                if object.get("container_labels"):
                    if object["container_labels"].get("io.kubernetes.pod.namespace"):
                        if object["container_labels"]["io.kubernetes.pod.namespace"] == self.NAMESPACE:
                            pod_name = object["container_labels"]["io.kubernetes.pod.name"]
                            container_name = object["container_labels"]["io.kubernetes.container.name"]
                            if pod_name:
                                for service in self.SERVICES:
                                    if service in pod_name:
                                        result.add(container_name)
            return list(result)
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

    def postAPIRequest(self, url, headers, payload, target, attack, cli_args, is_process_killer=False):
        print("{}: {} attack: {} \n".format(target, attack.upper(), cli_args))
        response = requests.post(url=url,
                                 headers=headers,
                                 data=json.dumps(payload))
        attack_id = response.text

        if is_process_killer:
            self.RESULTS[target]["process_kill"].append(attack_id)
        else:
            self.RESULTS[target][attack] = attack_id

        self.LOGGER.info("{} attack: {}: {} \n".format(attack.upper(), cli_args, attack_id))

        if response.status_code != 402:
            self.addTime(is_process_killer)

    def cpuAttackOnKubernetes(self, at: list):
        cli_args = ["cpu", "-l", "{}".format(self.SECONDS), "-c", "1", "-p", "{}".format(self.PERCENTAGE)]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = target_object
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD, "kubernetes", "cpu",
                            cli_args)

    def memoryAttackOnKubernetes(self, target_object: list):
        gb = random.randint(3, 5)
        cli_args = ['memory', '-l', "{}".format(self.SECONDS), '-g', "{}".format(gb), "1"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = target_object
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD, "kubernetes", "memory",
                            cli_args)

    def diskAttackOnKubernetes(self, target_object: list):
        cli_args = ["disk", "-l", "{}".format(self.SECONDS), "-d", "/tmp", "-w", "1", "-b", "4", "-p",
                    "{}".format(self.PERCENTAGE)]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = target_object
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD, "kubernetes", "disk",
                            cli_args)

    def ioAttackOnKubernetes(self, target_object: list):
        cli_args = ["io", "-l", "{}".format(self.SECONDS), "-d", "/tmp", "-w", "1", "-m", "rw", "-s", "4", "-c", "1"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = target_object
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD, "kubernetes", "io",
                            cli_args)

    def processKillAttackOnKubernetes(self, target_object: list):
        for object in target_object:
            cli_args = ["process_killer", "-l", "{}".format(self.SECONDS), "-i", "0", "-p", "{}".format(object)]
            self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
            self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = target_object
            self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD, "kubernetes", "process_kill",
                                cli_args, is_process_killer=True)

    def shutDownKillAttackOnKubernetes(self, target_object: list):
        cli_args = ["shutdown", "-d", "0"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = target_object
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD, "kubernetes", "shutdown",
                            cli_args)

    def blackHoleKillAttackOnKubernetes(self, target_object: list):
        cli_args = ["blackhole", "-l", "{}".format(self.SECONDS), "-h", "^api.gremlin.com", "-p", "^53"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["providers"] = []
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = target_object
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD, "kubernetes", "blackhole",
                            cli_args)

    def latencyKillAttackOnKubernetes(self, target_object: list):
        milli_seconds = random.randint(500, 1000)
        cli_args = ["latency", "-l", "{}".format(self.SECONDS), "-m", "{}".format(milli_seconds), "-h",
                    "^api.gremlin.com", "-p", "^53"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["providers"] = []
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = target_object
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD, "kubernetes", "latency",
                            cli_args)

    def dnsKillAttackOnKubernetes(self, target_object: list):
        cli_args = ["dns", "-l", "{}".format(self.SECONDS)]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["providers"] = []
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = target_object
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD, "kubernetes", "dns",
                            cli_args)

    def packetLossKillAttackOnKubernetes(self, target_object: list):
        cli_args = ["packet_loss", "-l", "{}".format(self.SECONDS), "-h", "^api.gremlin.com", "-p", "^53", "-r", "1"]
        self.KUBERNETES_PAYLOAD["impactDefinition"]["providers"] = []
        self.KUBERNETES_PAYLOAD["impactDefinition"]["cliArgs"] = cli_args
        self.KUBERNETES_PAYLOAD["targetDefinition"]["strategy"]["k8sObjects"] = target_object
        self.postAPIRequest(self.KUBERNETS_URL, self.HEADERS, self.KUBERNETES_PAYLOAD, "kubernetes", "packet_loss",
                            cli_args)

    def cpuAttackOnHosts(self, instances):
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = instances
        self.HOSTS_PAYLOAD["command"] = {
            "type": "cpu",
            "commandType": "CPU",
            "args": ["-l", "{}".format(self.SECONDS), "-p", "{}".format(self.PERCENTAGE), "-a"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD, "hosts", "cpu",
                            self.HOSTS_PAYLOAD["command"]["args"])

    def memoryAttackOnHosts(self, instances):
        gb = random.randint(100, 200)
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = instances
        self.HOSTS_PAYLOAD["command"] = {
            "type": "memory",
            "commandType": "Memory",
            "args": ["-l", "{}".format(self.SECONDS), "-g", "{}".format(gb)]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD, "hosts", "memory",
                            self.HOSTS_PAYLOAD["command"]["args"])

    def diskAttackOnHosts(self, instances):
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = instances
        self.HOSTS_PAYLOAD["command"] = {
            "type": "disk",
            "commandType": "Disk",
            "args": ["-l", "{}".format(self.SECONDS), "-d", "/tmp", "-w", "1", "-b", "4", "-p",
                     "{}".format(self.PERCENTAGE)]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD, "hosts", "disk",
                            self.HOSTS_PAYLOAD["command"]["args"])

    def ioAttackOnHosts(self, instances):
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = instances
        self.HOSTS_PAYLOAD["command"] = {
            "type": "io",
            "commandType": "IO",
            "args": ["-l", "{}".format(self.SECONDS), "-d", "/tmp", "-w", "1", "-m", "rw", "-s", "4", "-c", "1"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD, "hosts", "io",
                            self.HOSTS_PAYLOAD["command"]["args"])

    def processKillAttackOnHosts(self, instances):
        for instance in instances:
            self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = [instance]
            self.HOSTS_PAYLOAD["command"] = {
                "type": "process_killer",
                "commandType": "Process Killer",
                "args": ["-l", "{}".format(self.SECONDS), "-i", "0", "-p", "{}".format(instance)]
            }
            self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD, "hosts", "process_kill",
                                self.HOSTS_PAYLOAD["command"]["args"], is_process_killer=True)

    def shutDownKillAttackOnHosts(self, instances):
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = instances
        self.HOSTS_PAYLOAD["command"] = {
            "type": "shutdown",
            "commandType": "Shutdown",
            "args": ["-d", "0", "-r"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD, "hosts", "shutdown",
                            self.HOSTS_PAYLOAD["command"]["args"])

    def timeTravelKillAttackOnHosts(self, instances):
        time_travel_in_secs = random.randint(80000, 100000)
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = instances
        self.HOSTS_PAYLOAD["command"] = {
            "type": "time_travel",
            "commandType": "Time Travel",
            "args": ["-l", "{}".format(self.SECONDS), "-o", "{}".format(time_travel_in_secs)]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD, "hosts", "time_travel",
                            self.HOSTS_PAYLOAD["command"]["args"])

    def blackHoleKillAttackOnHosts(self, instances):
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = instances
        self.HOSTS_PAYLOAD["command"]["providers"] = []
        self.HOSTS_PAYLOAD["command"] = {
            "type": "blackhole",
            "commandType": "Blackhole",
            "args": ["-l", "{}".format(self.SECONDS), "-h", "^api.gremlin.com", "-p", "^53"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD, "hosts", "blackhole",
                            self.HOSTS_PAYLOAD["command"]["args"])

    def latencyKillAttackOnHosts(self, instances):
        milli_seconds = random.randint(500, 1000)
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = instances
        self.HOSTS_PAYLOAD["command"]["providers"] = []
        self.HOSTS_PAYLOAD["command"] = {
            "type": "latency",
            "commandType": "Latency",
            "args": ["-l", "{}".format(self.SECONDS), "-m", "{}".format(milli_seconds), "-h", "^api.gremlin.com", "-p",
                     "^53"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD, "hosts", "latency",
                            self.HOSTS_PAYLOAD["command"]["args"])

    def dnsKillAttackOnHosts(self, instances):
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = instances
        self.HOSTS_PAYLOAD["command"]["providers"] = []
        self.HOSTS_PAYLOAD["command"] = {
            "type": "dns",
            "commandType": "DNS",
            "args": ["-l", "{}".format(self.SECONDS)]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD, "hosts", "dns",
                            self.HOSTS_PAYLOAD["command"]["args"])

    def packetLossKillAttackOnHosts(self, instances):
        percentage_of_packets_to_drop = random.randint(50, 70)
        self.HOSTS_PAYLOAD["target"]["hosts"]["multiSelectTags"]["instance-id"] = instances
        self.HOSTS_PAYLOAD["command"]["providers"] = []
        self.HOSTS_PAYLOAD["command"] = {
            "type": "packet_loss",
            "commandType": "Packet Loss",
            "args": ["-l", "{}".format(self.SECONDS), "-h", "^api.gremlin.com", "-p", "^53", "-r",
                     "{}".format(percentage_of_packets_to_drop)]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.HOSTS_PAYLOAD, "hosts", "packet_loss",
                            self.HOSTS_PAYLOAD["command"]["args"])

    def cpuAttackOnContainers(self, containers: list):
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"][
            "io.kubernetes.container.name"] = containers
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "cpu",
            "commandType": "CPU",
            "args": ["-l", "{}".format(self.SECONDS), "-p", "{}".format(self.PERCENTAGE), "-a"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD, "containers", "cpu",
                            self.CONTAINERS_PAYLOAD["command"]["args"])

    def memoryAttackOnContainers(self, containers: list):
        gb = random.randint(100, 200)
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"][
            "io.kubernetes.container.name"] = containers
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "memory",
            "commandType": "Memory",
            "args": ["-l", "{}".format(self.SECONDS), "-g", "{}".format(gb)]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD, "containers", "memory",
                            self.CONTAINERS_PAYLOAD["command"]["args"])

    def diskAttackOnContainers(self, containers: list):
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"][
            "io.kubernetes.container.name"] = containers
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "disk",
            "commandType": "Disk",
            "args": ["-l", "{}".format(self.SECONDS), "-d", "/tmp", "-w", "1", "-b", "4", "-p",
                     "{}".format(self.PERCENTAGE)]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD, "containers", "disk",
                            self.CONTAINERS_PAYLOAD["command"]["args"])

    def ioAttackOnContainers(self, containers: list):
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"][
            "io.kubernetes.container.name"] = containers
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "io",
            "commandType": "IO",
            "args": ["-l", "{}".format(self.SECONDS), "-d", "/tmp", "-w", "1", "-m", "rw", "-s", "4", "-c", "1"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD, "containers", "io",
                            self.CONTAINERS_PAYLOAD["command"]["args"])

    def processKillAttackOnContainers(self, containers: list):
        for container in containers:
            self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"]["io.kubernetes.container.name"] = [
                container]
            self.CONTAINERS_PAYLOAD["command"] = {
                "type": "process_killer",
                "commandType": "Process Killer",
                "args": ["-l", "{}".format(self.SECONDS), "-i", "0", "-p", "{}".format(container)]
            }
            self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD, "containers", "process_kill",
                                self.CONTAINERS_PAYLOAD["command"]["args"], is_process_killer=True)

    def shutDownKillAttackOnContainers(self, containers: list):
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"][
            "io.kubernetes.container.name"] = containers
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "shutdown",
            "commandType": "Shutdown",
            "args": ["-d", "0", "-r"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD, "containers", "shutdown",
                            self.CONTAINERS_PAYLOAD["command"]["args"])

    def blackHoleKillAttackOnContainers(self, containers: list):
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"][
            "io.kubernetes.container.name"] = containers
        self.CONTAINERS_PAYLOAD["command"]["providers"] = []
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "blackhole",
            "commandType": "Blackhole",
            "args": ["-l", "{}".format(self.SECONDS), "-h", "^api.gremlin.com", "-p", "^53"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD, "containers", "blackhole",
                            self.CONTAINERS_PAYLOAD["command"]["args"])

    def latencyKillAttackOnContainers(self, containers: list):
        milli_seconds = random.randint(500, 1000)
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"][
            "io.kubernetes.container.name"] = containers
        self.CONTAINERS_PAYLOAD["command"]["providers"] = []
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "latency",
            "commandType": "Latency",
            "args": ["-l", "{}".format(self.SECONDS), "-m", "{}".format(milli_seconds), "-h", "^api.gremlin.com", "-p",
                     "^53"]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD, "containers", "latency",
                            self.CONTAINERS_PAYLOAD["command"]["args"])

    def dnsKillAttackOnContainers(self, containers: list):
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"][
            "io.kubernetes.container.name"] = containers
        self.CONTAINERS_PAYLOAD["command"]["providers"] = []
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "dns",
            "commandType": "DNS",
            "args": ["-l", "{}".format(self.SECONDS)]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD, "containers", "dns",
                            self.CONTAINERS_PAYLOAD["command"]["args"])

    def packetLossKillAttackOnContainers(self, containers: list):
        percentage_of_packets_to_drop = random.randint(50, 70)
        self.CONTAINERS_PAYLOAD["target"]["containers"]["multiSelectLabels"][
            "io.kubernetes.container.name"] = containers
        self.CONTAINERS_PAYLOAD["command"]["providers"] = []
        self.CONTAINERS_PAYLOAD["command"] = {
            "type": "packet_loss",
            "commandType": "Packet Loss",
            "args": ["-l", "{}".format(self.SECONDS), "-h", "^api.gremlin.com", "-p", "^53", "-r",
                     "{}".format(percentage_of_packets_to_drop)]
        }
        self.postAPIRequest(self.HOSTS_URL, self.HEADERS, self.CONTAINERS_PAYLOAD, "containers", "packet_loss",
                            self.CONTAINERS_PAYLOAD["command"]["args"])


if __name__ == '__main__':
    gremlin_obj = GremlinAttacks()
    gremlin_obj.LOGGER.info("attack object created \n")

    # container_targets = gremlin_obj.getAllActiveContainers()
    # gremlin_obj.LOGGER.info("retrieved all active containers: {} \n".format(container_targets))

    k8s_target = gremlin_obj.getAllAvailableKubernetesTargets()
    gremlin_obj.LOGGER.info("retrieved all active kubernetes targets {} \n".format(k8s_target))

    # hosts = ["i-0ca726e746c7a0092", "i-0b14d33bee8a136c5", "i-0f80e09df9c560ce1", "i-09401e4b2cec98d8e",
    #          "i-0fe1ec19deb5a4e5a", "i-067318e06abc81cb8"]
    # gremlin_obj.LOGGER.info("all active hosts: {} \n".format(hosts))

    #  Running Attacks on CONTAINERS:
    # if container_targets:
    #     print("Starting Container Attacks")
    #     gremlin_obj.LOGGER.info("Starting Container Attack \n")
    #     gremlin_obj.runAllAttacksOnContainers(container_targets)

    #  Running Attacks on KUBERNETES:
    if k8s_target:
        if k8s_target["DEPLOYMENT"]:
            print("Starting Deployment Attacks \n")
            gremlin_obj.LOGGER.info("Starting Deployment Attacks \n")
            gremlin_obj.runAllAttacksOnKubernetes(k8s_target["DEPLOYMENT"])

    if k8s_target["POD"]:
        print("Starting POD Attacks \n")
        gremlin_obj.LOGGER.info("Starting POD Attacks \n")
        gremlin_obj.runAllAttacksOnKubernetes(k8s_target["POD"])

    #  Running Attacks on HOSTS:
    # print("Running Host Attacks \n")
    # gremlin_obj.LOGGER.info("Running Host Attacks \n")
    # gremlin_obj.runAllAttacksOnHost(hosts)