import gc
import network
import utime as time
import usocket as socket
import ure
import ujson

gc.enable()

class DNSQuery:
    def __init__(self, data):
        self.data = data
        self.domain = ''

        m = data[2]
        tipo = (m >> 3) & 15
        if tipo == 0:
            ini = 12
            lon = data[ini]
            while lon != 0:
                self.domain += data[ini+1:ini+lon+1].decode("utf-8") + "."
                ini += lon+1
                lon = data[ini]

    def response(self, ip):
        packet = b''
        print("Response {} == {}".format(self.domain, ip))
        if self.domain:
            packet += self.data[:2] + b"\x81\x80"
            packet += self.data[4:6] + b"\x00\x00\x00\x00"
            packet += self.data[12:]
            packet += b"\xc0\x0c"
            packet += b"\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04"
            packet += bytes(map(int, ip.split(".")))
        return packet


class CaptivePortal:
    """ CaptivePortal
    First check to see if there is an existing config, if there is then try to connect to the wifi in there.
    If there isn't, or we can't connect, create a captive portal, send index.html to connections,
    try to connect to the network they specify and save the config
    This can be expanded to allow configuration of other stuff... (search for "Modify" below)
    Modify the html file to include the fields, modify the regex which parses their form submittal so that
    it includes these fields, modify the areas of code that save the config"""

    def __init__(self, essid_name):
        self.essid_name = essid_name

    def captive_portal(self):
        existing_config = False
        try:
            with open("wifi.json", "r") as f:
                configs = f.read()
                j = ujson.loads(configs)
                print(j)
            con = self.connection(j['network_name'], j['network_password'])
            if con is True:
                existing_config = True
                print("Network connected")
            else:
                existing_config = False
                print("Incorrect network configuration")
        except:
            print("No saved network")

        if existing_config is False:
            ap = network.WLAN(network.AP_IF)
            ap.active(True)
            ap.config(essid=self.essid_name, authmode=1)
            ip = ap.ifconfig()[0]
            print("DNS Server: dom.query. 60 in A {:s}".format(ip))

            udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udps.setblocking(False)
            udps.bind(('', 53))

            s = socket.socket()
            ai = socket.getaddrinfo(ip, 80)
            print("Web Server: Bind address information: ", ai)
            addr = ai[0][-1]

            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(addr)
            s.listen(1)
            s.settimeout(2)
            print("Web Server: Listening http://{}:80/".format(ip))

            # Modify this to match the form response that you are expecting
            regex = ure.compile("network\?ssid=(.*?)&password=(.*?)\sHTTP")

            set_connection = False
            while set_connection is False:
                try:
                    data, addr = udps.recvfrom(4096)
                    print("Incoming data...")
                    dns = DNSQuery(data)
                    udps.sendto(dns.response(ip), addr)
                    print("Replying: {:s} -> {:s}".format(dns.domain, ip))
                except:
                    print("No DNS")

                try:
                    res = s.accept()
                    client_sock = res[0]
                    client_addr = res[1]

                    req = client_sock.recv(4096)
                    print("Client:", client_addr)
                    print("Request:")
                    print(req)
                    with open('index.html', 'r') as content:
                        client_sock.send(content.read())
                        client_sock.close()
                    print()
                    search_result = regex.search(req)
                    if search_result:  # Modify these to match the form responses you are expecting
                        incoming_network_name = search_result.group(1)
                        incoming_network_pass = search_result.group(2)
                        con = self.connection(incoming_network_name, incoming_network_pass)
                        if con is True:  # Modify this to match the config you are writing out
                            d = {"network_name": incoming_network_name,
                                 "network_password": incoming_network_pass}
                            with open("wifi.json", "w") as f:
                                f.write(ujson.dumps(d))
                            set_connection = True

                except:
                    print("Timeout")
                time.sleep_ms(1000)
            udps.close()
            ap.active(False)

    def connection(self, network_name, network_password):
        attempts = 0
        station = network.WLAN(network.STA_IF)
        if not station.isconnected():
            print("Connecting to network...")
            station.active(True)
            station.connect(network_name, network_password)
            while not station.isconnected():
                print("Attempts: {}".format(attempts))
                attempts += 1
                time.sleep(5)
                if attempts > 3:
                    return False
        print('Network Config:', station.ifconfig())
        return True
