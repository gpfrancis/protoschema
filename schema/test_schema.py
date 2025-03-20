from unittest import TestCase
import unittest.main
import Schema


class TestSchema(TestCase):

    def test_schema_by_version(self):
        schema = Schema.get_schema("annotations", "7.4")
        self.assertEqual(schema.name, "annotations")

    def test_annotation(self):
        schema = Schema.get_schema("annotations", "7.4")
        schema_dict = schema.dict()
        self.assertEqual(schema_dict["fields"][2]["name"], "topic")
        self.assertEqual(schema_dict["fields"][2]["type"], str)
        self.assertEqual(schema_dict["fields"][0]["doc"], "auto increment counter")
        self.assertEqual(schema_dict["fields"][0]["extra"], "NOT NULL AUTO_INCREMENT")

    def test_objects(self):
        schema = Schema.get_schema("objects")
        schema_dict = schema.dict()
        self.assertEqual(schema_dict["fields"][0]["name"], "diaObjectId")
        self.assertEqual(schema_dict["fields"][100]["name"], "r_fpFluxMeanErr")

    def test_sql_create(self):
        schema = Schema.get_schema("objects")
        sql = schema.sql_create()
        self.assertEqual(len(sql), 3324)

    def test_html(self):
        schema = Schema.get_schema("objects")
        html = schema.html()
        self.assertEqual(len(html), 12671)


if __name__ == '__main__':
    unittest.main()
