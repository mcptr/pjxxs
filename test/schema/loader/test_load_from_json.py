import sys
import unittest
from nose.tools import assert_equal
from unittest.mock import MagicMock, patch, mock_open
import json

from pjxxs import fields, loader


json_params = {
	"sort_keys" : True,
	"indent" : 4,
}

mocked_mod_name = "mocked"
mocked = MagicMock()
inner_mocked = MagicMock()

with patch.dict("sys.modules", mocked=mocked, inner_mocked=inner_mocked):
	mocked.schema = fields.Schema("mocked", 1)
	mocked.schema.add_field(fields.Object("mocked_object"))
	mocked.schema.add_field(
		fields.Enum(
			"mocked_enum", required=True, allowed_values=["ONE", "TWO"]
		)
	)

	inner_mocked.schema = fields.Schema("inner_mocked", 1)
	inner_mocked.schema.add_field(
		fields.Object("inner_mocked_object", nullable=True)
	)
	inner_mocked.schema.add_field(
		fields.Array("inner_mocked_array", allowed_values=["INNER", "MOCKED"])
	)
	mocked.schema.add_field(fields.SchemaType("inner_mocked_ref", "inner_mocked"))


class TestLoadFromJson(unittest.TestCase):
	def setUp(self):
		with patch.dict("sys.modules", mocked=mocked, inner_mocked=inner_mocked):
			schema = fields.Schema("test")
			obj = fields.Object("object_field", required=True)
			obj.add_field(fields.Object("object_field_inner", nullable=True))
			obj.add_field(
				fields.Array(
					"object_field_inner_array",
					nullable=True,
					allowed_types=[str, int],
					allowed_values=["value", 1, 2, 3]
				)
			)
			schema.add_field(obj)
			self.schema = schema

	def test_loader_without_schema(self):
		expected = self.schema.to_json(**json_params)
		m = mock_open(read_data=expected)
		with patch("os.path.isfile", return_value=True):
			with patch("pjxxs.loader.open", m, create=True):
				loader.set_base_path("")
				result_schema = loader.load_from_json("asd")
				result = result_schema.to_json(**json_params)
				assert_equal(result, expected, "schema")

	def test_loader_with_schema(self):
		with patch.dict("sys.modules", mocked=mocked, inner_mocked=inner_mocked):
			self.schema.add_field(
				fields.SchemaType("level_1", mocked_mod_name, required=True)
			)

			expected = self.schema.to_json(**json_params)
			m = mock_open(read_data=expected)
			with patch("os.path.isfile", return_value=True):
				with patch("pjxxs.loader.open", m, create=True):
					loader.set_base_path("")
					result_schema = loader.load_from_json("asd")
					result = result_schema.to_json(**json_params)
					# print(result)
					assert_equal(result, expected, "schema")
