
from rh_flow_control.controls import IndexControl, Transporter
import copy

class ExecutionTree():
    def __init__(self) -> None:
        self._nodes = []
    def add_node(self, node_index, node_name, node_type):
        self._nodes.append({
            'index': node_index,
            'name': node_name,
            'type': node_type
        })
    def get_nodes(self):
        return copy.deepcopy(self._nodes)

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
    def analyze(self, index_control: IndexControl, tree: ExecutionTree):
        index_control.next()
        node_type = self.type
        tree.add_node(index_control.getIndex(), self.name, node_type)
        if node_type != 'Execute':
            index_control.new_child_branch()
        for articulator in self._articulators:
            articulator.analyze(index_control, tree)
        if node_type != 'Execute':
            index_control.kill_child_branch()
        return tree
        
        
 