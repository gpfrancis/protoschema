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


def to_cql_type(type_str: str) -> str:
    if type_str == 'float':
        return 'float'
    elif type_str == 'double':
        return 'double'
    elif type_str == 'int':
        return 'int'  # 31 bit with sign
    elif type_str == 'long':
        return 'bigint'  # 63 bit with sign
    elif type_str == 'bigint':
        return 'bigint'  # 63 bit with sign
    elif type_str == 'string':
        return 'ascii'
    elif type_str == 'char':
        return 'ascii'
    elif type_str == 'boolean':
        return 'boolean'
    elif type_str == 'blob':
        return 'blob'
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
        lines = []
        for f in self.fields():
            s = '`' + f['name'] + '` '   # name with backquotes for SQL
            s += to_sql_type(f['type'])  # convert AVRO type to SQL type
            if 'default' in f:  # is there a DEFAULT
                s += ' DEFAULT ' + f['default']
            if 'extra' in f:  # is there an EXTRA
                s += ' ' + f['extra']
            lines.append(s)
        sql = 'CREATE TABLE IF NOT EXISTS ' + self.name + '(\n'
        sql += ',\n'.join(lines)
        if "indexes" in self._data:  # add in the INDEX
            sql += ',\n' + ',\n'.join(self._data["indexes"])
        sql += '\n)\n'
        return sql

    def cql_create(self) -> str:
        """Return a Cassandra CQL create table statement corresponding to the schema"""
        lines = []
        for f in self.fields():
            s = '"' + f['name'] + '" '   # name with double quotes for CQL
            s += to_cql_type(f['type'])  # convert AVRO type to CQL type
            if 'extra' in f:  # is there an EXTRA
                s += ' ' + f['extra']
            lines.append(s)
        cql = 'CREATE TABLE IF NOT EXISTS ' + self.name + '(\n'
        cql += ',\n'.join(lines)
        if "indexes" in self._data:  # add in the INDEX
            cql += ',\n' + ',\n'.join(self._data["indexes"])
        cql += '\n)\n'
        if "with" in self._data:  # add in the WITH at the very end
            cql += self._data["with"] + '\n'
        return cql

    def json(self) -> str:
        """Return a JSON representation of the schema"""
        return json.dumps(self._data, indent=2)

    def html(self, headers=True, use_sections=True, include_ext=True) -> str:
        """Return a HTML representation of the schema."""
        html = ""
        if headers:
            html += f"<html>\n<head>\n<title>{ self.name }</title>\n</head>\n<body>\n"
            html += f"<h1>{ self.name }</h1>\n"
        if include_ext:
            secs = self.sections()
        else:
            secs = self.core_sections()
        for s in secs:
            if use_sections:
                html += f"<h2>{ s.get('section', '') }</h2>\n"
                html += f"<p>{ s.get('doc', '') }</p>\n"
            html += "<table>\n"
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


def get_sql_alter(name: str, old_version: str, new_version: str) -> str:
    """For the given schema, find differences between old_version and new_version
    and return an ALTER_TABLE SQL statement"""
    old_schema = get_schema(name, old_version)
    new_schema = get_schema(name, new_version)
    fields_old = old_schema.fields()
    fields_new = new_schema.fields()
    attr_old = [f['name'] for f in fields_old if 'name' in f]
    attr_new = [f['name'] for f in fields_new if 'name' in f]

    lines = ''
    # What needs to be ADDed to get the new schema
    for f in fields_new:
        if 'name' not in f:
            continue
        if f['name'] in attr_old:
            continue
        lines += 'ALTER TABLE %s ADD `%s` %s;\n' % (name, f['name'], to_sql_type(f['type']))
    # What needs to be DROPped to get the new schema
    for f in fields_old:
        if 'name' not in f:
            continue
        if f['name'] in attr_new:
            continue
        lines += 'ALTER TABLE %s DROP COLUMN `%s` %s\n;' % (name, f['name'], to_sql_type(f['type']))
    return lines


def get_cql_alter(name: str, old_version: str, new_version: str) -> str:
    """For the given schema, find differences between old_version and new_version
    and return an ALTER_TABLE CQL statement"""
    old_schema = get_schema(name, old_version)
    new_schema = get_schema(name, new_version)
    fields_old = old_schema.fields()
    fields_new = new_schema.fields()
    attr_old = [f['name'] for f in fields_old if 'name' in f]
    attr_new = [f['name'] for f in fields_new if 'name' in f]

    lines = ''
    # What needs to be ADDed to get the new schema
    for f in fields_new:
        if 'name' not in f:
            continue
        if f['name'] in attr_old:
            continue
        lines += 'ALTER TABLE %s ADD "%s" %s;\n' % (name, f['name'], to_cql_type(f['type']))
    # What needs to be DROPped to get the new schema
    for f in fields_old:
        if 'name' not in f:
            continue
        if f['name'] in attr_new:
            continue
        lines += 'ALTER TABLE %s DROP `%s` %s;\n' % (name, f['name'], to_cql_type(f['type']))
    return lines
