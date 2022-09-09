from ast import List
from rh_flow_control.controls import Transporter
from rh_flow_control.flow_control import Chain, Execute, Flow
import time
from random import randint


### Functions
def load(_d, _ds, _lg, _fc):
    time.sleep(5)
    return [0, 1, 2, 3, 4, 5]
class MathOperation():
    def __init__(self, op:str, n: int) -> None:
        self._number = n
        self._op = op
    def __call__(self, _d, _ds, _lg, _fc) -> List(int):
        r = randint(1,5)
        time.sleep(r)
        return [self._operation(self._op, n, self._number) for n in _d]
    def _operation(self, op: str, n1, n2):
        if op == 'add': return n1 + n2
        if op == 'sub': return n1 - n2
        if op == 'mult': return n1 * n2
        if op == 'div': return n1 / n2
        raise Exception('Invalid Operator')

## Loggers
chain = Chain(
    Execute(load),
    Execute(MathOperation('add', 10)),
    Execute(MathOperation('sub', 3)),
    Execute(MathOperation('mult', 2))
    )

f = Flow(chain).run()

print('Resultado', f)

