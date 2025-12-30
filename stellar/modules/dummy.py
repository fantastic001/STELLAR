
import pandas as pd
from stellar import StellarFunction, StellarExecution

class DummyFunction(StellarFunction):
    def __init__(self) -> None:
        super().__init__()
    
    def evaluate(self):
        return lambda: 0
    
    def name(self):
        return "dummy"

def register(execution: StellarExecution, **options):
    print(f"Registering Dummy module with options: {options}")
    execution.register_function(DummyFunction())