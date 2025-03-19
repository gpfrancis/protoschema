from importlib import import_module


def to_python_type(type_str: str):
    """Convert a string representation of a type to a python type"""
    if type_str == "char":
        return str
    if type_str == "string":
        return str
    if type_str == "bigstring":
        return str
    if type_str == "text":
        return str
    if type_str == "double":
        return float
    if type_str == "timestamp":
        return float
    if type_str == "long":
        return int
    if type_str == "JSON":
        return dict
    if type_str == "boolean":
        return bool
    if type_str == "blob":
        return bytes
    else:
        return eval(type_str)


def to_sql_type(type_str: str) -> str:
    if type_str == 'float':
        return 'float'
    elif type_str == 'double':
        return 'double'
    elif type_str == 'int':
        return 'int'             # 31 bit with sign
    elif type_str == 'long':
        return 'bigint'          # 63 bit with sign
    elif type_str == 'bigint':
        return 'bigint'          # 63 bit with sign
    elif type_str == 'date':
        return 'datetime(6)'
    elif type_str == 'string':
        return 'varchar(16)'
    elif type_str == 'bigstring':
        return 'varchar(80)'
    elif type_str == 'text':
        return 'text'
    elif type_str == 'timestamp':
        return 'timestamp'
    elif type_str == 'JSON':
        return 'JSON'
    else:
        raise(ValueError(f"Unknown type {type_str}."))


class Schema:
    """Abstract parent class for Lasair Schemata."""

    # populate the name and fields attributes to create a schema
    name = ""
    fields = []

    def dict(self) -> dict:
        """Return a python dict representation of the scehma"""
        py_schema = {"fields": []}
        for field in self.fields:
            py_schema["fields"].append({
                "name": field.get("name"),
                "type": to_python_type(field.get("type")),
                "doc": field.get(""),
            })
        return py_schema

    def sql(self) -> str:
        """Return an SQL create table statement corresponding to the schema"""
        pass

    def cql(self) -> str:
        """Return a Cassandra CQL create table statement corresponding to the schema"""
        pass

    def json(self) -> str:
        """Return a JSON representation of the scehma"""
        pass

    def html(self) -> str:
        """Return a HTML representation of the scehma"""
        pass


def get_by_version(schema: str, version: str) -> Schema:
    schema_module = import_module(f"{version}.{schema}")
    schema_class = getattr(schema_module, schema)
    schema_inst = schema_class()
    return schema_inst
