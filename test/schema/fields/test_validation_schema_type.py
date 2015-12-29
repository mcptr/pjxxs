import sys
import unittest
from unittest.mock import MagicMock, patch
from nose.tools import assert_true
from nose.tools import assert_false
from pjxxs import fields


mocked_mod_name = "mocked"
mocked = MagicMock()
inner_mocked = MagicMock()
inner_mocked.schema = fields.Schema("inner_mocked", 1)
inner_mocked.schema.add_field(fields.Object("inner_object"))
inner_mocked.schema.add_field(
	fields.Enum(
		"inner_enum", required=True, allowed_values=["ONE", "TWO"]
	)
)

with patch.dict("sys.modules", mocked=mocked, inner_mocked=inner_mocked):
	mocked.schema = fields.Schema(mocked_mod_name, 1)
	mocked.schema.add_field(fields.Object("mocked_object"))
	mocked.schema.add_field(
		fields.SchemaType("inner_mocked", "inner_mocked", nullable=False)
	)


class TestValidation(unittest.TestCase):
	def setUp(self):
		with patch.dict("sys.modules", mocked=mocked):
			schema = fields.Schema("main/schema", 1)
			schema.add_field(
				fields.SchemaType("level_1", mocked_mod_name, required=True)
			)
			self.schema = schema
			# print("\nDUMP", self.schema.to_json(sort_keys=True, indent=4))

	def test_001_validate_ok(self):
		cases = [
			dict(
				level_1=dict(
					mocked_object={},
					inner_mocked=dict(
						inner_object={},
						inner_enum="ONE"
					),
				)
			),
		]
		for data in cases:
			ok = self.schema.validate(data)
			# print(self.schema.get_errors())
			assert_true(ok)

	def test_002_validate_str_nok(self):
		cases = [
			dict(
				level_1=123
			),
			dict(
				level_1={}
			),
			dict(
				level_1=dict(
				)
			),
			dict(
				level_1=dict(
					inner_mocked=None
				)
			),
			dict(
				level_1=dict(
					inner_mocked=dict()
				)
			),
			dict(
				level_1=dict(
					mocked_object={},
					inner_mocked=dict(
						inner_object=None,
						inner_enum="INVALID"
					)
				),
			),
		]
		for data in cases:
			ok = self.schema.validate(data)
			# print(self.schema.get_errors(as_json=True))
			assert_false(ok)
