
from rh_flow_control.controls import Transporter


class Articulator():
    '''
    Definition: generic interface for flow control articulators, which defines specific king of flow. 
    '''
    def __init__(self, *articulators):
        self._articulators = articulators
        self._name = None
    def configs(self, name: str = ''):
        return self
    @property
    def name(self):
        return self._name if self._name else type(self).__name__
    @property
    def type(self):
        return type(self).__name__
    def __call__(self, transporter: Transporter):
        raise NotImplementedError()