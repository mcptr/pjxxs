#include "data.hxx"
#include "manager.hxx"
#include "nix/schema.hxx"
#include "nix/common.hxx"
#include "nix/util/fs.hxx"

#include <fstream>
#include <vector>
#include <boost/filesystem.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string/predicate.hpp>

namespace nix {

SchemaData::SchemaData(const Json::Value& data)
{
	root_ = data;
}

SchemaData::SchemaData(std::weak_ptr<SchemaManager> mgr)
	: mgr_(mgr)
{
}

SchemaData::SchemaData(const std::string& data)
{
	parse(data);
	build();
}

int SchemaData::version() const
{
	return version_;
}

void SchemaData::load(const std::string& path)
{
	namespace fs = boost::filesystem;

	if(!fs::is_regular_file(path)) {
		throw std::runtime_error("Schema not found: " + path);
	}
	std::ifstream file(path);
	Json::Reader reader;
	if(!reader.parse(file, root_, false)) {
		LOG(ERROR) << "Cannot parse schema file: " << path;
		throw std::runtime_error(reader.getFormattedErrorMessages());
	}
	file.close();
	name_ = root_["@id"].asString();
	version_ = root_["@version"].asInt();
	path_ = path;
	LOG(DEBUG) << "Schema " << name_;
	build();
}

void SchemaData::parse(const std::string& data)
{
	Json::Reader reader;
	if(!reader.parse(data, root_, false)) {
		LOG(ERROR) << "Cannot parse schema data: " << data;
		throw std::runtime_error(reader.getFormattedErrorMessages());
	}

	name_ = root_["@id"].asString();
	version_ = root_["@version"].asInt();
	path_ = std::string();
	LOG(DEBUG) << "Schema " << name_;
	build();
}

const Json::Value& SchemaData::as_data() const
{
	return data_;
}

void SchemaData::build()
{
	data_["@id"] = root_["@id"].asString();
	data_["@version"] = root_["@version"].asInt();
	build_data(root_, data_);
}

void SchemaData::build_data(Json::Value& root,
						Json::Value& data,
						const std::string& k)
{
	if(!root.size()) {
		return;
	}

	for(auto const& k : root.getMemberNames()) {
		if(k.at(0) != '@') {
			build_field(root[k], data, k);
			if(data.isMember(k) && data[k].isObject()) {
				build_data(root[k], data[k]);
			}
		}
	}
}

void SchemaData::build_field(Json::Value& root,
						 Json::Value& data,
						 const std::string& k)
{
	data[k] = Json::nullValue;

	const Json::Value& prop = root["@properties"];
	std::string field_type = prop["field_type"].asString();

	if(field_type.compare("Object") == 0) {
		set_field_default(prop, data[k], Json::objectValue);
	}
	else if(field_type.compare("Array") == 0) {
		set_field_default(prop, data[k], Json::arrayValue);
	}
	else if(field_type.compare("String") == 0) {
		set_field_default(prop, data[k], std::string());
	}
	else if(field_type.compare("Int") == 0) {
		set_field_default(prop, data[k], 0LL);
	}
	else if(field_type.compare("Double") == 0 ||
			field_type.compare("Numeric") == 0 ||
			field_type.compare("Time") == 0)
	{
		set_field_default(prop, data[k], (double) 0.0);
	}
	else if(field_type.compare("Bool") == 0) {
		set_field_default(prop, data[k], false);
	}
	else if(field_type.compare("Null") == 0) {
		set_field_default(prop, data[k], Json::nullValue);
	}
	else if(field_type.compare("Enum") == 0) {
		set_field_default(prop, data[k], Json::nullValue);
	}
	else if(boost::starts_with(field_type, "Schema:")) {
		std::shared_ptr<SchemaManager> manager = mgr_.lock();
		if(!manager) {
			throw std::runtime_error("Unable to load schema (no manager)");
		}
		auto s = manager->get(Schema::extract_id(field_type));
		set_field_default(prop, data[k], s->as_data());

		// copy schema definition into root
		const Json::Value& s_ref = s->raw();
		for(auto const& k : s_ref.getMemberNames()) {
			root[k] = s_ref[k];
		}
	}
	else {
		throw std::runtime_error(
			"Unknown type: " + field_type + " at " + k
		);
	}
}

} // nix
