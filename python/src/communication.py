from Queue import Queue, Empty
from threading import Thread


class Communication:
    """
    Worker that sends and receives information using multi-threaded queues
    """

    def __init__(self, conn):
        """
        initializes class with connection
        starts listening for messages to send/receive
        :param conn: connection to interact with
        """
        self.__connection = conn
        self.__read_queue = Queue()
        self.__write_queue = Queue()
        read_thread = Thread(target=self.read_worker)
        write_thread = Thread(target=self.write_worker)
        read_thread.setDaemon(True)
        write_thread.setDaemon(True)
        read_thread.start()
        write_thread.start()

    def send(self, msg):
        """
        sends message to connection
        non-blocking!
        :param msg: message to be sent
        """
        self.__write_queue.put(msg)

    def recv(self):
        """
        receives message from connection
        non-blocking!
        :return: None if no message otherwise returns oldest message not yet read
        """
        try:
            msg = self.__read_queue.get_nowait()
        except Empty:
            msg = None
        return msg

    def read_worker(self):
        """
        worker dedicated to reading messages from connection
        """
        while True:
            if self.__connection.poll():
                msg = self.__connection.recv()
                self.__read_queue.put(msg)

    def write_worker(self):
        """
        worker dedicated to writing messages to connection
        """
        while True:
            msg = self.__write_queue.get()
            self.__connection.send(msg)

"""

def f(conn):
    com = Communication(conn)
    i = 0
    while True:
        i += 1
        com.send(i)

from multiprocessing import Pipe, Process
a, b = Pipe()
aComm = Communication(a)
p = Process(target=f, args=(b,))
p.start() 
while True:
    msg = aComm.recv()
    if msg is not None:
        print msg
        """

