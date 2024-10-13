import socket


def server():
    proto = socket.getprotobyname('tcp')
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto)

    serv.bind(("localhost", 2224))
    serv.listen(1)
    return serv


serv = server()

while 1:
    conn, addr = serv.accept()
    while 1:
        message = conn.recv(64).decode()
        if message:
            me = ('Hi, I am a server, I received: ' + message).encode()
            conn.send(me)
        else:
            break
    conn.close()
