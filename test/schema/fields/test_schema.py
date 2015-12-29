import sys
import unittest
from nose.tools import assert_equal
from unittest.mock import MagicMock, patch
import json

from pjxxs import fields

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
	inner_mocked.schema.add_field(fields.Object("inner_mocked_object"))
	mocked.schema.add_field(fields.SchemaType("inner_mocked_ref", "inner_mocked"))


class TestValidation(unittest.TestCase):
	def setUp(self):
		with patch.dict("sys.modules", mocked=mocked, inner_mocked=inner_mocked):
			schema = fields.Schema("test")
			schema.add_field(fields.String("string_field"))
			schema.add_field(fields.Int("int_field", nullable=True))
			obj = fields.Object("obj")
			obj.add_field(fields.SchemaType("level_1", mocked_mod_name, required=True))
			inner_object = fields.Object("inner_object", required=True)
			inner_object.add_field(fields.Object("inner_inner_object", required=True))
			obj.add_field(inner_object)
			inner_array = fields.Array("inner_array", allowed_types=[str, int])
			inner_array.append(fields.String("")).append(fields.Array(""))
			obj.add_field(inner_array).add_field(fields.String("inner_field"))
			arr = fields.Array("array")
			arr.append(
				fields.String(""),
				fields.Int(""),
				fields.Bool(""),
				fields.Double("")
			)
			schema.add_field(arr)
			schema.add_field(obj)
			self.schema = schema

	def test_structure(self):
		expected = {
			"@id": "test",
			"@version": 0,
			"array": {
				"@properties": {
					"nullable": False,
					"allowed_types": [],
					"allowed_values": [],
					"field_type": "Array",
					"required": False
				}
			},
			"int_field": {
				"@properties": {
					"nullable": True,
					"allowed_types": [
						"int",
						"float",
					],
					"allowed_values": [],
					"field_type": "Int",
					"required": False
				}
			},
			"obj": {
				"@properties": {
					"nullable": False,
					"allowed_types": [
						"dict"
					],
					"allowed_values": [],
					"field_type": "Object",
					"required": False
				},
				"inner_array": {
					"@properties": {
						"nullable": False,
						"allowed_types": [
							"int",
							"str"
						],
						"allowed_values": [],
						"field_type": "Array",
						"required": False
					}
				},
				"inner_field": {
					"@properties": {
						"nullable": False,
						"allowed_types": [
							"str"
						],
						"allowed_values": [],
						"field_type": "String",
						"required": False
					}
				},
				"inner_object": {
					"@properties": {
						"nullable": False,
						"allowed_types": [
							"dict"
						],
						"allowed_values": [],
						"field_type": "Object",
						"required": True
					},
					"inner_inner_object": {
						"@properties": {
							"nullable": False,
							"allowed_types": [
								"dict"
							],
							"allowed_values": [],
							"field_type": "Object",
							"required": True
						}
					}
				},
				"level_1": {
					"@properties": {
						"nullable": False,
						"allowed_types": [
							"dict"
						],
						"allowed_values": [],
						"field_type": "Schema:mocked",
						"required": True,
					},
					"inner_mocked_ref": {
						"@properties": {
							"nullable": False,
							"allowed_types": [
								"dict"
							],
							"allowed_values": [],
							"field_type": "Schema:inner_mocked",
							"required": False,
						},
						"inner_mocked_object": {
							"@properties": {
								"nullable": False,
								"allowed_types": [
									"dict"
								],
								"allowed_values": [],
								"field_type": "Object",
								"required": False
							}
						}
					},
					"mocked_enum": {
						"@properties": {
							"nullable": False,
							"allowed_types": [
								"str"
							],
							"allowed_values": [
								"ONE",
								"TWO"
							],
							"field_type": "Enum",
							"required": True
						}
					},
					"mocked_object": {
						"@properties": {
							"nullable": False,
							"allowed_types": [
								"dict"
							],
							"allowed_values": [],
							"field_type": "Object",
							"required": False
						}
					}
				}
			},
			"string_field": {
				"@properties": {
					"nullable": False,
					"allowed_types": [
						"str"
					],
					"allowed_values": [],
					"field_type": "String",
					"required": False
				}
			}
		}

		assert_equal(
			self.schema.to_json(**json_params),
			json.dumps(expected, **json_params)
		)

	def test_inner_schema(self):
		with patch.dict("sys.modules", mocked=mocked, inner_mocked=inner_mocked):
			schema = fields.Schema("test")
			schema.add_field(
				fields.SchemaType("level_1", mocked_mod_name, required=True)
			)
			result = schema.to_json(**json_params)

			expected = {
				"@id": "test",
				"@version": 0,
				"level_1": {
					"@properties": {
						"nullable": False,
						"allowed_types": [
							"dict"
						],
						"allowed_values": [],
						"field_type": "Schema:mocked",
						"required": True
					},
					"inner_mocked_ref": {
						"@properties": {
							"nullable": False,
							"allowed_types": [
								"dict"
							],
							"allowed_values": [],
							"field_type": "Schema:inner_mocked",
							"required": False
						},
						"inner_mocked_object": {
							"@properties": {
								"nullable": False,
								"allowed_types": [
									"dict"
								],
								"allowed_values": [],
								"field_type": "Object",
								"required": False
							}
						}
					},
					"mocked_enum": {
						"@properties": {
							"nullable": False,
							"allowed_types": [
								"str"
							],
							"allowed_values": [
								"ONE",
								"TWO"
							],
							"field_type": "Enum",
							"required": True
						}
					},
					"mocked_object": {
						"@properties": {
							"nullable": False,
							"allowed_types": [
								"dict"
							],
							"allowed_values": [],
							"field_type": "Object",
							"required": False
						}
					}
				}
			}
			assert_equal(result, json.dumps(expected, **json_params), "schema")
