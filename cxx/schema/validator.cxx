#include "validator.hxx"
#include "nix/schema.hxx"
#include "nix/schema/manager.hxx"
#include "nix/common.hxx"

#include <memory>
#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string/predicate.hpp>

namespace nix {

SchemaValidator::SchemaValidator(std::weak_ptr<SchemaManager> mgr, int mask)
	: mgr_(mgr),
	  mask_(mask)
{
}

void SchemaValidator::set_schema_id(const Json::Value& root)
{
	schema_id_ = root["@id"].asString();
}

void SchemaValidator::register_error(const std::string& msg,
									 const std::string& k,
									 int idx)
{
	std::string err_k = data_path_;
	if(!k.empty()) {
		if(!err_k.empty()) {
			err_k.append(".");
		}
		err_k.append(k);
		if(idx > -1) {
			err_k.append("[" + std::to_string(idx) + "]");
		}
	}

	errors_[err_k].push_back(msg);
}


bool SchemaValidator::validate(const Schema& schema,
							   const Json::Value& data)
{
	return validate(schema.raw(), data);
}

bool SchemaValidator::validate(const Json::Value& schema,
							   const Json::Value& data)
{
	set_schema_id(schema);
	errors_.clear();

	if(schema.isNull()) {
		if(data.isNull()) {
			return true;
		}
		else {
			register_error("Data must be null");
			return false;
		}
	}

	if(schema.isMember("@properties")) {
		if(schema["@properties"]["nullable"].asBool() && data.isNull()) {
			register_error("Cannot be null");
			return true;
		}
	}

	if(!data.isObject()) {
		register_error("Invalid data - should be an object");
		return false;
	}

	if(data.isMember("@id")) {
		std::string schema_id = schema["@id"].asString();
		if(data["@id"].asString().compare(schema_id) != 0) {
			register_error("Expected schema '" + schema_id + "'");
			return false;
		}
	}

	return recurse_validate(schema, data);
}

bool SchemaValidator::recurse_validate(const Json::Value& root,
									   const Json::Value& data)
{
	if(!is_configured(DISABLE_SUPERFLUOUS_CHECK) &&
	   !validate_superfluous_data(root, data)) {
		return false;
	}

	for(auto const& k : root.getMemberNames()) {
		if(k.at(0) != '@') {
			if(!validate_field(root[k], data, k)) {
				return false;
			}
			if(data.isMember(k) && data[k].isObject()) {
				if(!recurse_validate(root[k], data[k])) {
					return false;
				}
			}
		}
	}
	return true;
}

bool SchemaValidator::validate_field(const Json::Value& root,
									 const Json::Value& data,
									 const std::string& k)
{
	const Json::Value& properties = root["@properties"];

	if(properties.isMember("required") && !data.isMember(k)) {
		if(!validate_required(properties, data, k)) {
			register_error("Required", k);
			return false;
		}
		return true;
	}

	if(data[k].isNull()) {
		if(!validate_nullable(properties, data[k], k)) {
			register_error("Cannot be null", k);
			return false;
		}
		return true;
	}

	bool t_allowed = is_type_allowed(
		properties["field_type"].asString(),
		data[k]
	);

	if(!t_allowed) {
		register_error("Invalid type " + properties["field_type"].asString(), k);
		return false;
	}
	else if(!validate_allowed_types(properties, data, k)) {
		return false;
	}

	if(!validate_constraints(properties, data, k)) {
		return false;
	}

	if(!validate_schemas(data, k)) {
		return false;
	}

	return validate_allowed_values(properties, data, k);
}

bool SchemaValidator::validate_required(const Json::Value& properties,
										const Json::Value& data,
										const std::string& k)
{
	if(properties.isMember("required") && properties["required"].asBool())
	{
		return data.isMember(k);
	}
	return true;
}

bool SchemaValidator::validate_nullable(const Json::Value& properties,
										  const Json::Value& data,
										  const std::string& k)
{
	if(properties.isMember("nullable") &&
	   properties["nullable"] != Json::nullValue)
	{
		bool nullable = properties["nullable"].asBool();
		if(!nullable) {
			return !data.isNull();
		}
	}
	return true;
}

bool SchemaValidator::validate_allowed_types(const Json::Value& properties,
											 const Json::Value& data,
											 const std::string& k)
{
	if(properties.isMember("allowed_types") &&
	   properties["allowed_types"].isArray())
	{
		if(properties["field_type"].compare("Array") == 0) {
			if(!data[k].isArray()) {
				register_error("Must be an array", k);
				return false;
			}

			int idx = 0;
			for(auto const& dit : data[k]) {
				if(!find_in_allowed_types(dit, properties["allowed_types"])) {
					register_error("Type not allowed in array", k, idx);
					return false;
				}
				idx++;
			}
		}
		else {
			if(!find_in_allowed_types(data[k], properties["allowed_types"])) {
				register_error("Type not allowed", k);
				return false;
			}
		}
	}

	return true;
}

bool SchemaValidator::find_in_allowed_types(const Json::Value& value,
											const Json::Value& choices)
{
	bool ok = !choices.size();
	for(auto const& it : choices) {
		if(is_type_allowed(it.asString(), value)) {
			ok = true;
			break;
		}
	}
	return ok;
}

bool SchemaValidator::validate_allowed_values(const Json::Value& properties,
											  const Json::Value& data,
											  const std::string& k)
{
	if(properties.isMember("allowed_values") &&
	   properties["allowed_values"].isArray() &&
	   properties["allowed_values"].size())
	{
		if(data[k].isArray() &&
		   (properties["field_type"].compare("Array") == 0))
		{
			int idx = 0;
			for(auto const& v : data[k]) {
				if(!is_value_allowed(v, properties["allowed_values"])) {
					register_error("Value not allowed", k, idx);
					return false;
				}
				idx++;
			}
		}
		else {
			if(!is_value_allowed(data[k], properties["allowed_values"])) {
				register_error("Value not allowed", k);
				return false;
			}
		}
	}

	return true;
}

bool SchemaValidator::is_type_allowed(const std::string& type,
									  const Json::Value& data)
{
	std::string t = boost::algorithm::to_lower_copy(type);

	if(t.compare("bool") == 0 && !(data.isBool() || data.isInt()))
	{
		return false;
	}

	if((t.compare("str") == 0 ||
		t.compare("string") == 0 ||
		t.compare("enum") == 0) && !data.isString())
	{
		return false;
	}

	if(t.compare("int") == 0 && !(data.isDouble() || data.isIntegral()))
	{
		return false;
	}

	if((t.compare("double") == 0 ||
		t.compare("numeric") == 0 ||
		t.compare("float") == 0 ||
		t.compare("time") == 0)
	   && !(data.isDouble() || data.isInt()))
	{
		return false;
	}

	if((t.compare("object") == 0 ||
		t.compare("dict") == 0) && !data.isObject())
	{
		return false;
	}

	if((t.compare("array") == 0 ||
		t.compare("list") == 0) && !data.isArray())
	{
		return false;
	}

	if(t.compare("null") == 0 && !data.isNull()) {
		return false;
	}

	if(boost::starts_with(type, "Schema:")) {
		std::string id = Schema::extract_id(type);
		return (
			data.isObject() &&
			data.isMember("@id") &&
			(data["@id"].asString().compare(id) == 0)
		);
	}

	return true;
}

bool SchemaValidator::validate_superfluous_data(const Json::Value& root,
												const Json::Value& data)
{
	bool is_strict = false;
	bool is_object = (root["@properties"]["field_type"] == "Object");

	// if data type was defined as object, without any keys
	// specified - we need to allow arbitrary content
	if(is_object) {
		for(auto const& k_it : root.getMemberNames()) {
			if(k_it.at(0) != '@') {
				is_strict = is_configured(DISABLE_SUPERFLUOUS_CHECK);
				break;
			}
		}
	}

	for(auto const& d_it : data.getMemberNames()) {
		if(d_it.at(0) != '@') {
			if(!root.isMember(d_it)) {
				if(!is_object || is_strict) {
					register_error("Superfluous data", d_it);
					return false;
				}
			}
		}
	}

	return true;
}

bool SchemaValidator::is_value_allowed(const Json::Value& data,
									   const Json::Value& choices)
{
	bool found = false;
 	Json::ValueIterator it = choices.begin();
	for( ; it != choices.end(); it++) {
		if(data == *it) {
			found = true;
			break;
		}
	}
	return found;

}

bool SchemaValidator::validate_schemas(const Json::Value& data,
									   const std::string& k)
{
	if(data[k].isArray()) {
		std::size_t idx = 0;
		for(auto const& v : data[k]) {
			if(!validate_schema_type(v)) {
				register_error("Invalid data for schema", k, idx);
				return false;
			}
			idx++;
		}
		return true;
	}
	else if(!validate_schema_type(data[k])) {
		register_error("Invalid data for schema", k);
		return false;
	}

	return true;
}

bool SchemaValidator::validate_schema_type(const Json::Value& value)
{
	auto mgr_ptr_ = mgr_.lock();
	if(!mgr_ptr_) {
		LOG(WARNING) << "validate_schema_type(): "
					 << "returning true without checks";
		return true;
	}

	if(value.isObject() && value.isMember("@id")) {
		std::string id = value["@id"].asString();
		auto schema = mgr_ptr_->get(id);

		bool ok = schema->validate(value);
		if(!ok) {
			for(auto const& entry : schema->get_errors()) {
				for(auto const& err : entry.second) {
					LOG(ERROR) << "INNER: " << entry.first << ": " << err;
				}
			}
		}

		return ok;
	}
	return true;
}

bool SchemaValidator::validate_constraints(const Json::Value& properties,
										   const Json::Value& data,
										   const std::string& k)
{
	std::string ftype = boost::algorithm::to_lower_copy(
		properties["field_type"].asString()
	);

	if(ftype.compare("str") == 0 || ftype.compare("string") == 0) {
		return validate_string_constraints(properties, data, k);
	}

	return true;
}

bool SchemaValidator::is_configured(int option) const
{
	return ((mask_ & option) == option);
}

bool SchemaValidator::validate_string_constraints(
	const Json::Value& properties,
	const Json::Value& data,
	const std::string& k)
{
	std::string v = data[k].asString();
	if(!properties["min_len"].isNull()) {
		std::size_t min_len = properties["min_len"].asInt();
		if(v.length() < min_len) {
			register_error(
				"String value too short (<" + std::to_string(min_len) + ")",
				k
			);
			return false;
		}
	}

	if(!properties["max_len"].isNull()) {
		std::size_t max_len = properties["max_len"].asInt();
		if(v.length() > max_len) {
			register_error(
				"String value too long (>" + std::to_string(max_len) + ")",
				k
			);
			return false;
		}
	}

	// TODO: check format

	return true;
}


} // nix
