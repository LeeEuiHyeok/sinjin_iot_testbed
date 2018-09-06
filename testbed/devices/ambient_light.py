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

# Import the TCS34725 module.
import Adafruit_TCS34725


# Create a TCS34725 instance with default integration time (2.4ms) and gain (4x).
import smbus
tcs = Adafruit_TCS34725.TCS34725()

# You can also override the I2C device address and/or bus with parameters:
#tcs = Adafruit_TCS34725.TCS34725(address=0x30, busnum=2)

# Or you can change the integration time and/or gain:
tcs = Adafruit_TCS34725.TCS34725(gain=Adafruit_TCS34725.TCS34725_GAIN_60X)
# Possible integration time values:
#  - TCS34725_INTEGRATIONTIME_2_4MS  (2.4ms, default)
#  - TCS34725_INTEGRATIONTIME_24MS
#  - TCS34725_INTEGRATIONTIME_50MS
#  - TCS34725_INTEGRATIONTIME_101MS
#  - TCS34725_INTEGRATIONTIME_154MS
#  - TCS34725_INTEGRATIONTIME_700MS
# Possible gain values:
#  - TCS34725_GAIN_1X
#  - TCS34725_GAIN_4X
#  - TCS34725_GAIN_16X
#  - TCS34725_GAIN_60X

# Disable interrupts (can enable them by passing true, see the set_interrupt_limits function too).
tcs.set_interrupt(False)


# Enable interrupts and put the chip back to low power sleep/disabled.
tcs.set_interrupt(True)
tcs.disable()


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

while (True):
    try:
        #### TCS34725 ####
        # Read the R, G, B, C color data.
        r, g, b, c = tcs.get_raw_data()

        # Calculate color temperature using utility functions.  You might also want to
        # check out the colormath library for much more complete/accurate color functions.
        color_temp = Adafruit_TCS34725.calculate_color_temperature(r, g, b)

        # Calculate lux with another utility function.
        lux = Adafruit_TCS34725.calculate_lux(r, g, b)
        data = {'value': lux}

        def myOnPublishCallback():
            print(lux)

        success = deviceCli.publishEvent(args.event, "json", data, qos=0, on_publish=myOnPublishCallback)
        if not success:
            print("Not connected to IoTF")
        time.sleep(args.delay)

    except:
        print("error!")

# Disconnect the device and application from the cloud
deviceCli.disconnect()
