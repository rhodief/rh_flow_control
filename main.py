from typing import List
from rh_flow_control.controls import Transporter
from rh_flow_control.flow_control import Chain, Execute, Flow, Parallel, ParallelStream, Stream
import time
from random import randint


### Functions
def load(_d, _ds, _lg, _fc):
    time.sleep(5)
    return [0, 1, 2, 3, 4, 5]
class MathOperation():
    def __init__(self, op:str, n: int, is_iter = True) -> None:
        self._number = n
        self._op = op
        self._is_iter = is_iter
    def __call__(self, _d, _ds, _lg, _fc) -> List[int]:
        time.sleep(1)
        if self._is_iter: return [self._operation(self._op, n, self._number) for n in _d]
        return self._operation(self._op, _d, self._number)
    def _operation(self, op: str, n1, n2):
        try:
            if op == 'add': return n1 + n2
            if op == 'sub': return n1 - n2
            if op == 'mult': return n1 * n2
            if op == 'div': return n1 / n2
            raise Exception('Invalid Operator')
        except:
            print(op, n1, n2)
        

## Loggers
'''
chain = Chain(
    Execute(load),
    Execute(MathOperation('add', 10)),
    Execute(MathOperation('sub', 3)),
    Execute(MathOperation('mult', 2))
    )

'''

'''
chain = Chain(Execute(load))
stream = Stream(
    Execute(MathOperation('add', 10, False)),
    Execute(MathOperation('sub', 3, False)),
    Execute(MathOperation('mult', 2, False))
)
'''


'''
chain = Chain(Execute(load))
stream = ParallelStream(
    Execute(MathOperation('add', 10, False)),
    Execute(MathOperation('sub', 3, False)),
    Execute(MathOperation('mult', 2, False))
)
'''
main_chain = Chain(Execute(load))
chain = Chain(
    Execute(MathOperation('add', 10)),
    Execute(MathOperation('sub', 3)),
    Execute(MathOperation('mult', 2))
)
stream = ParallelStream(
    Execute(MathOperation('add', 10, False)),
    Execute(MathOperation('sub', 3, False)),
    Execute(MathOperation('mult', 2, False))
)
parallel = Parallel(
    chain,
    stream
)


#f = Flow(chain, stream).run()
f = Flow(main_chain, parallel).analyze().get_nodes()

print('Resultado', f)

