from stellar import StellarType
import pandas as pd 
import datetime

class NotNullIntType(StellarType):
    def evaluate(self):
        return lambda: lambda x: int(x) if not pd.isna(x) else 0
    def name(self):
        return "not_null_int"
    
class AccountingType(StellarType):
    def evaluate(self):
        lambda currency, separator, comma: lambda x: float(x.replace(currency, '').replace(separator, '').replace(comma, ".")) if not pd.isna(x) and x is not None else 0
    def name(self):
        return "accounting"

class ParsedDateType(StellarType):
    def evaluate(self):
        return lambda format: lambda x: datetime.datetime.strptime(x, format).date() if not pd.isna(x) and x is not None else None
    def name(self):
        return "parsed_date"

