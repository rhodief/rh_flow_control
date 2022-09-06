from logging import Logger
from typing import Any, Dict
from collections.abc import Callable
from rh_flow_control.default import DefaultDataFlow

from rh_flow_control.model import Articulator

from .controls import STATUS_TYPE, Transporter, ExecutionControl, DataStore



class Execute(Articulator):
    '''
    Definition: this will trigger a user execution. It receive a callable
    '''
    def __init__(self, callable: Callable, params:Dict = {}) -> None:
        super().__init__([])
        self._callable = callable
        self._params = params
    def __call__(self, transporter: Transporter) -> Any:
        transporter.execution_control().check_in(self)
        if transporter.status == STATUS_TYPE.EXEC:
            transporter.execution_control().start_exec()
            transporter.receive_data(self._callable(*transporter.deliver(), **self._params))
            transporter.execution_control().end_exec()
        transporter.execution_control().check_out(self)
        return transporter

    
class Chain(Articulator):
    '''
    It calls articulators sequencially. 
    '''
    def __call__(self, transporter: Transporter) -> Any:
        transporter.execution_control().check_in(self)
        for articulator in self._articulators:
            transporter = articulator(transporter)
        transporter.execution_control().check_out(self)
        return transporter

class Stream(Articulator):
    '''
    It calls each item of iterator to pass through all articulators and it collects all of them in the end.
    '''
    pass

class ParallelStream(Articulator):
    '''
    Same of Stream, but it runs in parallel (threads)
    
    '''
    pass

class Parallel(Articulator):
    '''
    Each articulator becomes a branch to parallel execution
    '''
    pass

class Flow():
    '''
    Run a set of articulators. 
    '''
    def __init__(self, *articulator: Articulator, transporter = None, flow_logger = None) -> None:
        ## ToDo   Analyze... 
        self._articulators = articulator
        self._transporter = transporter
        self._flow_logger = flow_logger
        self._default_configs = DefaultDataFlow()
        if self._transporter is None:
            _flow_logger = self._default_configs.loggers()
            self._super_printer = self._default_configs.printers()
            self._flow_logger = _flow_logger
            self._set_new_transporter()
    def run(self):
        self._transporter.setStatus(STATUS_TYPE.EXEC)
        self._super_printer.watch()
        self._flow_execution()
        self._super_printer.block()
        self._transporter.setStatus(STATUS_TYPE.IDLE)
        return self._transporter.data()
        
    def _flow_execution(self) -> Transporter:
        for articulator in self._articulators:
            self._transporter = articulator(self._transporter)   
    def _set_new_transporter(self):
        execution_control = ExecutionControl(flow_logger=self._flow_logger)
        data_store = DataStore()
        self._transporter = Transporter(execution_control, data_store)

    