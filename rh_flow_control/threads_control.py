from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List
from rh_flow_control.controls import Transporter
from rh_flow_control.model import Articulator


class RhThreads():
    def __init__(self, task_callable: Callable, transporters: List[Transporter], articulators: List[Articulator] = [], n_workers: int = 10) -> None:
        self._n_workers = n_workers
        self._task_callable = task_callable
        self._transporters = transporters
        self._articulators = articulators
    def run(self):
        with  ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._task_callable,transporter, self._articulators) for transporter in self._transporters]
            return [future.result() for future in futures]
                
    
        