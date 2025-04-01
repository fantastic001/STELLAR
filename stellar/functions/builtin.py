
from stellar import StellarFunction
import datetime

class SampleFuncion(StellarFunction):
    def evaluate(self):
        return lambda column: column.sample(frac=1)
    def name(self):
        return "sample"

class MeanFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.mean()
    def name(self):
        return "mean"

class SumFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.sum()
    def name(self):
        return "sum"
    
class CountFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.count()
    def name(self):
        return "count"

class MinFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.min()
    def name(self):
        return "min"

class MaxFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.max()
    def name(self):
        return "max"

class StdFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.std()
    def name(self):
        return "std"

class VarFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.var()
    def name(self):
        return "var"

class MedianFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.median()
    def name(self):
        return "median"

class ModeFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.mode()
    def name(self):
        return "mode"

class DateFunction(StellarFunction):
    def evaluate(self):
        return lambda y,m,d: datetime.date(y, m, d)
    def name(self):
        return "date"

class TodayFunction(StellarFunction):
    def evaluate(self):
        return lambda: datetime.date.today()
    def name(self):
        return "today"

class SubstrFunction(StellarFunction):
    def evaluate(self):
        return lambda column, sep, index: column.apply(lambda x: x.split(sep)[index]) if x is not None else ""
    def name(self):
        return "substr"

class ReplaceFunction(StellarFunction):
    def evaluate(self):
        return lambda column, old, new: column.str.replace(old, new)
    def name(self):
        return "replace"

class LineFunction(StellarFunction):
    def evaluate(self):
        return lambda column, index: column.apply(lambda x: x.split('\n')[index])
    def name(self):
        return "line"

class CastFunction(StellarFunction):
    def evaluate(self):
        return lambda column, dtype: column.astype(eval(dtype))
    def name(self):
        return "cast"

class LenFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.str.len()
    def name(self):
        return "len"


class LowerFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.str.lower()
    def name(self):
        return "lower"

class UpperFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.str.upper()
    def name(self):
        return "upper"

class StripFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.str.strip()
    def name(self):
        return "strip"

class LstripFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.str.lstrip()
    def name(self):
        return "lstrip"

class RstripFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.str.rstrip()
    def name(self):
        return "rstrip"

class TitleFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.str.title()
    def name(self):
        return "title"

class CapitalizeFunction(StellarFunction):
    def evaluate(self):
        return lambda column: column.str.capitalize()
    def name(self):
        return "capitalize"

