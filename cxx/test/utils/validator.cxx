#include "validator.hxx"
#include <nix/common.hxx>

namespace test {
namespace utils {

void dump_errors(const nix::SchemaValidator& validator)
{
	dump_errors(validator.get_errors(), validator.get_schema_id());
}

void dump_errors(const nix::SchemaValidator::ErrorsMap_t& errors,
				 const std::string schema_id)
{
	if(errors.size() && schema_id.length()) {
		LOG(ERROR) << "\nErrors for schema: "
				   << schema_id;
	}

	for(auto const& entry : errors) {
		for(auto const& err : entry.second) {
			LOG(ERROR) << entry.first << ": " << err;
		}
	}
}

} // utils
} // test
