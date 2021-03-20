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
        if self.ostream.state == State.OPEN:
            self.ostream.state = State.CLOSED
        if len(packet.payload) > len(b""):            
            self.ostream.firstPacketSent = True
        print(self.format_line("SEND", packet))

    def on_receive(self, buf):
        '''Method that dispatches the received packet'''
        pkt = Packet().decode(buf)
        print(self.format_line("RECV", pkt))
        
        self.connId = pkt.connId

        if pkt.isAck:            
            if self.ostream.state == State.FIN:
                print(f"Got an ACK with FIN")
                self.finWaiting = time.time()
                self.ostream.state = State.FIN_WAIT
            if self.ostream.state == State.CLOSED:
                self.ostream.state = State.OPEN
        

        # if pkt.isSyn and pkt.isAck:
        #     ack_packet = self.ostream.ack(ackNo=pkt.ackNum, connId=self.connId)
        #     self._send(ack_packet)
        #     self.ostream.state = State.OPEN
        # elif pkt.isAck:
        #     self.ostream.seqNum = pkt.ackNum
        #     if self.ostream.state == State.CLOSED:
        #         self.ostream.state = State.OPEN
        #     elif self.ostream.state == State.FIN:
        #         self.finWaiting = time.time()
        #         self.ostream.state = State.FIN_WAIT
        # elif pkt.isFin:
        #     ack_packet = self.ostream.ack(ackNo=pkt.seqNum + 1, connId=self.connId)
        #     self._send(ack_packet)
        ###
        ### IMPLEMENT
        ###

    def on_timeout(self):
        '''Called every 0.5 seconds if nothing received'''
        if self.ostream.state == State.FIN_WAIT and (time.time() - self.finWaiting) >= 2:
            sys.exit(0)
        
        ###
        ### IMPLEMENT
        ###

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
        self._send(pkt)
        self.ostream.state = State.CLOSED

    def close(self):
        pkt = self.ostream.makeNextPacket(self.connId, payload=b"", isFin=True)
        self._send(pkt)

    def isClosed(self):
        return self.ostream.state == State.CLOSED
