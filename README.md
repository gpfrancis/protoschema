# protoschema

Prototyping an idea for how to handle Lasair schemata.

The idea is to store the schema as JSON rather than directly as python.
All schemata use the same format as `objects` with sections, which can optionally be marked as extended;
we use accessor methods, e.g. `fields()`, `ext_fields()`, to deal with this.

## Examples

Get the annotations schema:
```
schema = Schema.get_schema("annotations", "7.4")
```

Get the schema as a list of sections, excluding any marked as extended, e.g. for the web interface:
```
sections = schema.core_sections()
```

Get the schmea as a Python dict, e.g. for features:
```
schema_dict = schema.dict()
```

Get the SQL "CREATE TABLE" statement for a schema:
```
sql = schema.sql_create()
```

Get the SQL "ALTER TABLE" statement needed to migrate from version 7.3 to 7.4:
```
cql = Schema.get_cql_alter("diaSources", "7.3", "7.4")
```