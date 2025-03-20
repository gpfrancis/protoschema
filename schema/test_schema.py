from unittest import TestCase
import unittest.main
import Schema


class TestSchema(TestCase):

    def test_schema_by_version(self):
        schema = Schema.get_schema("annotations", "7.4")
        self.assertEqual("annotations", schema.name)

    def test_annotation(self):
        schema = Schema.get_schema("annotations", "7.4")
        schema_dict = schema.dict()
        self.assertEqual("topic", schema_dict["fields"][2]["name"])
        self.assertEqual(str, schema_dict["fields"][2]["type"])
        self.assertEqual("auto increment counter", schema_dict["fields"][0]["doc"])
        self.assertEqual("NOT NULL AUTO_INCREMENT", schema_dict["fields"][0]["extra"])

    def test_objects(self):
        schema = Schema.get_schema("objects")
        schema_dict = schema.dict()
        self.assertEqual("diaObjectId", schema_dict["fields"][0]["name"])
        self.assertEqual("r_fpFluxMeanErr", schema_dict["fields"][100]["name"])

    def test_sql_create(self):
        schema = Schema.get_schema("objects")
        sql = schema.sql_create()
        self.assertEqual(3324, len(sql))

    def test_cql_create(self):
        schema = Schema.get_schema("diaSources")
        cql = schema.cql_create()
        print(len(cql))
        self.assertEqual(3663, len(cql))

    def test_html(self):
        schema = Schema.get_schema("objects")
        html = schema.html()
        self.assertEqual(12671, len(html))

    def test_alter_table_cql(self):
        cql = Schema.get_cql_alter("diaSources", "7.3", "7.4")
        self.assertEqual(118, len(cql))


if __name__ == '__main__':
    unittest.main()
