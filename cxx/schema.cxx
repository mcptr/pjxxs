#include "schema.hxx"
#include "schema/manager.hxx"

#include "nix/common.hxx"
#include "nix/util/fs.hxx"

#include <fstream>
#include <vector>
#include <boost/filesystem.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string/predicate.hpp>

namespace nix {

Schema::Schema(std::shared_ptr<const SchemaData> data_ptr,
			   std::weak_ptr<SchemaManager> mgr)
	: data_ptr_(data_ptr),
	  mgr_(mgr)
{
}

bool Schema::validate(const Json::Value& data, int mask)
{
	validator_.reset(new SchemaValidator(mgr_, mask));
	return validator_->validate(*this, data);
}

const SchemaValidator::ErrorsMap_t& Schema::get_errors() const
{
	if(!validator_) {
		throw std::runtime_error(
			"Call validate() before get_errors()"
		);
	}
	return validator_->get_errors();
}

std::string Schema::extract_id(const std::string& type_id)
{
	std::vector<std::string> parts;
	boost::algorithm::split(parts, type_id, boost::is_any_of(":"));

	if(parts.size() != 2) {
		throw std::runtime_error(
			"Invalid Schema field specified: " + type_id
		);
	}

	return parts.at(1);
}

} // nix
