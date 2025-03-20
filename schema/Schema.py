import re
import json

default_version = "7.4"


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
        raise ValueError(f"Unknown type {type_str}.")


class Schema:
    """Lasair Schema."""

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self._data = {}

    def load(self, schemafile: str = None):
        """Load the schema definition from file. Use the default location if not supplied.
        In general one should use get_schema instead of calling this directly.."""
        if schemafile is None:
            schemafile = re.sub("[._]", "/", self.version) + "/" + self.name + ".json"
        with open(schemafile) as f:
            self._data = json.load(f)

    def core_sections(self) -> list:
        """Get a list of core sections in the schema."""
        sections = []
        for section in self._data.get("sections", []):
            if not section.get("ext"):
                sections.append(section)
        return sections

    def ext_sections(self) -> list:
        """Get a list of extended sections in the schema."""
        sections = []
        for section in self._data.get("sections", []):
            if section.get("ext"):
                sections.append(section)
        return sections

    def sections(self) -> list:
        """Get a list of all sections in the schema."""
        return self._data.get("sections", [])

    def core_fields(self) -> list:
        """Get a (flattened) list of core fields in the schema (returns empty list if none)"""
        fields = []
        for section in self.core_sections():
            if not section.get("ext"):
                fields += section.get("fields", [])
        return fields

    def ext_fields(self) -> list:
        """Get a (flattened) list of extended fields in the schema (returns empty list if none)"""
        fields = []
        for section in self.ext_sections():
            if section.get("ext"):
                fields += section.get("fields", [])
        return fields

    def fields(self) -> list:
        """Get a (flattened) list of all fields in the schema (both core and extended)"""
        fields = []
        for section in self.sections():
            fields += section.get("fields", [])
        return fields

    def indexes(self):
        """Get the indexes for the schema (or None if no index section)"""
        return self._data.get("indexes")

    def dict(self) -> dict:
        """Return a python dict representation of the schema. Includes only fields (both core and extended),
        i.e. does not include indexes and flattens sections."""
        py_schema = {"fields": []}
        for field in self.fields():
            py_schema["fields"].append({
                "name": field.get("name"),
                "type": to_python_type(field.get("type")),
                "doc": field.get("doc"),
                "extra": field.get("extra"),
            })
        return py_schema

    def sql_create(self) -> str:
        """Return an SQL create table statement corresponding to the schema"""
        tablename = self.name
        lines = []
        for f in self.fields():
            s = '`' + f['name'] + '` '   # name with backquotes for SQL
            s += to_sql_type(f['type'])  # convert AVRO type to SQL type
            if 'default' in f:  # is there a DEFAULT
                s += ' DEFAULT ' + f['default']
            if 'extra' in f:  # is there an EXTRA
                s += ' ' + f['extra']
            lines.append(s)
        sql = 'CREATE TABLE IF NOT EXISTS ' + tablename + '(\n'
        sql += ',\n'.join(lines)
        if self.indexes():  # add in the INDEX
            sql += ',\n' + ',\n'.join(self.indexes())
        sql += '\n)\n'
        return sql

    def sql_alter(self) -> str:
        """Return an SQL alter table statement corresponding to the schema"""
        pass

    def cql_create(self) -> str:
        """Return a Cassandra CQL create table statement corresponding to the schema"""
        pass

    def cql_alter(self) -> str:
        """Return a Cassandra CQL alter table statement corresponding to the schema"""
        pass

    def json(self) -> str:
        """Return a JSON representation of the schema"""
        return json.dumps(self._data, indent=2)

    def html(self, headers=True, use_sections=True, include_ext=True) -> str:
        """Return a HTML representation of the schema."""
        html = ""
        if headers:
            html += f"<html>\n<head>\n<title>{ self.name }</title>\n</head>\n<body>\n"
            html += f"<h1>{ self.name }</h1>\n"
        use_sections = False
        if len(self.sections()) > 1:
            use_sections = True
        for s in self.sections():
            html += "<table>\n"
            html += f"<h2>{ s.get('section', '') }</h2>\n"
            html += f"<p>{ s.get('doc', '') }</p>\n"
            for f in s.get("fields", []):
                html += f"<tr><td>{ f.get('name', '') }</td><td>{ f.get('doc', '') }</td></tr>\n"
            html += "</table>\n"
        if headers:
            html += "</body>\n"
        return html


def get_schema(name: str, version: str = default_version) -> Schema:
    s = Schema(name, version)
    s.load()
    return s

