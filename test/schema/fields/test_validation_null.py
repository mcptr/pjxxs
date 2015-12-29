import unittest
from nose.tools import assert_true
from nose.tools import assert_false
from pjxxs import fields


class TestValidation(unittest.TestCase):
	def setUp(self):
		schema = fields.Schema("main/schema", 1)
		# required should be forced to not required.
		schema.add_field(fields.Null("required", required=True))
		schema.add_field(fields.Null("not-required"))
		self.schema = schema
		# print(self.schema.to_json(sort_keys=True, indent=4))

	def test_001_validate_ok(self):
		errors = {}
		cases = [
			{},
			{
				"required" : None
			},
			{
				"required" : None,
				"not-required" : None,
			},
		]
		for data in cases:
			ok = self.schema.validate(data, errors)
			# print(errors)
			assert_true(ok)

	def test_002_validate_nok(self):
		errors = {}
		cases = [
			{
				"required" : "ASD"
			},
			{
				"required" : "test"
			},
			{
				"required" : None,
				"not-required" : 123,
			},
			{
				"required" : "asd",
				"not-required" : 123,
			},
		]
		for data in cases:
			ok = self.schema.validate(data, errors)
			# print("ERR", errors)
			assert_false(ok)
