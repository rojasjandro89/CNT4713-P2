# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-

import sys
import time

from .common import *
from .istream import Istream
from .ostream import Ostream, State
from .packet import Packet

class Socket:
    '''Incomplete socket abstraction for Confundo protocol'''

    def __init__(self, sock, connId=0):
        self.sock = sock
        self.connId = connId
        self.sock.settimeout(0.5)
        self.istream = None
        self.ostream = None
        self.finWaiting = None

    def format_line(self, command, pkt):
        s = f"{command} {pkt.seqNum} {pkt.ackNum} {pkt.connId} {int(self.ostream.cc.cwnd)} {self.ostream.cc.ssthresh}"
        if pkt.isAck: s = s + " ACK"
        if pkt.isSyn: s = s + " SYN"
        if pkt.isFin: s = s + " FIN"
        if pkt.isDup: s = s + " DUP"
        return s

    def _send(self, packet):
        '''"Private" method to send packet out'''

        self.sock.sendto(packet.encode(), self.remote)
        print(self.format_line("SEND", packet))

    def on_receive(self, buf, file):
        '''Method that dispatches the received packet'''
        pkt = Packet().decode(buf)
        print(self.format_line("RECV", pkt)) #+ f" | {self.ostream.state}"
        
        self.connId = pkt.connId

        if pkt.isSyn:
            payload = file.read(MTU)
            ack_pkt = self.ostream.ack(pkt.seqNum+1, self.connId, payload)
            self.ostream.state = State.CLOSED
            self._send(ack_pkt)            
        elif pkt.isAck:
            self.ostream.lastAckTime = time.time()
            if self.ostream.state == State.CLOSED:
                self.ostream.state = State.OPEN
            elif self.ostream.state == State.FIN:
                self.finWaiting = time.time()
                self.ostream.state = State.FIN_WAIT
        elif pkt.isFin:
            fin_ack_pkt = self.ostream.ack(pkt.seqNum+1, self.connId)
            self._send(fin_ack_pkt)

        if not ((pkt.isSyn and pkt.isAck) or self.ostream.state == State.FIN or self.ostream.state == State.FIN_WAIT):
            self.ostream.state = State.OPEN

    def on_timeout(self):
        '''Called every 0.5 seconds if nothing received'''
        now = time.time()
        if self.ostream.state == State.FIN_WAIT and (now - self.finWaiting) >= FIN_WAIT_TIME:
            sys.exit(1)
        if (now - self.ostream.lastAckTime) >= GLOBAL_TIMEOUT:
            return True

        return False

    def connect(self, remote):
        self.remote = remote
        self.ostream = Ostream()

        pkt = self.ostream.makeNextPacket(connId=0, payload=b"", isSyn=True)
        self._send(pkt)

    def canSendData(self): 
        return self.ostream.canSendNewData()

    def send(self, payload):
        pkt = self.ostream.makeNextPacket(self.connId, payload)
        if not (pkt.isSyn or pkt.isFin):
            self.ostream.state = State.CLOSED
        self._send(pkt)        

    def close(self):
        pkt = self.ostream.makeNextPacket(self.connId, payload=b"", isFin=True)
        self._send(pkt)

    def isClosed(self):
        return self.ostream.state == State.CLOSED
