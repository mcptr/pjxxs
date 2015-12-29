import unittest
from nose.tools import assert_true
from nose.tools import assert_false
from pjxxs import fields


class TestValidation(unittest.TestCase):
	def setUp(self):
		schema = fields.Schema("main/schema", 1)
		schema.add_field(fields.Array("array_1", required=True))
		schema.add_field(fields.Array("array_2", default=[]))
		schema.add_field(
			fields.Array(
				"array_3",
				nullable=True,
				required=True,
				allowed_types=[str, int],
				allowed_values=["one", "two", 543],
				default=[],
			)
		)
		self.schema = schema
		# print(self.schema.to_json(sort_keys=True, indent=4))

	def test_001_validate_ok(self):
		errors = {}
		cases = [
			dict(
				array_1=[],
				array_2=[],
				array_3=[],
			),
			dict(
				array_1=["test", 123, [], {}],
				array_2=[],
				array_3=None,
			),
			dict(
				array_1=["test", 123, [], {}],
				array_2=[],
				array_3=[],
			),
			dict(
				array_1=["test", 123, [], {}],
				array_2=["test", 123, 124, "qwe"],
				array_3=[],
			),
			dict(
				array_1=["test", 123, [], {}],
				array_2=["test", 123, 124, "qwe"],
				array_3=["one", "two", 543],
			),
		]
		for data in cases:
			ok = self.schema.validate(data, errors)
			# print(errors)
			assert_true(ok)

	@unittest.skip
	def test_002_validate_nok(self):
		cases = [
			dict(
				array_2=None,
				array_3=[],
			),
			dict(
				array_1=[],
				array_2=None,
				array_3=["invalid value"],
			),
			dict(
				array_1=[],
				array_2=[],
				array_3=["asd", 123.0, [], "this is ok", {}],
			),
		]
		for data in cases:
			ok = self.schema.validate(data)
			# print("ERR", schema.get_errors())
			assert_false(ok)
