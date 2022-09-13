#!python3

import os
import sys
import glob
import json
import socket
from threading import Thread

port = 53
host = '127.0.0.1'
server = False

def load_zones():
    zonefiles = glob.glob('zones/*.zone')
    jsonzone = {}   
    for zonefile in zonefiles:
        with open(zonefile, 'rt') as file:
            data = json.load(file)
            jsonzone[data['$origin']] = data
    return jsonzone

zonedata = load_zones()

def getzone(domain):
    global zonedata
    try:

        return zonedata[domain]
    except KeyError:
        print(f'No records for {domain}')

def getflags(flags):
    byte1 = flags[0:1]
    byte2 = flags[1:2]
    
    rflags = ''
    QR = '1'

    OPCODE = ''
    for bit in range(1,5):
        OPCODE += str(ord(byte1)&(1<<bit))

    AA = '1'
    TC = '0'
    RD = '0'

    # Byte 2
    RA = '0'
    Z = '000'
    RCODE = '0000'

    return int(QR+OPCODE+AA+TC+RD, 2).to_bytes(1,
            byteorder='big')+int(RA+Z+RCODE, 2).to_bytes(1, byteorder='big')

def getquestiondomain(data):
    state = 0
    expectedlength = 0
    domainstring = ''
    domainparts = []
    x = 0
    y = 0
    
    for byte in data:
        if state == 1:
            if byte != 0:
                domainstring += chr(byte)   
            x += 1
            
            if x == expectedlength:
                domainparts.append(domainstring)
                domainstring = ''
                state = 0
                x = 0

            if byte == 0:
                domainparts.append(domainstring)
                break
        else:
            state = 1
            expectedlength = byte
    
        y += 1

    questiontype = data[y:y+2]
    return (domainparts,questiontype) 

def getrecs(data):
    domain, questiontype = getquestiondomain(data)
    qt = ''
    if questiontype == b'\x00\x01':
        qt = 'a'

    zone = getzone('.'.join(domain))

    return (zone[qt], qt, domain)

def buildquestion(domainname, rectype):
    qbytes = b''

    for part in domainname:
        length = len(part)
        qbytes += bytes([length])

        for char in part:
            qbytes += ord(char).to_bytes(1, byteorder='big')

    if rectype == 'a':
        qbytes += (1).to_bytes(2, byteorder='big')

    qbytes += (1).to_bytes(2, byteorder='big')

    return qbytes

def rectobyte(domainname, rectype, recttl, recval):
    rbytes = b'\xc0\x0c'

    if rectype == 'a':
        rbytes = rbytes + bytes([0]) + bytes([1])

    rbytes = rbytes + bytes([0]) + bytes([1])

    rbytes += int(recttl).to_bytes(4, byteorder='big')

    if rectype == 'a':
        rbytes = rbytes + bytes([0]) + bytes([4])

        for part in recval.split('.'):
            rbytes += bytes([int(part)])

    return rbytes

def buildresponse(data, addr):
    global server
    # TransactionID
    TransactionID = data[:2]

    # Get Flags
    Flags = getflags(data[2:4])

    # Question Count
    QDCOUNT = b'\x00\x01'

    # Answer Count
    ANCOUNT = len(getrecs(data[12:])[0]).to_bytes(2, byteorder='big')

    # Nameserver Count
    NSCOUNT = (0).to_bytes(2, byteorder='big')

    # Additional Count
    ARCOUNT = (0).to_bytes(2, byteorder='big')

    dnsheader = TransactionID+Flags+QDCOUNT+ANCOUNT+NSCOUNT+ARCOUNT

    records, rectype, domainname = getrecs(data[12:])

    dnsquestion = buildquestion(domainname, rectype)
    dnsbody = b''

    for record in records:
        dnsbody += rectobyte(domainname, rectype, record['ttl'], record['value'])

    response = dnsheader + dnsquestion + dnsbody
    server.sendto(response, addr)

def main():
    #if os.getuid() != 0:
    #    print('Run this script as root!!!')
    #    sys.exit(1)
    global server
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind((host, port))

        while True:
            data, addr = server.recvfrom(512)
            client = Thread(target=buildresponse, args=(data,addr))
            client.start()
            #r = buildresponse(data)
            
            
    except Exception as e:
        print(str(e))
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == '__main__':
    main()
