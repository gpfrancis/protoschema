from unittest import TestCase
import unittest.main
import Schema

fields = [
    {"name": "id",       "type": "int",       "doc": "ID is of type int", "extra": "NOT_NULL"},
    {"name": "number1",  "type": "double",    "doc": "Number1 is of type double"},
    {"name": "number2",  "type": "float",     "doc": "Number2 is of type float"},
    {"name": "number3",  "type": "long",      "doc": "Number3 is of type long"},
    {"name": "number4",  "type": "string",    "doc": "Number4 is of type string"},
    {"name": "number5",  "type": "bigstring", "doc": "Number5 is of type bigstring"},
    {"name": "number6",  "type": "text",      "doc": "Number6 is of type text"},
    {"name": "number7",  "type": "timestamp", "doc": "Number7 is of type timestamp"},
    {"name": "number8",  "type": "JSON",      "doc": "Number8 is of type JSON"},
    {"name": "number9",  "type": "char",      "doc": "Number9 is of type char"},
    {"name": "number10", "type": "boolean",   "doc": "Number10 is of type boolean"},
    {"name": "number11", "type": "blob",      "doc": "Number11 is of type blob"},
]


class TestSchema(TestCase):

    def test_python(self):
        schema = Schema.Schema()
        schema.name = "testing"
        schema.fields = fields
        schema_dict = schema.dict()
        self.assertEqual(schema_dict["fields"][0]["type"], int)
        self.assertEqual(schema_dict["fields"][1]["type"], float)

    def test_schema_by_version(self):
        schema = Schema.get_by_version("testschema", "7.4")
        self.assertEqual(schema.name, "testschema")


if __name__ == '__main__':
    unittest.main()
