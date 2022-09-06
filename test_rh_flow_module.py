from ast import List
import unittest
from rh_flow_control.controls import STATUS_TYPE, DataStore, ExecutionControl, Transporter
from rh_flow_control.flow_control import Chain, Execute, Flow

### Functions
def load(_d, _ds, _lg, _fc):
    return [0, 1, 2, 3, 4, 5]
class MathOperation():
    def __init__(self, op:str, n: int) -> None:
        self._number = n
        self._op = op
    def __call__(self, _d, _ds, _lg, _fc) -> List(int):
        return [self._operation(self._op, n, self._number) for n in _d]
    def _operation(self, op: str, n1, n2):
        if op == 'add': return n1 + n2
        if op == 'sub': return n1 - n2
        if op == 'mult': return n1 * n2
        if op == 'div': return n1 / n2
        raise Exception('Invalid Operator')

## CONTROLS CLASSES
class TestExecutionControlClass(unittest.TestCase):
    '''
    ExecutionControl Class
    '''
    def setUp(self) -> None:
        self.execution_control = ExecutionControl()
    def test_instanciation(self):
        '''
        ExecutionControl: Class instanciation is empty
        '''
        self.assertEqual(self.execution_control.getIndex().getIndex(), '')
    def test_checkin_check_out_and_current_execution(self):
        '''
        ExecutionControl: Chain - Check-in, check-out and current index
        '''
        self.execution_control.check_in(Chain())
        self.execution_control.check_in(Execute(lambda x: 1))
        self.assertEqual(self.execution_control.getIndex().getIndex(), '0.0')
        self.execution_control.check_in(Execute(lambda x: 1))
        self.assertEqual(self.execution_control.getIndex().getIndex(), '0.1')
        self.execution_control.check_out(Chain())
        self.execution_control.check_in(Chain())
        self.assertEqual(self.execution_control.getIndex().getIndex(), '1.-1') ## Add a placehold for the child
        self.execution_control.check_in(Execute(lambda x: 1))
        self.execution_control.check_in(Execute(lambda x: 1))
        self.assertEqual(self.execution_control.getIndex().getIndex(), '1.1') ## Add a placehold for the child
        self.execution_control.check_out(Chain())
        self.execution_control.check_out(Chain())
        self.assertEqual(self.execution_control.getIndex().getIndex(), '') ## Add a placehold for the child
    def test_current_execution(self):
        '''
        ExecutionControl: CurrentExecution - check number of executions
        '''
        self.execution_control.check_in(Chain())
        self.execution_control.check_in(Execute(lambda x: 1))
        self.assertEqual(len(self.execution_control.current_execution().to_dict()), 2)
        self.execution_control.check_out(Execute(lambda x: 1))
        self.execution_control.check_in(Execute(lambda x: 1))
        self.execution_control.check_out(Execute(lambda x: 1))
        self.assertEqual(len(self.execution_control.current_execution().to_dict()), 1)
        self.execution_control.check_out(Chain())
        self.execution_control.check_in(Chain())
        self.assertEqual(len(self.execution_control.current_execution().to_dict()), 2) ## Add a placehold for the child
        self.execution_control.check_in(Execute(lambda x: 1))
        self.execution_control.check_out(Execute(lambda x: 1))
        self.execution_control.check_in(Execute(lambda x: 1))
        self.assertEqual(len(self.execution_control.current_execution().to_dict()), 3) ## Add a placehold for the child
        self.execution_control.check_out(Execute(lambda x: 1))
        self.execution_control.check_out(Chain())
        self.execution_control.check_out(Chain())
        self.assertEqual(len(self.execution_control.current_execution().to_dict()), 1) ## Add a placehold for the child
    def test_time_execution(self):
        '''
        ExecutionControl: CurrentExecution - Delta Time Execution
        '''
        self.execution_control.check_in(Chain())
        self.execution_control.check_in(Execute(lambda x: 1))
        self.execution_control.start_exec()
        self.execution_control.end_exec()
        self.assertLessEqual(self.execution_control.current_execution().get_execution(self.execution_control.getIndex()).delta_time, 0.01)
        

      
    
class TestTransporterClass(unittest.TestCase):
    '''
    Transporter
    '''
    def setUp(self) -> None:
        execution_control = ExecutionControl(Flow)
        data_store = DataStore()
        self._transporter = Transporter(execution_control, data_store)
    def test_instantiate_with_no_value(self):
        '''
        Test deliver None if it instantiate with no value. 
        '''
        self.assertEqual(self._transporter.data(), None)
    def test_receive_and_expose_data(self):
        '''
        Receive data and expose it
        '''
        data = 'My Data'
        transporter = self._transporter.receive_data(data)
        self.assertEqual(transporter.data(), data)
    def test_set_and_get_status(self):
        '''
        Transporter: set and get status
        '''
        transporter = self._transporter
        transporter.setStatus(STATUS_TYPE.NO_EXEC)
        self.assertEqual(str(transporter.status.name), 'NO_EXEC')
        

### FLOW_CONTROL CLASSES
class TestChainClass(unittest.TestCase):
    '''
    Chain Class
    '''
    def test_math_operations(self):
        '''
        Call Chain Articulator: Test math operation over a list of integers
        '''
        chain = Chain(
                    Execute(load),
                    Execute(MathOperation('add', 10)),
                    Execute(MathOperation('sub', 3)),
                    Execute(MathOperation('mult', 2))
                    )
        self.assertEqual(
            Flow(chain).run(),
            [14, 16, 18, 20, 22, 24]
        )

    

if __name__ == '__main__':
    unittest.main()