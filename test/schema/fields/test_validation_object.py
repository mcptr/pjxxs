import unittest
from nose.tools import assert_true
from nose.tools import assert_false
from pjxxs import fields


class TestValidation(unittest.TestCase):
	def setUp(self):
		schema = fields.Schema("main/schema", 1)
		obj_1 = fields.Object("object_1", required=True)
		obj_2 = fields.Object("object_2", nullable=True)
		obj_2.add_field(
			fields.Array("obj2_arr", nullable=True, allowed_types=[int, dict])
		)
		obj_3 = fields.Object("object_3", nullable=True)
		obj_3.add_field(
			fields.Object("obj_3_inner_1", required=True, default={}, nullable=False)
		)
		schema.add_field(obj_1)
		schema.add_field(obj_2)
		schema.add_field(obj_3)
		self.schema = schema
		# print(self.schema.to_json(sort_keys=True, indent=4))

	def test_001_validate_ok(self):
		errors = {}
		cases = [
			dict(
				object_1={},
				object_2=None,
				object_3=None,
			),
			dict(
				object_1={},
				object_2={},
				object_3=None,
			),
			dict(
				object_1={},
				object_2={},
				object_3=dict(
					obj_3_inner_1=dict(another_level=987123)
				),
			),
			dict(
				object_1=dict(test=123),
				object_2=dict(
					test=123,
					obj2_arr=None
				),
				object_3=None,
			),
			dict(
				object_1=dict(test=123),
				object_2=dict(
					test=123,
					obj2_arr=[]
				),
				object_3=None,
			),
			dict(
				object_1=dict(test=123),
				object_2=dict(
					test=123,
					obj2_arr=[123, dict(qwe=234)]
				),
				object_3=dict(
					obj_3_inner_1={}
				),
			),
			dict(
				object_1=dict(test=123),
				object_2=dict(
					test=123,
					obj2_arr=[123, dict(qwe=234)]
				),
				object_3=dict(obj_3_inner_1=dict(test=[123123, {}])),
			),
		]
		for data in cases:
			ok = self.schema.validate(data, errors)
			# print(errors)
			assert_true(ok)

	def test_002_validate_nok(self):
		errors = {}
		cases = [
			dict(
			),
			dict(
				object_1={},
				object_2="not an object",
				object_3=123,
			),
			dict(
				object_1={},
				object_2={},
				object_3=dict(
					obj_3_inner_1="should be an object"
				),
			),
			dict(
				object_1=["should be an object"],
				object_2=dict(
					obj2_arr=[123, "string not allowed"]
				),
				object_3=dict(obj_3_inner_1="should be an object"),
			),
		]
		for data in cases:
			ok = self.schema.validate(data, errors)
			# print("ERR", errors)
			assert_false(ok)
