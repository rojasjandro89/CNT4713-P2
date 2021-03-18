#!/usr/bin/env python3

import sys
import socket as SOCKET
from utils import Utils

import confundo

if __name__ == '__main__':
    [host, port, filename] = Utils.processClientArgs()
    file = open(filename, "rb")
    socket = SOCKET.socket(SOCKET.AF_INET, SOCKET.SOCK_DGRAM)
    confundoSocket = confundo.Socket(socket)

    try:
        remote = SOCKET.getaddrinfo(host, port, family=SOCKET.AF_INET, type=SOCKET.SOCK_DGRAM)
        (family, type, proto, canonname, sockaddr) = remote[0]
        confundoSocket.connect(sockaddr)
    except (SOCKET.error, OverflowError) as e:
        file.close()
        socket.close()
        Utils.errorOut(f'Invalid hostname or port ({e})')

    while True:
        try:
            (inPacket, fromAddr) = socket.recvfrom(1024)
            # Note in the above, parameter to .recvfrom should be at least MTU+12 (524), but can be anything else larger if we are willing to accept larger packets

            # Process incoming packet
            confundoSocket.on_receive(inPacket)

        except SOCKET.error as e:
            # this is the source of timeouts
            isError = confundoSocket.on_timeout()
            if isError:
                # on_timout should return True on critical timeout
                sys.stderr.write("ERROR: (%s)\n" % e)
                sys.exit(1)
            if confundoSocket.isClosed():
                break

        while not file.closed and confundoSocket.canSendData():
            data = file.read(confundo.MTU)
            if not data:
                file.close()
                break
            confundoSocket.send(data)

        if file.closed and confundoSocket.canSendData():
            confundoSocket.close()
