"""
This is part of the Release Contorll project. This is taking the time the magnet should be activated from the iOS App and sends it to the Release Device. The idea is, that the iPhone can be within reach while the elecro magnet can not be influenced by that since the proxy is not in reach.

TODO: Add sensors that disable the electro magnet in certain events like a car driving in or a door opening
TODO: Add an optional emergency code to diable the electro magnet before the timer runs
TODO: Maybe add an hmac check so no one else can use this proxy
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from time import sleep
import urllib.parse
import requests
from threading import Timer


hostName = "" # Use "" to listen on all interfaces
hostPort = 6969


class ElectroMagnet:
    def __init__(self, ip=None):
        self.ip = ip

    def _resendContinueMessageToReleaseDevice(self):
        url = "http://"+self.ip+"/SetActiveForSeconds=30"
        print(url)
        print("Resending continue message")
        _ = requests.get(url)

    def _sendReleaseMessageToReleaseDevice(self):
        url = "http://"+self.ip+"/SetState=OFF"
        _ = requests.get(url)

    def activate(self, seconds):
        self._resendContinueMessageToReleaseDevice()

        tick = 0
        resendActivationMessageTimeout = 0
        while 1:
            tick += 1
            resendActivationMessageTimeout += 1
            
            print(str(tick)+" ticks of "+str(seconds))

            if seconds <= tick:
                print("Send release message to release device")
                self._sendReleaseMessageToReleaseDevice()
                break

            if resendActivationMessageTimeout >= 15:
                print("Resendingcontinue message to release device")
                resendActivationMessageTimeout = 0
                self._resendContinueMessageToReleaseDevice()

            sleep(1)


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Title goes here.</title></head>", "utf-8"))
        self.wfile.write(bytes("<body><p>This is a test.</p>", "utf-8"))
        self.wfile.write(bytes("<p>You accessed path: %s</p>" % self.path, "utf-8"))

        parsedUrl = urllib.parse.urlparse(self.path)
        parsedQuery = urllib.parse.parse_qs(parsedUrl.query)
        elecroMagnet.ip = parsedQuery["TargetIPAdress"][0]
        elecroMagnet.activate(int(parsedQuery["SetActiveForSeconds"][0]))

        self.wfile.write(bytes("</body></html>", "utf-8"))

myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    elecroMagnet = ElectroMagnet()
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))


