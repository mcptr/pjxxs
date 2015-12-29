import unittest
from nose.tools import assert_true
from nose.tools import assert_false
from pjxxs import fields


class TestValidation(unittest.TestCase):
	def setUp(self):
		schema = fields.Schema("main/schema", 1)
		schema.add_field(fields.Bool("non-nullable", required=True))
		schema.add_field(fields.Bool("nullable", nullable=True))
		self.schema = schema
		# print(self.schema.to_json(sort_keys=True, indent=4))

	def test_001_validate_ok(self):
		errors = {}
		cases = [
			{
				"non-nullable" : True
			},
			{
				"non-nullable" : False,
			},
			{
				"non-nullable" : True,
				"nullable" : None,
			},
		]
		for data in cases:
			ok = self.schema.validate(data, errors)
			assert_true(ok)

	def test_002_validate_nok(self):
		errors = {}
		cases = [
			{
			},
			{
				"non-nullable" : None,
			},
			{
				"non-nullable" : 17,
			},
			{
				"non-nullable" : "ASD",
				"nullable" : "asd",
			},
		]
		for data in cases:
			ok = self.schema.validate(data, errors)
			# print(errors)
			assert_false(ok)
