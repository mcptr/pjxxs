#!/usr/bin/python3 -tt

from pjxxs.fields import *
from pjxxs import manager

schema = Schema("api/user", 1)
schema.add_field(String("user", nullable=False, required=True))
schema.add_field(String("password", nullable=False, required=True))
schema.add_field(Int("uid", nullable=False, required=True))


permissions = Array(
	"permissions",
	allowed_types=["Schema:api/permission"],
	default=[]
)

schema.add_field(permissions)

if __name__ == "__main__":
	print(schema.to_json(indent=4, sort_keys=True))
	data = {
		"user": "some user",
		"password": "secret",
		"uid": 1000,
		"permissions": {}
	}
	errors = {}
	ok = schema.validate(data, errors)
	print("Should fail:", errors)
	assert not ok

	data = {
		"user": "some user",
		"password": "secret",
		"uid": 1000,
		"permissions": []
	}
	errors = {}
	ok = schema.validate(data, errors)
	assert ok
	print("Should live", errors)

	data = {
		"user": "some user",
		"password": "secret",
		"uid": 1000,
		"permissions": [{
			"@id": "api/permission",
			"read": True,
			"write": True,
			"name": "ASD"
		}]
	}
	errors = {}
	ok = schema.validate(data, errors)
	assert ok
	print("Should live", errors)

	data = {
		"user": "some user",
		"password": "secret",
		"uid": 1000,
		"permissions": [{
			"@id": "api/permission",
			"read": True,
			"write": True,
		}]
	}
	errors = {}
	ok = schema.validate(data, errors)
	assert not ok
	print("Should fail", errors)
