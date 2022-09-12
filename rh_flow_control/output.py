from enum import Enum
from pyclbr import Function
from queue import Queue
from enum import Enum
import threading
from typing import Any

class LogType(Enum):
    EXECUTION = 'EXECUTION'
    USER = 'USER'
    
class BrokerPort():
    def put(self, msg):
        raise NotImplementedError()        
    def get(self):
        raise NotImplementedError()
    def done(self):
        raise NotImplementedError()
    def block(self):
        raise NotImplementedError()
    
    
class QueueBrokerAdapter(BrokerPort):
    def __init__(self, q:Queue) -> None:
        self._queue = q
    def put(self, msg):
        self._queue.put(msg)
    def get(self):
        return self._queue.get()
    def done(self):
        return self._queue.task_done()
    def block(self):
        return self._queue.join()
        
class SuperLogger():
    '''
    This is responsable for both execution and user logs
    '''
    def __init__(self, broker: BrokerPort) -> None:
        self._broker = broker
    def send(self, logType: LogType, obj: object):
        self._broker.put({
            'type': logType.name,
            'msg': obj
        })
        
class ExposingWorkerPort():
    def __call__(self) -> Any:
        raise NotImplementedError()
    

class SimplePrintWorkerAdapter(ExposingWorkerPort):
    def __call__(self, broker) -> Any:
        while True:
            item = broker.get()
            #print(item['msg'])
            broker.done()
            
        
class SuperPrinter():
    '''
    This is responsable to expose the application logs.
    '''
    def __init__(self, broker: BrokerPort, exposingWorker: ExposingWorkerPort) -> None:
        self._broker = broker
        self._bd = {}
        self._thread = threading.Thread(target=exposingWorker, args=(self._broker,), daemon=True)        
    def watch(self):
        self._thread.start()
        pass
    def block(self):
        self._broker.block()
    
class ILogger:
    def __init__(self, super_logger: SuperLogger) -> None:
        self._logger = super_logger
        self._bd = []
        self._type = LogType.EXECUTION
    @property
    def logType(self) -> LogType:
        raise NotImplementedError()
    def log(self, msg):
        self._logger.send(self.logType, msg)
        self._bd.append(msg)
    def bd(self):
        return self._bd
        

class ULogger(ILogger):
    @property
    def logType(self) -> LogType:
        return LogType.USER
        

class ELogger(ILogger):
    @property
    def logType(self) -> LogType:
        return LogType.EXECUTION

class FlowLogger():
    def __init__(self, super_logger: SuperLogger) -> None:
        self._super_logger = super_logger
        self._u_logger = ULogger(self._super_logger)
        self._e_logger = ELogger(self._super_logger)
    @property
    def user_logger(self):
        return self._u_logger
    @property
    def exec_logger(self):
        return self._e_logger
    
    
    

        