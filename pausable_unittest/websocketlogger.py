
import threading
import json
from select import select
from . import picklablelogger
from . import SimpleWebSocketServer
from . import websocket

class LogServer(SimpleWebSocketServer.WebSocket):
    @property
    def is_logger(self):
        return self._is_logger

    def handleMessage(self):
        try:
            data = json.loads(self.data)
            if data["action"] == "register":
                if data["type"] == "server":
                    self._is_logger = True
                else:
                    self._is_logger = False
            elif data["action"] == "log":
                if self._is_logger:
                    for client in self.server.connections.values():
                        if not client.is_logger:
                            client.sendMessage(self.data)
            elif data["action"] == "end":
                self.server.close()
            else:
                pass
        except Exception as e:
            pass

    def handleConnected(self):
        self._is_logger = False

    def handleClose(self):
        pass

class WebSocketServer(SimpleWebSocketServer.SimpleWebSocketServer):
    def __init__(self, host, port, websocketclass, selectInterval=0):
        super(WebSocketServer, self).__init__(host, port, websocketclass, selectInterval)
        self._closed = False

    def close(self):
        self._closed = True
        super(WebSocketServer, self).close()

    def closed(self):
        return self._closed

    def serveforever(self):
        while not self.closed():
            writers = []
            for fileno in self.listeners:
                if fileno == self.serversocket:
                    continue
                client = self.connections[fileno]
                if client.sendq:
                    writers.append(fileno)

            if self.selectInterval:
                rList, wList, xList = select(self.listeners, writers, self.listeners, self.selectInterval)
            else:
                rList, wList, xList = select(self.listeners, writers, self.listeners)

            for ready in wList:
                client = self.connections[ready]
                try:
                    while client.sendq:
                        opcode, payload = client.sendq.popleft()
                        remaining = client._sendBuffer(payload)
                        if remaining is not None:
                            client.sendq.appendleft((opcode, remaining))
                            break
                        else:
                            # if opcode == SimpleWebSocketServer.CLOSE:
                            if opcode == 0x08:
                                raise Exception('received client close')

                except Exception as n:
                    self._handleClose(client)
                    del self.connections[ready]
                    self.listeners.remove(ready)

            for ready in rList:
                if ready == self.serversocket:
                    try:
                        sock, address = self.serversocket.accept()
                        newsock = self._decorateSocket(sock)
                        newsock.setblocking(0)
                        fileno = newsock.fileno()
                        self.connections[fileno] = self._constructWebSocket(newsock, address)
                        self.listeners.append(fileno)
                    except Exception as n:
                        if sock is not None:
                            sock.close()
                else:
                    if ready not in self.connections:
                        continue
                    client = self.connections[ready]
                    try:
                        client._handleData()
                    except Exception as n:
                        self._handleClose(client)
                        del self.connections[ready]
                        self.listeners.remove(ready)

            for failed in xList:
                if failed == self.serversocket:
                    self.close()
                    raise Exception('server socket failed')
                else:
                    if failed not in self.connections:
                        continue
                    client = self.connections[failed]
                    self._handleClose(client)
                    del self.connections[failed]
                    self.listeners.remove(failed)

class WebSocketServerThread(threading.Thread):
    def __init__(self, address, port, event):
        self.event = event
        self.address = address
        self.port = port
        super(WebSocketServerThread, self).__init__()

    def run(self):
        try:
            server = WebSocketServer(self.address, self.port, LogServer, 0)
        finally:
            self.event.set()
        server.serveforever()

class PicklableWebSocketHandler(picklablelogger.PicklableHandler):
    MAX_LOG_COUNT = 1000

    def __init__(self, address="0.0.0.0", port=12345, fmt=picklablelogger.FORMAT,
                 date_format=picklablelogger.DATE_FORMAT, max_log_count=MAX_LOG_COUNT):
        super(PicklableWebSocketHandler, self).__init__(fmt=fmt, date_format=date_format)
        self.__address = address
        self.__port = port
        self.__server_thread = None
        self.__connection = None
        self.__max_log_count = max_log_count
        self.__log_count = 0
        self.__log_list = []

    def open(self):
        if self.__server_thread:
            return
        event = threading.Event()
        self.__server_thread = WebSocketServerThread(self.__address, self.__port, event)
        self.__server_thread.start()
        event.wait()
        connection = websocket.create_connection("ws://127.0.0.1:%d/" % self.__port)
        self.__connection = connection
        self.send({"action": "register", "type": "server"})

    def close(self):
        if self.__server_thread is None:
            return
        self.send({"action": "end"})
        self.__server_thread.join()
        self.__server_thread = None
        self.__connection = None

    def emit(self, record):
        log = self.format(record)
        self.raw_writeln(log)

    def raw_writeln(self, text):
        self.open()
        if self.__max_log_count and self.__log_count >= self.__max_log_count:
            self.__log_list[self.__log_count % self.__max_log_count] = text
        else:
            self.__log_list.append(text)
        self.__log_count += 1
        self.send({"action": "log", "text": text})

    def send(self, param):
        if self.__server_thread is None:
            return
        self.__connection.send(json.dumps(param))

    def prepare_for_pause(self):
        super(PicklableWebSocketHandler, self).prepare_for_pause()
        self.close()
