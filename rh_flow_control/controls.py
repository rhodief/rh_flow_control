
from ast import List
from enum import Enum
from typing import Any, Dict
from datetime import datetime

from rh_flow_control.output import ELogger, FlowLogger, SuperLogger


class STATUS_TYPE(Enum):
    IDLE = 'IDLE'
    NO_EXEC = 'NO_EXEC'
    EXEC = 'EXEC'

class IndexControl:
    def __init__(self, index = []) -> None:
        self._index = index
    def next(self):
        if len(self._index) < 1: self._index = [-1]
        self._index[-1] += 1
        return self
    def new_child_branch(self, index = -1):
        self._index.append(index)
        return self
    def kill_child_branch(self):
        self._index.pop()
        return self
    def getIndex(self) -> str:
        return '.'.join([str(i) for i in self._index])
    def copy(self):
        return IndexControl(self._index)
    
class TreeNode:
    def __init__(self, index: str, name: str, ntype: str) -> None:
        self._name = name
        self._type = ntype
        self._index = index
        self._start = None
        self._end = None
    @property
    def name(self):
        return self._name                
    @property
    def getType(self):
        return self._type
    @property
    def index(self):
        return self._index
    def set_start_time(self, time):
        self._start = time
    def set_end_time(self, time):
        self._end = time
    @property
    def delta_time(self):
        return round((self._end - self._start).total_seconds(), 5) if self._start and self._end else None
    def to_dict(self):
        ret = {
            'name': self.name,
            'type': self.getType,
            'index': self.index
        }
        if self._start:
            ret['start'] = self._start
            ret['end'] = self._end
            ret['delta'] = self.delta_time
        return ret
        
class CurrentExecution:
    def __init__(self, e_logger: ELogger) -> None:
        self._current = {}
        self._e_logger = e_logger
    def set_execution(self, index: IndexControl, node: TreeNode):
        i = index.getIndex()
        self._current[i] = TreeNode(i, node.name, node.getType)
        self._e_logger.log(self._current[i])
    def remove_execution(self, index: IndexControl):
        i = index.getIndex()
        if i in self._current:
            del self._current[index.getIndex()]
    def get_execution(self, index: IndexControl) -> TreeNode:
        return self._current.get(index.getIndex(), None)
    def get_all_executions(self):
        return self._current
    def to_dict(self):
        return {k: v.to_dict() for k, v in self._current.items()}

'''
class ExecutionTree:
    def __init__(self, treeDto = []) -> None:
        self._tree: List(TreeNode) = []
        self._current_index = ''
        ## Parse Tree... 
    def add_node(self, name: str, ntype: str, indexStr: str):
        self._tree.append(TreeNode(indexStr, name, ntype))
        self._current_index = indexStr
    def get_node(self, index: str):
        node = [node for node in self._tree if node.index == index]
        return node[0] if len(node) > 0 else None
    def __len__(self):
        return len(self._tree)


'''
class FakeBroker():
    def put(self, msg):
        pass
    def get(self):
        pass
    def done(self):
        pass
    def block(self):
        pass

class ExecutionControl:
    def __init__(self, index_control: IndexControl = None, current_execution: CurrentExecution = None, flow_logger: FlowLogger = None) -> None:
        self._index = index_control if index_control is not None else IndexControl()
        self._flow_logger = flow_logger if flow_logger else FlowLogger(SuperLogger(FakeBroker()))
        self._current_execution = current_execution if current_execution is not None else CurrentExecution(self._flow_logger._e_logger)
    def current_execution(self):
        return self._current_execution
    def u_logger(self):
        return self._flow_logger.user_logger
    def getIndex(self):
        return self._index
    def check_in(self, articulator: Any):
        '''
        When transporter arrives a Node
        '''
        self._index.next()
        node_type = articulator.type
        i = self._index
        node = TreeNode(i, articulator.name, articulator.type)
        self._current_execution.set_execution(i, node)        
        if node_type != 'Execute':
            self._index.new_child_branch()
        return self
        
    def check_out(self, articulator: Any):
        '''
        When transporter leaves a Node
        '''
        self._current_execution.remove_execution(self._index)
        node_type = articulator.type
        if node_type != 'Execute':
            self._index.kill_child_branch()
        
    def start_exec(self):
        '''
        When an execution starts
        '''
        self._current_execution.get_execution(self._index).set_start_time(datetime.now())
        
    def end_exec(self):
        '''
        When an execution ends
        '''
        self._current_execution.get_execution(self._index).set_end_time(datetime.now())
        
class DataStore:
    pass


class Transporter:
    def __init__(self, execution_control: ExecutionControl, data_store: DataStore, data = None) -> None:
        self._data = data
        self._status = STATUS_TYPE.IDLE
        self._execution_control = execution_control
        self._data_store = data_store
    def setStatus(self, status: STATUS_TYPE):
        self._status = status
    @property
    def status(self):
        return self._status
    def deliver(self):
        return self._data, self._data_store, None, self._execution_control.u_logger()
    def receive_data(self, data):
        self._data = data
        return self
    def data(self):
        return self._data
    def execution_control(self) -> ExecutionControl:
        return self._execution_control
    
    
    
    
