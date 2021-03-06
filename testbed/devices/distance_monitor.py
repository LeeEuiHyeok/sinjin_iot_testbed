# *****************************************************************************
# Copyright (c) 2017 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# *****************************************************************************

import time
import sys
import uuid
import argparse
import get_raw_data as grd

import RPi.GPIO as gpio

trig_pin = 13
echo_pin = 19

gpio.setmode(gpio.BCM)
gpio.setup(trig_pin, gpio.OUT)
gpio.setup(echo_pin, gpio.IN)


try:
	import ibmiotf.device
except ImportError:
	# This part is only required to run the sample from within the samples
	# directory when the module itself is not installed.
	#
	# If you have the module installed, just use "import ibmiotf.device"
	import os
	import inspect
	cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../src")))
	if cmd_subfolder not in sys.path:
		sys.path.insert(0, cmd_subfolder)
	import ibmiotf.device

def commandProcessor(cmd):
	print("Command received: %s" % cmd.data)


authMethod = None
#xdataset = grd.get_data_from_csv('temperature')

# Initialize the properties we need
parser = argparse.ArgumentParser()

# Primary Options
parser.add_argument('-o', '--organization', required=False, default="quickstart")
parser.add_argument('-T', '--devicetype', required=False, default="simpleDev")
parser.add_argument('-I', '--deviceid', required=False, default=str(uuid.uuid4()))
parser.add_argument('-t', '--token', required=False, default=None, help='authentication token')
parser.add_argument('-c', '--cfg', required=False, default=None, help='configuration file')
parser.add_argument('-E', '--event', required=False, default="event", help='type of event to send')
parser.add_argument('-N', '--nummsgs', required=False, type=int, default=1, help='send this many messages before disconnecting')
parser.add_argument('-D', '--delay', required=False, type=float, default=1, help='number of seconds between msgs')
args, unknown = parser.parse_known_args()

if args.token:
	authMethod = "token"

# Initialize the device client.

try:
	if args.cfg is not None:
		deviceOptions = ibmiotf.device.ParseConfigFile(args.cfg)
	else:
		deviceOptions = {"org": args.organization, "type": args.devicetype, "id": args.deviceid, "auth-method": authMethod, "auth-token": args.token}
	deviceCli = ibmiotf.device.Client(deviceOptions)
	deviceCli.commandCallback = commandProcessor
except Exception as e:
	print("Caught exception connecting device: %s" % str(e))
	sys.exit()

# Connect and send datapoint(s) into the cloud
deviceCli.connect()


while True:
    gpio.output(trig_pin, False)
    time.sleep(0.5)

    gpio.output(trig_pin, True)
    time.sleep(0.00001)
    gpio.output(trig_pin, False)

    while gpio.input(echo_pin) == 0:
        pulse_start = time.time()

    while gpio.input(echo_pin) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34000 / 2
    distance = round(distance, 2)

    print(distance)
    data = {'value': distance }

    def myOnPublishCallback():
        print(distance)


    success = deviceCli.publishEvent(args.event, "json", data, qos=0, on_publish=myOnPublishCallback)
    if not success:
        print("Not connected to IoTF")
    time.sleep(args.delay)


# Disconnect the device and application from the cloud
deviceCli.disconnect()
