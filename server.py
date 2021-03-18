#!/usr/bin/env python3

import sys
import confundo
import argparse
import socket

parser = argparse.ArgumentParser("Parser")
parser.add_argument("host", help="Set Hostname")
parser.add_argument("port", help="Set Port Number", type=int)
parser.add_argument("file", help="Set File Directory")
args = parser.parse_args()

# Example how to use the provided confundo.Header class
sampleInput = b'\x00\x00\x00*\x00\x00\x00\x00\x00\x00\x00\x02sample-buffer'
print(sampleInput)
print(sampleInput[0:12])

pkt = confundo.Header()
pkt.decode(sampleInput[0:12])

print(f'SeqNum: {pkt.seqNum}')
print(f'AckNum: {pkt.ackNum}')
print(f'ConnId: {pkt.connId}')
print(f'IsAck: {pkt.isAck}')
print(f'IsSyn: {pkt.isSyn}')
print(f'IsFin: {pkt.isFin}')
# print(pkt.seqNum, pkt.ackNum, pkt.connId, pkt.isAck, pkt.isSyn, pkt.isFin)

if __name__ == '__main__':
    sys.stderr.write("server is not implemented yet\n")
