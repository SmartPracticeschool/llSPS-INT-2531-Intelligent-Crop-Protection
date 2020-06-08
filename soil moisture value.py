import time
import sys
import ibmiotf.application
import ibmiotf.device
import random
import requests
#Provide your IBM Watson Device Credentials
organization = "3q1zrv"
deviceType = "raspberrypi"
deviceId = "123456"
authMethod = "token"
authToken = "12345678"
def myCommandCallback(cmd):
        print("Command received: %s" % cmd.data)#Commands

try:
	deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
	deviceCli = ibmiotf.device.Client(deviceOptions)
	#..............................................
	
except Exception as e:
	print("Caught exception connecting device: %s" % str(e))
	sys.exit()
# Connect and send a datapoint "hello" with value "world" into the cloud as an event of type "greeting" 10 times
deviceCli.connect()
while True:
        hum=random.randint(10, 40)
        #print(hum)
        temp =random.randint(30, 80)
        #Send Temperature & Humidity to IBM Watson
        data = { 'Temperature' : temp, 'Humidity': hum }
        if hum<=25:
            url = "https://www.fast2sms.com/dev/bulk"
            querystring = {"authorization":"uL2wfido0XYZTj65QsHCPVBGpFmMyDWzhler1IbxOS8ng4av7U1ByCDmlnYsvF8c5L9odPIWrp2wMziJ","sender_id":"FSTSMS","message":"water level in the soil is low ,please sprinkle water","language":"english","route":"p","numbers":"9440443739,9440580362"}
            headers = {
                         'cache-control': "no-cache"
            }
            response = requests.request("GET", url, headers=headers, params=querystring)
            print(response.text)
        #print (data)
        def myOnPublishCallback():
            print ("Published Temperature = %s C" % temp, "Humidity = %s %%" % hum, "to IBM Watson")
        success = deviceCli.publishEvent("Weather", "json", data, qos=0, on_publish=myOnPublishCallback)
        if not success:
            print("Not connected to IoTF")
        time.sleep(2)
        deviceCli.commandCallback = myCommandCallback
# Disconnect the device and application from the cloud
deviceCli.disconnect()
