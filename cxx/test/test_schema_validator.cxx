#include "tools/base.hxx"
#include "utils/validator.hxx"
#include "utils/file.hxx"

#include <nix/schema.hxx>
#include <nix/schema/data.hxx>
#include <nix/schema/manager.hxx>
#include <nix/schema/validator.hxx>

#include <string>
#include <iostream>


int main(int argc, char** argv)
{
	using std::string;
	using namespace test;

	UnitTest unit;

	nix::SchemaValidator validator;

	unit.test_case(
		"Schema null, data null", 
		[&validator](TestCase& test)
		{
			nix::SchemaData schema;
			bool ok = validator.validate(schema.raw(), Json::nullValue);
			test::utils::dump_errors(validator);
			test.assert_true(ok, "Validates ok");
		}
	);

	unit.test_case(
		"Schema null, data non-null", 
		[&validator](TestCase& test)
		{
			nix::SchemaData schema;
			bool ok = validator.validate(schema.raw(), Json::objectValue);
			test::utils::dump_errors(validator);
			test.assert_false(ok, "Does not validate");
		}
	);

	unit.test_case(
		"Data as schema, invalid @id", 
		[&validator](TestCase& test)
		{
			Json::Value schema = Json::objectValue;
			schema["@id"] = "schema";
			Json::Value v = Json::objectValue;
			v["@id"] = "invalid";
			bool ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_false(ok, "Is invalid @id");
		}
	);

	unit.test_case(
		"Data as schema, correct @id", 
		[&validator](TestCase& test)
		{
			Json::Value schema = Json::objectValue;
			schema["@id"] = "schema";
			Json::Value v = Json::objectValue;
			v["@id"] = "schema";
			bool ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_true(ok, "Valid @id");
		}
	);

	unit.test_case(
		"Additional data", 
		[](TestCase& test)
		{
			nix::SchemaValidator validator;
			Json::Value schema = Json::objectValue;
			schema["@id"] = "schema";
			schema["bool"]["@properties"]["field_type"] = "Bool";
			schema["bool"]["@properties"]["required"] = false;
			Json::Value v = Json::objectValue;
			v["string"] = "value";

			bool ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_false(ok, "superfluous data found");

			schema["string"]["@properties"]["field_type"] = "String";
			schema["string"]["@properties"]["required"] = true;

			ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_true(ok, "data ok");

			v["nested"]["spam"] = "spam";
			ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_false(ok, "nested spam found");

			schema["nested"]["@properties"]["field_type"] = "Object";
			ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_true(ok, "nested ok,  spam allowed - any object");

			schema["nested"]["spam"]["@properties"]["required"] = true;
			ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_true(ok, "spam ok");
		}
	);

	unit.test_case(
		"Validate @properties.required", 
		[](TestCase& test)
		{
			nix::SchemaValidator validator;
			Json::Value schema = Json::objectValue;
			schema["@id"] = "schema";
			schema["bool"]["@properties"]["field_type"] = "Bool";
			schema["bool"]["@properties"]["required"] = true;
			Json::Value v = Json::objectValue;

			bool ok = validator.validate(schema, v);
			test.assert_false(ok, "'bool' field required");

			schema["bool"]["@properties"]["required"] = false;
			ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_true(ok, "'bool' field not required");
		}
	);

	unit.test_case(
		"Validate @properties.nullable", 
		[](TestCase& test)
		{
			nix::SchemaValidator validator;
			Json::Value schema = Json::objectValue;
			schema["@id"] = "schema";
			schema["bool"]["@properties"]["field_type"] = "Bool";
			schema["bool"]["@properties"]["nullable"] = false;
			Json::Value v = Json::objectValue;

			bool ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_false(ok, "null not allowed");

			schema["bool"]["@properties"]["nullable"] = true;
			ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_true(ok, "null allowed");
		}
	);

 	unit.test_case(
		"Validate @properties.allowed_types", 
		[](TestCase& test)
		{
			nix::SchemaValidator validator;
			Json::Value schema = Json::objectValue;
			schema["@id"] = "schema";
			schema["val"]["@properties"]["field_type"] = "String";
			schema["val"]["@properties"]["nullable"] = false;

			Json::Value ok_values;
			ok_values.append("string_val");

			Json::Value v = Json::objectValue;
			for(auto const& it : ok_values) {
				v["val"] = it;
				bool ok = validator.validate(schema, v);
				test::utils::dump_errors(validator);
				test.assert_true(ok, "type allowed");
			}

			Json::Value invalid_values;
			invalid_values.append(Json::nullValue);
			invalid_values.append(ok_values);
			invalid_values.append(123);

			for(auto const& it : invalid_values) {
				v["val"] = it;
				bool ok = validator.validate(schema, v);
				test::utils::dump_errors(validator);
				test.assert_false(ok, "invalid type");
			}
		}
	);

 	unit.test_case(
		"Validate @properties.allowed_types in array", 
		[](TestCase& test)
		{
			nix::SchemaValidator validator;
			Json::Value schema = Json::objectValue;
			schema["@id"] = "schema";
			schema["val"]["@properties"]["field_type"] = "Array";
			schema["val"]["@properties"]["nullable"] = false;
			schema["val"]["@properties"]["allowed_types"] = Json::arrayValue;
			schema["val"]["@properties"]["allowed_types"].append("str");
			schema["val"]["@properties"]["allowed_types"].append("int");


			Json::Value v;
			v["val"] = "invalid";
			bool ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_false(ok, "Cannot set non-list type as array");

			Json::Value valid_array;
			valid_array.append("valid");
			valid_array.append(123);
			v["val"] = valid_array;
			ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_true(ok, "Array containing valid data types");

			Json::Value invalid_array;
			invalid_array.append("valid string");
			invalid_array.append(Json::objectValue);
			v["val"] = invalid_array;
			ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_false(ok, "Array containing invalid data types");
		}
	);

 	unit.test_case(
		"Validate @properties.allowed_values", 
		[](TestCase& test)
		{
			nix::SchemaValidator validator;
			Json::Value schema = Json::objectValue;
			schema["@id"] = "schema";
			schema["val"]["@properties"]["field_type"] = "String";
			schema["val"]["@properties"]["nullable"] = false;

			schema["val"]["@properties"]["allowed_types"] = Json::arrayValue;
			schema["val"]["@properties"]["allowed_types"].append("str");

			schema["val"]["@properties"]["allowed_values"] = Json::arrayValue;
			schema["val"]["@properties"]["allowed_values"].append("one");

			Json::Value ok_values;
			ok_values.append("one");

			Json::Value v = Json::objectValue;
			for(auto const& it : ok_values) {
				v["val"] = it;
				bool ok = validator.validate(schema, v);
				test::utils::dump_errors(validator);
				test.assert_true(ok, "value allowed");
			}

			Json::Value invalid_values;
			invalid_values.append("invalid");
			invalid_values.append(321);
			invalid_values.append(false);
			invalid_values.append(true);
			invalid_values.append(Json::nullValue);
			invalid_values.append(Json::arrayValue);
			invalid_values.append(Json::objectValue);

			for(auto const& it : invalid_values) {
				v["val"] = it;
				bool ok = validator.validate(schema, v);
				test::utils::dump_errors(validator);
				test.assert_false(ok, "invalid value");
			}
		}
	);


 	unit.test_case(
		"Validate @properties.allowed_values in array", 
		[](TestCase& test)
		{
			nix::SchemaValidator validator;
			Json::Value schema = Json::objectValue;
			schema["@id"] = "schema";
			schema["val"]["@properties"]["field_type"] = "Array";
			schema["val"]["@properties"]["nullable"] = false;

			schema["val"]["@properties"]["allowed_types"] = Json::arrayValue;
			schema["val"]["@properties"]["allowed_types"].append("str");
			schema["val"]["@properties"]["allowed_types"].append("int");
			schema["val"]["@properties"]["allowed_types"].append("Schema:example");

			schema["val"]["@properties"]["allowed_values"] = Json::arrayValue;
			schema["val"]["@properties"]["allowed_values"].append("one");
			schema["val"]["@properties"]["allowed_values"].append(123);

			Json::Value array_ok;
			array_ok.append("one");
			array_ok.append(123);

			Json::Value v = Json::objectValue;
			v["val"] = array_ok;
			bool ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_true(ok, "values in array allowed");

			v["val"] = Json::objectValue;
			ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_false(ok, "cannot set object");

			Json::Value invalid_values;
			invalid_values.append("invalid");
			invalid_values.append(321);
			invalid_values.append(false);
			invalid_values.append(true);
			invalid_values.append(Json::nullValue);
			invalid_values.append(Json::objectValue);
			invalid_values.append(Json::arrayValue);

			v["val"] = invalid_values;
			ok = validator.validate(schema, v);
			test::utils::dump_errors(validator);
			test.assert_false(ok, "invalid value");
		}
	);


	unit.test_case(
		"Validate @properties.allowed_values Schema type in array", 
		[](TestCase& test)
		{
			std::string data_dir = (
				test.get_config().base_dir + "/data/json/schema"
			);

			std::shared_ptr<nix::SchemaManager> mgr(
				new nix::SchemaManager(data_dir)
			);

			mgr->load("validator/array_test");

			auto const schema = mgr->get("validator/array_test");
			test.assert_true(schema->validate(schema->as_data()), "Validates ok");

			Json::Value data = Json::objectValue;
			data["@id"] = "validator/array_test";
			data["elements"] = Json::arrayValue;
			data["elements"].append("invalid");

			bool ok = schema->validate(data);
			test::utils::dump_errors(schema->get_errors());
			test.assert_false(ok, "Element of invalid type");

			Json::Value element = Json::objectValue;
			element["@id"] = "validator/array_INVALID";

			data["elements"] = Json::arrayValue;
			data["elements"].append(element);

			ok = schema->validate(data);
			test::utils::dump_errors(schema->get_errors());
			test.assert_false(ok, "Element of invalid type (wrong schema id)");

			element["@id"] = "validator/array_element";

			data["elements"] = Json::arrayValue;
			data["elements"].append(element);

			ok = schema->validate(data);
			test::utils::dump_errors(schema->get_errors());
			test.assert_true(ok, "Element of valid type");

			element["string"] = 123;
			data["elements"] = Json::arrayValue;
			data["elements"].append(element);

			ok = schema->validate(data);
			test::utils::dump_errors(schema->get_errors());
			test.assert_false(ok, "element['string'] is invalid");

			element["string"] = "one";
			data["elements"] = Json::arrayValue;
			data["elements"].append(element);

			ok = schema->validate(data);
			test::utils::dump_errors(schema->get_errors());
			test.assert_true(ok, "element['string'] is valid");
		}
	);


	// unit.test_case(
	// 	"Arbitrary json tests", 
	// 	[](TestCase& test)
	// 	{
	// 	}
	// );


	return unit.run(argc, argv);
}

