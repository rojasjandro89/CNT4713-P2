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
    def __init__(self, base = 42, isOpening = True):
        self.base = base
        self.seqNum = base
        self.lastAckTime = time.time() # last time ACK was sent / activity timer
        self.cc = CwndControl()
        self.buf = b""
        self.state = State.INVALID
        self.nDupAcks = 0

    def safelyWrapSeqNum(self):
        if self.seqNum > MAX_SEQNO:
            self.seqNum -= (MAX_SEQNO + 1)

    def ack(self, ackNo, connId, payload=b''):
        if self.state == State.INVALID:
            return None
        return self.makeNextPacket(connId, payload, isAck=True, ackNum=ackNo)


    def makeNextPacket(self, connId, payload, isSyn=False, isFin=False, isAck=False, ackNum=0, **kwargs):
        if isSyn:
            self.state = State.SYN
        if isFin:
            self.state = State.FIN
        if isAck:
            self.seqNum += 1
            
        self.safelyWrapSeqNum()
        pkt = Packet(payload, False, seqNum=self.seqNum, ackNum=ackNum, connId=connId, isAck=isAck, isSyn=isSyn, isFin=isFin)
        self.seqNum += len(payload)

        return pkt

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
        canSend = self.state == State.OPEN #and (self.cc.cwnd - inFlight) >= MTU
        #if not canSend:
            #print(f"...")
        return canSend

    def __str__(self):
        return f"state:{self.state} base:{self.base} seqNum:{self.seqNum} nSentData:{len(self.buf)} cc:{self.cc}"