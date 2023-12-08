import sys
import time
import bx5

ledtest = bx5.led('192.168.3.19')

if sys.argv[1]:
    if sys.argv[1]=='on':
        ledtest.led_on()
    elif sys.argv[1]=='off':
        ledtest.led_off()
    elif sys.argv[1]=='Status':
        print(ledtest.status()['screenOnOff'])
    elif sys.argv[1]=='Brightness':
        print(ledtest.status()['Brightness'])
    elif sys.argv[1]=='syncdate':
        ledtest.syncdate()