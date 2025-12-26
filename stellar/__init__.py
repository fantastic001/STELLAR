
from ast import Tuple
import tatsu 
import pandas as pd 
import datetime 
from stellar.config import get_classes_inheriting


syntax = """


@@grammar::TableTransformer

start = 
    table_def:table_def 
        filters:filters 
        transformations:transformations
        export_defs:export_defs $ |
    table_def:table_def
        transformations:transformations
        export_defs:export_defs $ |
    table_def:table_def
        export_defs:export_defs $ |
    table_def:table_def $
    ;

table_def = "table" name:table_name "{" defs:column_defs "}" "from" src:table_source ;
filters = head:filter tail:filters | "directly" | head:filter ;
filter = "filter" condition:condition_expr;
transformations = head:transformation tail:transformations | head:transformation;
string = /\"[^\"]*\"/ ;

table_name =  /[A-Za-z][a-zA-Z0-9_]*/ | string ;
table_source = string:string "{" options:options "}" | string;
options = head:option tail:options | head:option;
option = /[A-Za-z_][A-Za-z_0-9]*/ ":" value;

column_defs = head:column_def "," tail:column_defs | head:column_def;
column_def = name:column_name ":" type:column_type "as" renamed:string | name:column_name ":" type:column_type;
column_name = string | /[A-Za-z_][A-Za-z_0-9]*/ ;
column_type = "int" | "float" | "str" | "bool" | "date" | "datetime" | func:function;


transformation =  debug:"print" "*" "where" condition:condition_expr |  debug:"print" col:column_name | "let" name:column_name "=" val:expression condition:condition;
expression = left:term op:"+" right:expression | left:term op:"-" right:expression | left:term;
term = left:factor op:"*" right:term | left:factor op:"/" right:term | left:factor;
factor = value:value | function:function | "(" expression:expression ")" | column_name:column_name;
value = number | string | "true" | "false" | "null";
number = /[0-9]+\\.?[0-9]*/;
function = name:function_name "(" args:arguments ")" | name:function_name "(" ")";
function_name = /[A-Za-z_][A-Za-z_0-9]*/;
arguments = head:expression "," tail:arguments | head:expression;

condition = all:"everywhere" | "if" expression:condition_expr ;
condition_expr = 
    | rel:"not" negated:condition_factor
    | left:condition_factor rel:"and" right:condition_expr 
    | left:condition_factor rel:"or" right:condition_expr 
    | left:condition_factor 
    ;
condition_factor = name:column_name op:operator expression:expression
    | "(" factor:condition_expr ")" 
    ;
operator = "<=" | ">=" | "=" | "!=" | "contains" | "<" | ">" | "like" ;

export_def = "export" name:table_name "to" src:table_source;
export_defs = head:export_def tail:export_defs | head:export_def;

"""


EXAMPLE = """
table sales {
    id: int,
    date: date,
    amount: float,
    is_paid: bool
} from "file://sales.csv" 
# {
#     header: 0
# }


# filter amount > 10000
filter is_paid = true

# let amount = amount * 1.1 if date > date(2020, 1, 1)
let amount = amount * 1.2 everywhere
let mean = mean(amount) everywhere 

export sales to "file://sales_transformed.csv"


"""
import re 

class StellarType:
    """
    This represents type of column which it can have.
    """
    def evaluate(self):
        """
        Returns function taking arguments which returns function taking column which it converts to given type.
        """
        raise NotImplementedError("Subclass must implement this method")

    def name(self):
        raise NotImplementedError("Subclass must implement this method")

    def __call__(self, *args):
        return self.evaluate()(*args)

class StellarFunction:
    """
    This represents function which can be applied to column.
    """
    def evaluate(self):
        """
        Returns function taking column which it applies to.
        """
        raise NotImplementedError("Subclass must implement this method")

    def name(self):
        raise NotImplementedError("Subclass must implement this method")

    def __call__(self, *args):
        return self.evaluate()(*args)


class StellarExecution:
    def __init__(self, 
        table_loader,
        filters: list,
        transformations: list,
        exporters: list):  
        self.table_loader = table_loader
        self.filters = filters
        self.transformations = transformations
        self.exporters = exporters

    def execute(self):
        df = self.load_table()
        df = self.apply_filters(df)
        df = self.apply_transformations(df)
        for exporter in self.exporters:
            exporter(df)
        return df
    
    def load_table(self):
        return self.table_loader()
    
    def apply_filters(self, df):
        for filter in self.filters:
            df = filter(df)
        return df

    def apply_transformations(self, df):
        for transformation in self.transformations:
            df = transformation(df)
        return df


def get_available_functions():
    functions = {}
    for f in get_classes_inheriting(StellarFunction):
        functions[f().name()] = f()
    return functions

def get_available_types():
    types = {}
    for t in get_classes_inheriting(StellarType):
        types[t().name()] = t()
    return types

