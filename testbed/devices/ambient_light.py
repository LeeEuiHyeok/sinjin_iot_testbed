import RPi.GPIO as gpio
import time

anal_pin = 17

gpio.setmode(gpio.BCM)
gpio.setup(anal_pin, gpio.OUT)


