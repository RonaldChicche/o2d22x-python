import xmlrpc.client
import concurrent.futures
import socket


# This function will return the IP address of the device even when it is conncted to a VPN
def get_ip_address(refference_ip, refference_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((refference_ip, refference_port))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

class XmlRpcCameraProxy:
    def __init__(self, ip:str, port:int, timeout:float=30):
        self.user_ip = get_ip_address(ip, port)
        print(self.user_ip)
        self.url = f"http://{ip}:{port}/RPC2"
        self.stream_url = f"udp://{ip}:50002"
        socket.setdefaulttimeout(timeout)
        self.proxy = xmlrpc.client.ServerProxy(self.url)
        self.test_config = [0]

    def __getattr__(self, name):
        """
        Allows to call the methods of the proxy directly
        """
        return getattr(self.proxy, name)
    
    def __del__(self):
        self.disconnect()

    def disconnect(self):
        #           proxy.xmlDisconnect(ip_client)
        # heart_beat = self.proxy.xmlHeartbeat()
        if self.test_config[0] == 0:
            self.test_config = self.proxy.xmlTestConfig(0)
        resp = self.proxy.xmlDisconnect(self.user_ip)
        if resp[0] == 0:
            print(f"Disconnected from {self.ip}")
        else:
            print(f"Error disconnecting from {self.ip}")

    def connect(self, platform):
        resp = self.proxy.xmlConnect(self.user_ip, platform)
        if resp[0] == 0:
            print(f"Connected: {self.user_ip} -> {self.url}")
            self.id = resp[1]
            self.session = resp[2]
            self.model = resp[3]
            self.firmware_version = resp[4]
            network_params = self.get_network_parameters()
            self.ip = network_params['ip']
            self.subnet = network_params['subnet']
            self.gateway = network_params['gateway']
            self.http_port = network_params['http_port']
            self.udp_port = network_params['udp_port']
            self.mac = network_params['mac']
        else:
            print(f"Error connecting to {self.user_ip}: {resp[0]}")

    def get_compaitble_versions(self):
        resp = self.proxy.xmlGetCompatibleCPVersions()
        if resp[0] == 0:
            self.num_versions = resp[1]
            self.compatible_versions = resp[2:]
            print(f"Compatible versions: {self.compatible_versions}")
        else:
            print(f"Error getting compatible versions: {resp[0]}")
    
    def get_network_parameters(self):
        network_params = {}
        resp = self.proxy.xmlGetNetworkParameters()
        if resp[0] == 0:
            network_params['ip'] = resp[2]
            network_params['subnet'] = resp[3]
            network_params['gateway'] = resp[4]
            network_params['http_port'] = resp[5]
            network_params['udp_port'] = resp[6]
            network_params['mac'] = resp[7]
            # pcic = self.proxy.xmlGetPcicTcpConfig()
            # if pcic[0] == 0:
            #     network_params['pcic_port'] = pcic[1]
            # else:
            #     network_params['pcic_port'] = None

            self.ip = network_params['ip']
            self.subnet = network_params['subnet']
            self.gateway = network_params['gateway']
            self.http_port = network_params['http_port']
            self.udp_port = network_params['udp_port']
            self.mac = network_params['mac']
            # self.pcic_port = network_params['pcic_port']
        else:
            print(f"Error getting network parameters: {resp[0]}")  
        
        return network_params

    def init_config(self):
        resp = self.proxy.xmlGetConfigList()
        if resp[0] == 0:
            self.available_configs = resp[1]
            self.size_configs = resp[3]
            self.config_id = resp[4] # this is the only attribute that i know what is ... i thinnk
        else:
            print(f"Error getting configuration list: {resp[0]}")
        print(f'<{self.ip}> Init config: ', end='')
        self.open_config = self.proxy.xmlOpenConfiguration(self.config_id, 0)
        print(self.open_config, end='')
        self.test_config = self.proxy.xmlTestConfig(1)
        print(self.test_config)

    def detection(self):
        result = {}
        print(f'<{self.ip}> Execute detection: ', end='')
        resume_results = self.proxy.xmlResumeResults()
        print(f'Res:{resume_results}', end='')
        trigger = self.proxy.xmlExecuteTrigger()
        print(f'Trigger: {trigger}')
        poll_results = [0,0]
        while poll_results[1] == 0:
            poll_results = self.proxy.xmlPollResults()
        print(f'\tPoll: {poll_results[1]}', end=' -> ')
        config_results = self.proxy.xmlGetConfigRunResults()
        print(f'<{self.ip}> Conf Res: {config_results}')
        if config_results[1] == 0:
            raise ValueError(f"Error executing detection: {config_results[1]}")
        self.last_detection = self.proxy.xmlGetConfigInstances(1)
        if self.last_detection[0] == 0:
            # type result [0, 1, [1, 'Ak0xAw__', 260.440002, 0.959605, 335.676086, 87.168205, 0.908069, 17, 627, 455, 57, 79], 322.972]
            result['result'] = self.last_detection[2][0]
            result['id_app'] = self.last_detection[2][1]
            result['cal_time'] = self.last_detection[2][2]
            result['orientation'] = self.last_detection[2][3]
            result['x'] = self.last_detection[2][4]
            result['y'] = self.last_detection[2][5]
            result['confidence'] = self.last_detection[2][6]
            result['error'] = 0
            return result
        else:
            raise ValueError(f"Error getting results: {self.last_detection[0]}")


    def execute_detection(self, tries=3):
        while tries > 0:
            try:
                result = self.detection()
                print(result)
                return result
            except socket.timeout:
                tries -= 1
                print("Timeout, trying again...")
            except ValueError as e:
                print(e)
                tries -= 1
                print("ValueError, trying again...")
        
        result = {}
        result['error'] = 1
        print(result)
        return result
        

class XmlRpcProxyManager:
    def __init__(self, ip_list, port, platform="3.5.0061"):
        self.platform = platform
        self.proxies = [XmlRpcCameraProxy(ip, port) for ip in ip_list]

    def __getitem__(self, index):
        """
        Returns the proxy at the given index
        proxy = proxy_manager[0] 
        """
        return self.proxies[index]

    def __len__(self):
        """
        Returns the number of proxies
        len(proxy_manager)
        """
        return len(self.proxies)
    
    def __iter__(self):
        """
        Returns an iterator over the proxies
        for proxy in proxy_manager:
            print(proxy)
        """
        return iter(self.proxies)
    
    def connect(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.proxies)) as executor:
            futures = [executor.submit(proxy.connect, self.platform) for proxy in self.proxies]
            results = [future.result() for future in futures]
            print(results)    
    
    def disconnect(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.proxies)) as executor:
            futures = [executor.submit(proxy.disconnect) for proxy in self.proxies]
            results = [future.result() for future in futures]
        return results

    def get_compaitble_versions(self):
        for proxy in self.proxies:
            proxy.get_compaitble_versions()

    def init_config(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.proxies)) as executor:
            futures = [executor.submit(proxy.init_config) for proxy in self.proxies]
            results = [future.result() for future in futures]
        return results

    def execute_detection(self, tries=3):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.proxies)) as executor:
            futures = [executor.submit(proxy.execute_detection) for proxy in self.proxies]
            print(futures)
            results = []
            for future in futures:
                try:
                    print(future)
                    result = future.result()
                except Exception as e:
                    result = None
                    print(f"Error: {e}")
                results.append(result)
        return results
    