class Semantics:

    def __init__(self):
        self.tn = None
        self.columns = {}
        self.export = None
        self.df = None 
    

    def table_def(self, ast):
        def loader():
            self.tn = ast.name 
            columns = {}
            for column_name, column_type, new_column_name in ast.defs:
                columns[column_name] = column_type
            schema, location, options = ast.src
            print("schema: ", schema)
            print("location: ", location)
            print("options: ", options)
            if schema == 'file' and location.endswith('.csv'):
                df = pd.read_csv(location, **options)
            elif schema == 'file' and location.endswith('.xlsx') or location.endswith('.xls'):
                df = pd.read_excel(location, dtype=str, **options)
            elif schema == 'db':
                pass 
            elif schema == 'api':
                pass
            elif schema == 'gdrive':
                pass
            elif schema == "exec":
                import subprocess 
                cmd = location
                if "output" not in options:
                    args = options.get("args", "")
                    if "args" in options:
                        del options["args"]
                    df = subprocess.check_output(
                        cmd +" "+ args, 
                        shell=True, 
                        **options
                    )
                else:
                    args = options.get("args", "")
                    if "args" in options:
                        del options["args"]
                    output = options["output"]
                    del options["output"]
                    subprocess.run(cmd + " " + args, shell=True, **options)
                    df = pd.read_csv(output)
            for column_name, column_type, new_column_name in ast.defs:
                if column_name not in df.columns:
                    df[column_name] = eval(column_type)()
                if not isinstance(column_type, str):
                    converter = column_type(df)
                    df[column_name] = df[column_name].apply(converter)
                else:
                    if column_type == 'date':
                        df[column_name] = df[column_name].apply(lambda x: datetime.date(*map(int, x.split('-'))))
                    elif column_type == 'datetime':
                        df[column_name] = pd.to_datetime(df[column_name])
                    elif column_type == 'int':
                        df[column_name] = df[column_name].astype(int)
                    elif column_type == 'float':
                        df[column_name] = df[column_name].astype(float)
                    elif column_type == 'str':
                        df[column_name] = df[column_name].apply(lambda x: str(x) if not pd.isna(x) else "")
                        df[column_name] = df[column_name].astype(str)
                    elif column_type == 'bool':
                        df[column_name] = df[column_name].astype(bool)
                if new_column_name != column_name:
                    df.rename(columns={column_name: new_column_name}, inplace=True)
            return df 
        return loader
    
    def column_def(self, ast):
        return ast.name, ast.type, ast.renamed if ast.renamed is not None else ast.name
    
    def filters(self, ast):
        filters = [] 
        if ast == 'directly':
            return filters
        if ast.tail is None:
            filters = [ast.head]
        else:
            filters =  [ast.head] + ast.tail
        return filters
    
    def filter(self, ast):
        condition = ast.condition
        def f(df):
            result = condition(df)
            return df[result]
        return f
    
    def transformations(self, ast):
        transformations = [] 
        if ast is None:
            return transformations
        if ast.tail is None:
            transformations = [ast.head]
        else:
            transformations =  [ast.head] + ast.tail
        return transformations 
    
    def transformation(self, ast):
        if ast.debug is not None and ast.condition is None:
            def f(df):
                print(df[ast.col])
                print("Columns in dataframe: " , df.columns)
                return df
            return f
        if ast.debug is not None and ast.condition is not None:
            def f(df):
                from pprint import pprint
                result = df[ast.condition(df)]
                for index, row in result.iterrows():
                    pprint(row.to_dict())
                print("Number of records: ", len(result))
                return df
            return f
        name = ast.name
        expression = ast.val
        condition = ast.condition
        def f(df):
            result = expression(df)
            if condition is not None:
                if name not in df.columns:
                    df[name] = pd.NA 
                df.loc[condition(df), name] = result
            else:
                if name not in df.columns:
                    df[name] = pd.NA
                df[name] = result
            return df
        return f
    
    def start(self, ast):
        table_loader = ast.table_def
        filters = ast.filters or []
        transformations = ast.transformations or []
        exporters = ast.export_defs or []
        execution = StellarExecution(
            table_loader=table_loader,
            filters=filters,
            transformations=transformations,
            exporters=exporters
        )
        return execution
    
    def string(self, ast):
        return "".join(ast[1:-1])
    
    def table_name(self, ast):
        return ast
    
    def table_source(self, ast):
        if isinstance(ast, str):
            string = ast
            schema = string.split('://')[0]
            location = string.split('://')[1] if "://" in string else ""
            options = {}
        else:
            string = ast.string 
            schema = string.split('://')[0]
            location = string.split('://')[1] if "://" in string else ""
            options = ast.options
        return schema, location, options
    
    def column_defs(self, ast):
        if ast.tail is None:
            return [ast.head]
        return [ast.head] + ast.tail
    
    def column_name(self, ast):
        return ast
    
    def column_type(self, ast):
        if isinstance(ast, str):
            return ast
        else:
            return ast.func
    
    def expression(self, ast):
        def f(df):
            if ast.op is None:
                return ast.left(df)
            left = ast.left
            right = ast.right
            if ast.op == '+':
                return left(df) + right(df)
            elif ast.op == '-':
                return left(df) - right(df)
        return f
        
    def term(self, ast):
        def f(df):
            if ast.op is None:
                return ast.left(df)
            left = ast.left
            right = ast.right
            if ast.op == '*':
                return left(df) * right(df)
            elif ast.op == '/':
                return left(df) / right(df)
        return f
    
    def factor(self, ast):
        def f(df):
            if ast.column_name is not None:
                return df[ast.column_name]
            elif ast.value is not None:
                return ast.value
            elif ast.function is not None:
                return ast.function(df)
            elif ast.expression is not None:
                return ast.expression(df)
        return f
    
    def value(self, ast):
        if ast == 'true':
            return True
        elif ast == 'false':
            return False
        elif ast == 'null':
            return None
        return ast
    
    def number(self, ast):
        if "." in ast:
            return float("".join(ast))
        else:
            return int("".join(ast))
    
    def function(self, ast):
        name = ast.name
        fs = {}
        fs.update(get_available_functions())
        fs.update(get_available_types())
        def f(df):
            args = []
            if ast.args is not None:
                args = [arg(df) for arg in ast.args]
            return fs[name](*args)
        return f
    
    def function_name(self, ast):
        return ast
    
    def arguments(self, ast):
        if ast.tail is None:
            return [ast.head]
        return [ast.head] + ast.tail
    
    def condition(self, ast):
        if ast.all == 'everywhere':
            return None
        return ast.expression
    
    def operator(self, ast):
        if ast == '<':
            return lambda x,y: x < y
        elif ast == '>':
            return lambda x,y: x > y
        elif ast == '<=':
            return lambda x,y: x <= y
        elif ast == '>=':
            return lambda x,y: x >= y
        elif ast == '=':
            return lambda x,y: x == y
        elif ast == '!=':
            return lambda x,y: x != y
        elif ast == "contains":
            return lambda x,y: x.str.contains(y) 
        elif ast == "like":
            return lambda x,y: x.str.replace(" ", "").str.lower().str.contains(y.replace(" ", "").lower())
    
    def export_def(self, ast):
        def f(df):
            name = ast.name
            if name != self.tn:
                raise ValueError(f"Export table name {name} does not match the table name {self.table_name}")
            schema, location, options = ast.src
            columns = df.columns
            if "columns" in options:
                columns = options["columns"].split(",")
                del options["columns"]
            df = df[columns]
            if schema == 'file' and location.endswith('.csv'):
                df.to_csv(location, **options)
            elif schema == 'file' and location.endswith('.xlsx'):
                df.to_excel(location, **options)
            elif schema == 'db':
                pass
            elif schema == 'api':
                pass
            elif schema == 'gdrive':
                pass
            elif schema == "none":
                pass 
            elif schema == "screen":
                if "groupby" in options:
                    df = df.groupby(options["groupby"])
                    operation = "sum"
                    if "operation" in options:
                        operation = options["operation"]
                    df = getattr(df[options["target"]], operation)()
                if "head" in options:
                    df = df.head(options["head"])
                if "tail" in options:
                    df = df.tail(options["tail"])
                if "unique" in options:
                    df = df[options["unique"]].unique()
                if isinstance(df, pd.DataFrame):
                    print(df.to_markdown())
                elif isinstance(df, pd.Series):
                    print(df.to_markdown())
                else:
                    for x in df:
                        print(x)
        return f
    
    def export_defs(self, ast):
        if ast is None:
            return []
        if ast.tail is None:
            return [ast.head]
        return [ast.head] + ast.tail

    def condition_expr(self, ast):
        def f(df):
            if ast.rel is None and ast.left is not None:
                return ast.left(df)
            left = ast.left
            right = ast.right
            if ast.rel == 'and':
                return left(df) & right(df)
            elif ast.rel == 'or':
                return left(df) | right(df)
            elif ast.rel == 'not':
                return ~ast.negated(df)
        return f
    
    def condition_factor(self, ast):
        def f(df):
            if ast.name is not None:
                return ast.op(df[ast.name], ast.expression(df))
            else:
                return ast.factor(df)
        return f

    def option(self, ast):
        return ast[0], ast[2]
    
    def options(self, ast):
        if ast.tail is None:
            return {
                ast.head[0]: ast.head[1]
            }
        return {
            ast.head[0]: ast.head[1],
            **ast.tail
        }

parser = tatsu.compile(syntax, semantics=Semantics())

def parse(text):
    # remove comments 
    text = re.sub(r'#.*', '', text)
    return parser.parse(text)


def run(text):
    execution = parse(text)
    print("Starting execution...")
    exported = execution.execute()
    return exported

def partial_parse(text) -> tuple[StellarExecution, str, str]:
    parsed_text = text 
    while len(parsed_text) > 0:
        try:
            result =  parse(parsed_text)
            remaining = text[len(parsed_text):]
            return result, parsed_text, remaining
        except tatsu.exceptions.FailedParse as e:
            # remove last line
            lines = parsed_text.splitlines()
            lines = lines[:-1]
            parsed_text = "\n".join(lines)
    return None, None, text
