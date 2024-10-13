import socket

def sendPacket():
    proto = socket.getprotobyname('tcp')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto)
    try:
        s.connect(("127.0.0.1", 2224))
        s.send("Hello world".encode())

        resp = s.recv(1024)
        print (resp)
    except socket.error:
        pass
    finally:
        s.close()

if __name__ == '__main__':
    sendPacket()
