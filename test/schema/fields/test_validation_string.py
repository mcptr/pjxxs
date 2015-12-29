import unittest
from nose.tools import assert_true
from nose.tools import assert_false
from pjxxs import fields


class TestValidation(unittest.TestCase):
	def setUp(self):
		schema = fields.Schema("main/schema", 1)
		schema.add_field(fields.String("non-nullable", required=True, default="asd"))
		schema.add_field(fields.String("nullable", nullable=True))
		schema.add_field(
			fields.String(
				"strict_value",
				nullable=True,
				allowed_values=["one", "two"]
			)
		)
		schema.add_field(
			fields.String(
				"len_value",
				nullable=True,
				min_len=3,
				max_len=6
			)
		)
		self.schema = schema
		# print(self.schema.to_json(sort_keys=True, indent=4))

	def test_001_validate_str_ok(self):
		errors = {}
		cases = [
			{
				"non-nullable" : "value"
			},
			{
				"non-nullable" : "",
			},
			{
				"non-nullable" : "",
				"nullable" : None,
			},
			{
				"non-nullable" : "",
				"nullable" : None,
				"strict_value" : "one"
			},
			{
				"non-nullable" : "",
				"len_value" : "123"
			},
			{
				"non-nullable" : "",
				"len_value" : "123456"
			},
		]
		for data in cases:
			ok = self.schema.validate(data, errors)
			assert_true(ok)

	def test_002_validate_str_nok(self):
		cases = [
			{
			},
			{
				"non-nullable" : 13,
			},
			{
				"non-nullable" : "",
				"nullable" : 17,
				"strict_value" : "invalid"
			},
			{
				"non-nullable" : "",
				"len_value" : "1"
			},
			{
				"non-nullable" : "",
				"len_value" : "1234567"
			},
		]
		for data in cases:
			ok = self.schema.validate(data)
			# print(self.schema.get_errors(as_json=True))
			assert_false(ok)
