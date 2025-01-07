import json
import re
import requests

from kubernetes import client, config

class registerError(Exception):
    def __init__(self, message, status_code):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.status_code = status_code

class register_RestApi():
    def __init__( self, config_file, username, password ):
        self.config_file = config_file
        self.username = username
        self.password = password
        config.load_kube_config()
        self.v1 = client.CoreV1Api()

        appmgr_ip = self.get_pod_ips( "ricplt", "deployment-ricplt-appmgr")
        url = f"http://{appmgr_ip}:8085/ric/v1/root/generateToken"
        params = {
            "username"  : username,
            "password"  : password,
            "api"       : "post",
            "apiObject" : "appmgr",
            "apiPath"   : "/ric/v1/root/addUser"
        }
        response = requests.get( url = url, params = params )
        if response.status_code == 200:
            self.token = response.json().get( "access_token" )
        elif response.status_code == 403:
            raise registerError( "failed to get token, access forbidden", 403 )
        else:
            raise registerError( "failed to get token", response.status_code )
        
        url = f"http://{appmgr_ip}:8085/ric/v1/root/addUser"
        raise registerError( "end", 400 )

    def get_pod_ips( self, namespace, pod_name ):
        try:
            pods = self.v1.list_pod_for_all_namespaces()
            for pod in pods.items:
                print(f"Namespace: {pod.metadata.namespace}, Pod Name: {pod.metadata.name}, Status: {pod.status.phase}")
                if pod.metadata.namespace == namespace and pod.status.phase.lower() == "running" and re.search( fr"{pod_name}", pod.metadata.name, re.IGNORECASE ):
                    return pod.status.pod_ip
        except client.exceptions.ApiException as e:
            print(f"Error fetching Pod IPs: {e}")
            return ""