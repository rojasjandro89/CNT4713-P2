# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-

from .common import *
from .packet import Packet
from .cwnd_control import CwndControl

from enum import Enum
import time
import sys

class State(Enum):
    INVALID = 0
    SYN = 1
    OPEN = 3
    FIN = 10
    FIN_WAIT = 11
    CLOSED = 20
    ERROR = 21

class Ostream:
    def __init__(self, base = 12345, isOpening = True):
        self.base = base
        self.seqNum = base
        self.lastAckTime = time.time() # last time ACK was sent / activity timer
        self.cc = CwndControl()
        self.buf = b""
        self.state = State.INVALID
        self.firstPacketSent = False
        self.nDupAcks = 0

    def ack(self, ackNo, connId):
        if self.state == State.INVALID:
            return None
        self.lastAckTime = time.time()
        # if self.state == State.FIN_WAIT:
        #     return Packet(b"", False, seqNum=self.seqNum, ackNum=ackNo, connId=connId, isAck=True, isSyn=False, isFin=False)
        # else:
        #     self.seqNum += 1
        #     return Packet(b"", False, seqNum=ackNo, ackNum=self.seqNum, connId=connId, isAck=True, isSyn=False, isFin=False)
        ###
        ### IMPLEMENT
        ###
        pass

    def makeNextPacket(self, connId, payload, isSyn=False, isFin=False, isAck=False, **kwargs):
        ackNum = 0
        if isSyn:
            self.base = 42
            self.seqNum = 42
            self.state = State.SYN
            self.cc.cwnd = 1024
            self.cc.ssthresh = 15000
        elif isFin:
            self.state = State.FIN
        elif not self.firstPacketSent or isAck:
            isAck = True
            self.seqNum += 1
            ackNum = self.seqNum
        else:
            self.seqNum += len(payload)
        packet = Packet(payload, False, seqNum=self.seqNum, ackNum=ackNum, connId=connId, isAck=isAck, isSyn=isSyn, isFin=isFin)

        ###
        ### IMPLEMENT
        ###
        return packet

    def hasBufferedData(self):
        ###
        ### IMPLEMENT
        ###
        pass

    def makeNextRetxPacket(self, connId):
        ###
        ### IMPLEMENT
        ###
        pass

    def on_timeout(self, connId):
        ###
        ### IMPLEMENT
        ###
        return None

    def canSendNewData(self):
        inFlight = (self.seqNum - self.base) % MAX_SEQNO
        if (inFlight < len(self.buf)):
            return False
        return self.state == State.OPEN

    def __str__(self):
        return f"state:{self.state} base:{self.base} seqNum:{self.seqNum} nSentData:{len(self.buf)} cc:{self.cc}"
