import struct
import socket
from datetime import datetime


def date_decode(value: hex):
    # convert hex 0x23 > int 23
    result=[]
    for x in range(len(value)):
        result.append(int(hex(value[x])[2:]))
    return result
def date_code(value):
    # convert int 23 > int(hex 0x23)
    result=[]
    for x in range(len(value)):
        result.append(int(str(value[x]),16))
    return result

def crc16(data: bytes):
    xor_in = 0x0000  # initial value
    xor_out = 0x0000  # final XOR value
    poly = 0xA001  # generator polinom (reversed form)
    reg = xor_in
    for octet in data:
        reg ^= octet
        for j in range(0,8):
            if (reg & 0x0001) > 0:
                reg =(reg >> 1) ^ poly
            else:
                reg = reg >> 1
    return reg ^ xor_out

def chsum8xor(data: bytes):
    checksum = 0
    for x in data:
        checksum ^= x
    return checksum

# packet = b"\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xfe\xff\x00\x80\x05\x00\xfe\xff\x01\x00\x02\x59\x00\x90\x96\x72\x00\x00\x00\x00\x00\x00\x05\x00\x1e\x78\xc8\x01\xa2\x00\x00\x00\x5a\x5a"

class led:
    def __init__(self, ip, port=5005):
        self.address = ip, port
    
    def sendpacket(self, packet: bytes):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.address)
            s.settimeout(2.5)

            s.send(packet)
            data = s.recv(1024)
            s.close()
            return data
    
    def sendcmd(self, body):
        # \x01 - ?
        # \xa2 - cmdgroup
        # \x0f - cmd

        # \x01\xa2\x0f\x00\x00 - Get status																																								
        # \x01\xa2\x05\x01\x00\x01 - led_on
        # \x01\xa2\x05\x01\x00\x00 - led_off
        # \x01\xa2\x02\x08\x00\x23\x20\x12\x01\x21\x01\x37\x05 - install date 2023.12.1 21:01:37 5week



        # dstAddr
        header = b"\x01\x00"
        # srcAddress	
        header += b"\x00\x80"
        # protocolVer
        header += b"\x05"
        # protocolType
        header += b"\x00"
        # deviceType
        header += b"\x52\x00"
        # phyType
        header += b"\x01"
        # 
        header += b"\x00"
        # msgSeq	
        header += b"\x00\x00"
        # 
        header += b"\x00\x90"
        # encryptionType
        header += b"\x96"
        # randomNumber
        header += b"\x00"
        # secret					
        header += b"\x00\x00\x00\x00\x00\x00"
        # bodyLen (LE)	
        header += struct.pack('H', len(body))
        # CRC-16 (CheckSum body)				
        header += struct.pack('H', crc16(body))

        # preheader
        packet=b"\xa5"*8
        # header
        packet+=header
        # CheckSum8 XOR (header)
        packet+=struct.pack('B', chsum8xor(header))
        # preheader
        packet+=body
        # end
        packet+=b'\x5a'*2

        # print(packet)
        # x=''
        # for y in bytearray(packet):
        #     x+=f" {y:02x}"
        # print(x)

        return self.sendpacket(packet)

    def status(self):
        # data=self.sendpacket(b"\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\x01\x00\x00\x80\x05\x00\x52\x00\x01\x00\x32\x6c\x00\x90\x96\x5d\x00\x00\x00\x00\x00\x00\x05\x00\x2e\x7b\x82\x01\xa2\x0f\x00\x00\x5a\x5a")
        data=self.sendcmd(b'\x01\xa2\x0f\x00\x00')
        status=struct.unpack_from('??BBBxxxxx??B', data, len(data)-34)
        statusdate = struct.unpack_from('<HBBBBBB', data, len(data)-20)
        statusdate=date_decode(statusdate)

        a = {
            "screenOnOff": status[0],
            "timingOnOff": status[1],
            "brightnessMode": status[2],
            "Brightness": status[3],
            "programNum": status[4],
            "screenLocked": status[5],
            "programLocked":status[6],
            "runningMode": status[7],
            "date": statusdate
        }
        return a
    def led_on(self):
        #self.sendpacket(b"\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\x01\x00\x00\x80\x05\x00\x52\x00\x01\x00\x6a\x58\x00\x90\x96\x02\x00\x00\x00\x00\x00\x00\x06\x00\x68\xc4\x4b\x01\xa2\x05\x01\x00\x01\x5a\x5a")
        self.sendcmd(b"\x01\xa2\x05\x01\x00\x01")
    def led_off(self):
        # self.sendpacket(b"\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\x01\x00\x00\x80\x05\x00\x52\x00\x01\x00\x6e\x58\x00\x90\x96\x76\x00\x00\x00\x00\x00\x00\x06\x00\xa9\x04\x3a\x01\xa2\x05\x01\x00\x00\x5a\x5a")
        self.sendcmd(b"\x01\xa2\x05\x01\x00\x00")
    def dateset(self, date: list):
        '''
        date format [YYYY, M, D, H, M, S, W] 
        example [2023, 12, 7, 13, 37, 22, 4] 
        '''
        # date=date_code()
        datepacket = b'\x01\xa2\x02\x08\x00'
        date=date_code(date)
        datepacket += struct.pack('<HBBBBBB', date[0], date[1], date[2], date[3], date[4], date[5], date[6])
        self.sendcmd(datepacket)
    def syncdate(self):
        nowdate=datetime.now()
        setdata=[nowdate.year, nowdate.month, nowdate.day, nowdate.hour, nowdate.minute, nowdate.second, nowdate.isoweekday()]
        self.dateset(setdata)



if __name__ == "__main__": 
    ledtest = led('192.168.3.19')
    # ledtest.status()
    # ledtest.dateset([2023, 12, 7, 13, 37, 22, 4])
    # ledtest.led_off()
    # ledtest.ledon()
    # ledtest.syncdate()
    # ledtest.sendcmd()