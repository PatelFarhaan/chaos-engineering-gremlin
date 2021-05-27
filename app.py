import os
import yaml
import json
import requests
from decimal import Decimal


class RequestLimit(object):
    def __init__(self):
        self.result = {}
        self.duration = "7d"
        self.deployment_names = {}
        self.github_repo_path = "../../env_repo/"
        self.container_service_mapping_updated = {}
        self.ignore_contianers = ["POD", "vault-agent"]
        self.github_config_filename = "configuration.yaml"
        self.common_json = json.load(open("../../env_repo/deployment/common.json"))
        self.thanos_url = self.common_json["monitoring"]["thanos"]
        cluster = [ v.get("cluster") for k,v in self.common_json.items() if k == "landscape" ][0]
        self.namespaces = ["***REMOVED_K8S_NAMESPACE***", "***REMOVED_K8S_NAMESPACE***"]
        self.container_service_mapping = json.load(open("../../ccgf_repo/platform-deployment-config/container-service-mapping.json"))
        self.ignore_services = ["ccgf-ingestion-processor", "ccgf-bulkfile-processor", "ccgf-audit-processor", "ccgf-notification-processor"]

        if cluster.startswith("aws-"):
            self.cluster = cluster[4:]
        else:
            self.cluster = cluster

    def base_schema(self):
        return {
            "request_count": {
                "cpu": None,
                "memory": None
            },
            "proxy_count": {
                "cpu": None,
                "memory": None
            }
        }

    def get_avg_cpu_of_service_per_namespace(self, namespace):
        query = f"""
        avg by (container) 
        (rate (container_cpu_usage_seconds_total{{
        cluster_name="{self.cluster}", 
        namespace="{namespace}",
        container!="istio-proxy"}}
        [{self.duration}]))
        """
        url = f"{self.thanos_url}/api/v1/query?query={query}"
        payload = {}
        headers = {}
        response = requests.get(url, headers=headers, data=payload)
        response = response.json()

        for i in response["data"]["result"]:
            container = i.get("metric").get("container")
            if container and container not in self.ignore_contianers:
                cpu = float(i.get("value")[1])
                cpu = cpu if cpu >= 0.010 else 0.010
                float_cpu = float(f"{Decimal(f'{cpu:.2g}'):f}") * 1000
                self.result[container] = self.base_schema()
                self.result[container]["request_count"]["cpu"] = f"{float_cpu}m"

    def get_avg_mem_of_service_per_namespace(self, namespace):
        query = f"""
         avg by (container) 
         (avg_over_time(container_memory_working_set_bytes{{
         container!="istio-proxy",
         cluster_name="{self.cluster}", 
         namespace="{namespace}"}}
         [{self.duration}]))
        """
        url = f"{self.thanos_url}/api/v1/query?query={query}"
        payload = {}
        headers = {}
        response = requests.get(url, headers=headers, data=payload)
        response = response.json()

        for i in response["data"]["result"]:
            if not i.get("metric").get("container") in self.result:
                continue
            elif i.get("metric").get("container") in self.result:
                self.result[i.get("metric").get("container")]["request_count"][
                    "memory"] = f'{round(float(i.get("value")[1]) * 9.5367431640625e-7)}' + "Mi"
            else:
                self.result[i.get("metric").get("container")] = self.base_schema()
                self.result[i.get("metric").get("container")]["request_count"][
                    "memory"] = f'{round(float(i.get("value")[1]) * 9.5367431640625e-7)}' + "Mi"

    def get_avg_cpu_of_istio_proxy_per_namespace(self, namespace):
        for pod_name in self.result:
            query = f"""
                         avg (rate (container_cpu_usage_seconds_total
                         {{
                             image!="", 
                             namespace="{namespace}", 
                             pod=~"{pod_name}.*",
                             container="istio-proxy", 
                             cluster_name="{self.cluster}" 
                         }}
                            [{self.duration}]))
                    """
            url = f"{self.thanos_url}/api/v1/query?query={query}"
            payload = {}
            headers = {}
            response = requests.get(url, headers=headers, data=payload)
            response = response.json()
            for i in response["data"]["result"]:
                if i.get("value"):
                    cpu = float(i.get("value")[1])
                    cpu = cpu if cpu >= 0.010 else 0.010
                    float_cpu = float(f"{Decimal(f'{cpu:.2g}'):f}") * 1000
                    self.result[pod_name]["proxy_count"][
                        "cpu"] = f"{float_cpu}m"

    def get_avg_mem_of_istio_proxy_per_namespace(self, namespace):
        for pod_name in self.result:
            query = f"""
                     avg by (container) 
                     (avg_over_time(container_memory_working_set_bytes
                     {{
                            namespace="{namespace}", 
                            pod=~"{pod_name}.*", 
                            container="istio-proxy",
                            cluster_name="{self.cluster}" 
                    }}
                        [{self.duration}]))
                    """
            url = f"{self.thanos_url}/api/v1/query?query={query}"
            payload = {}
            headers = {}
            response = requests.get(url, headers=headers, data=payload)
            response = response.json()

            for i in response["data"]["result"]:
                if i.get("value"):
                    self.result[pod_name]["proxy_count"][
                        "memory"] = f'{round(float(i.get("value")[1]) * 9.5367431640625e-7)}' + "Mi"

    def get_deployment_names_per_namespace(self, namespace):
        self.deployment_names = {}
        query = f"""
                kube_deployment_labels{{
                cluster_name="***REMOVED_K8S_CLUSTER***", namespace="{namespace}"
                }}
                """
        url = f"{self.thanos_url}/api/v1/query?query={query}"
        response = requests.get(url=url, headers={}, data={})
        resp = response.json()
        for i in resp["data"]["result"]:
            metric = i.get("metric")
            deployment_name = metric.get("deployment")
            label = metric.get("label_app")
            if not "gateway" in label:
                self.deployment_names[label] = deployment_name

    def write_results_to_github_repo(self, config_file, content):
        with open(config_file, "w") as file_write:
            yaml.dump(content, file_write, sort_keys=True)
        file_write.close()

    def filter_file_results(self, service_cpu_req, service_mem_req, proxy_cpu_req, proxy_mem_req):
        result = {}
        result_hm = {}

        temp_hm = {
            "requests": {
                "cpu" if service_cpu_req else None: service_cpu_req,
                "memory" if service_mem_req else None: service_mem_req
            },
            "proxy": {
                "cpu" if proxy_cpu_req else None: proxy_cpu_req,
                "memory" if proxy_mem_req else None: proxy_mem_req
            }
        }

        keys = ["requests", "proxy"]
        for key in keys:
            result_hm[key] = {}
            for k, v in temp_hm[key].items():
                if k:
                    result_hm[key][k] = v
        for key in keys:
            if result_hm[key]:
                result[key] = result_hm[key]
        return result

    def filter_patch_results(self, service_cpu_req, service_mem_req, proxy_cpu_req, proxy_mem_req):
        result = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "sidecar.istio.io/proxyCPU": proxy_cpu_req,
                            "sidecar.istio.io/proxyMemory": proxy_mem_req
                        }
                    },
                    "spec": {
                        "containers": {
                            "resources": {
                                "requests": {
                                    "cpu": service_cpu_req,
                                    "memory": service_mem_req
                                }
                            }
                        }
                    }
                }
            }
        }

        for k,v in result["spec"]["template"]["metadata"]["annotations"].items():
            if not v:
                result["spec"]["template"]["metadata"]["annotations"].pop(k)

        for k,v in result["spec"]["template"]["spec"]["containers"]["resources"]["requests"].items():
            if not v:
                result["spec"]["template"]["metadata"]["annotations"].pop(k)
        return result

    def patch_deployment_files(self):
        for container, container_details in self.result.items():
            deployment_name = self.deployment_names.get(container)
            service_name = self.container_service_mapping.get(container)

            if service_name and deployment_name:
                config_file = f"{self.github_repo_path}{service_name}/{self.github_config_filename}"
                if not os.path.isfile(config_file) or service_name in self.ignore_services:
                    continue

                content = yaml.full_load(open(config_file))
                proxy_cpu_req = self.result.get(container).get("proxy_count").get("cpu")
                proxy_mem_req = self.result.get(container).get("proxy_count").get("memory")
                service_cpu_req = self.result.get(container).get("request_count").get("cpu")
                service_mem_req = self.result.get(container).get("request_count").get("memory")

                result = self.filter_file_results(service_cpu_req, service_mem_req, proxy_cpu_req, proxy_mem_req)
                content["service"]["resources"] = result

                if not result:
                    content["service"].pop("resources")
                    continue

                # comment this line to include proxy values: todo
                # content["service"]["resources"].pop("proxy")

                if service_name in ["ccgf-logger", "ccgf-search"]:
                    self.write_results_to_github_repo(config_file, content)

                patch_content = self.filter_patch_results(service_cpu_req, service_mem_req, proxy_cpu_req, proxy_mem_req)
                _temp_str = str(patch_content).replace("'", '"')
                str_content = f"'{_temp_str}'"

                if container in ("cms", "tms"):
                    query = f"kubectl patch deployment {deployment_name} --patch {str_content} -n ***REMOVED_K8S_NAMESPACE***"
                else:
                    query = f"kubectl patch deployment {deployment_name} --patch {str_content} -n ***REMOVED_K8S_NAMESPACE***"
                print(query, "\n")

    def driver_function(self):
        for namespace in self.namespaces:
            self.result = {}
            self.get_deployment_names_per_namespace(namespace)
            self.get_avg_cpu_of_service_per_namespace(namespace)
            self.get_avg_mem_of_service_per_namespace(namespace)
            self.get_avg_cpu_of_istio_proxy_per_namespace(namespace)
            self.get_avg_mem_of_istio_proxy_per_namespace(namespace)
            self.patch_deployment_files()


if __name__ == '__main__':
    obj = RequestLimit()
    obj.driver_function()