from queue import Queue
from rh_flow_control.output import FlowLogger, QueueBrokerAdapter, SimplePrintWorkerAdapter, SuperLogger, SuperPrinter

class DefaultDataFlow:
    def loggers(self):
        q = Queue()
        self.broker = QueueBrokerAdapter(q)
        super_logger = SuperLogger(self.broker)
        flow_logger = FlowLogger(super_logger)
        return flow_logger
    def printers(self, newPrinterAdapter = None):
        ## Printers
        printer_worker = newPrinterAdapter if newPrinterAdapter else SimplePrintWorkerAdapter()
        return SuperPrinter(self.broker, printer_worker)

