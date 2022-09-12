from logging import Logger
from typing import Any, Dict, List, Tuple
from collections.abc import Callable
from unittest import result
from rh_flow_control.default import DefaultDataFlow

from rh_flow_control.model import Articulator
from rh_flow_control.threads_control import RhThreads

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
    def __call__(self, transporter: Transporter):
        transporter.execution_control().check_in(self)
        transporter_clones = transporter.clone_for_iterable()
        new_clones = []
        for transporter_clone in transporter_clones:
            new_transporter = transporter_clone    
            for articulator in self._articulators:
                new_transporter = articulator(new_transporter)
            new_clones.append(new_transporter)
        transporter.recompose(new_clones)            
        transporter.execution_control().check_out(self)
        return transporter

class ParallelStream(Articulator):
    '''
    Same of Stream, but it runs in parallel (threads)
    
    '''
    def __call__(self, transporter: Transporter):
        transporter.execution_control().check_in(self)
        transporter_clones = transporter.clone_for_iterable()
        def parallel_task(task_transporter: Transporter, task_articulators: List[Articulator]):
            new_transporter = task_transporter
            for articulator in task_articulators:
                new_transporter = articulator(new_transporter)
            return new_transporter
        result_transporters = RhThreads(parallel_task, transporter_clones, self._articulators).run()
        transporter.recompose(result_transporters)
        transporter.execution_control().check_out(self)
        return transporter
        
        
        

class Parallel(Articulator):
    '''
    Each articulator becomes a branch to parallel execution
    '''
    def __call__(self, transporter: Transporter):
        transporter.execution_control().check_in(self)
        n_branches = len(self._articulators)
        transporter_clones = transporter.clone(n_branches)
        branch_zip = zip(self._articulators, transporter_clones)
        def parallel_task(zip_articulators_transporter: Tuple[Articulator, Transporter], _ = None):
            articulator_task, transporter_task = zip_articulators_transporter
            print(transporter_task.data(), articulator_task.name)
            return articulator_task(transporter_task)
        result_transporters = RhThreads(parallel_task, branch_zip).run()
        transporter.recompose(result_transporters)
        transporter.execution_control().check_out(self)
        return transporter

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

    