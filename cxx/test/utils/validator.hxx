#ifndef TEST_UTILS_VALIDATOR_HXX
#define TEST_UTILS_VALIDATOR_HXX

#include <nix/schema/validator.hxx>
#include <string>

namespace test {
namespace utils {

void dump_errors(const nix::SchemaValidator& validator);

void dump_errors(const nix::SchemaValidator::ErrorsMap_t& errors,
				 const std::string schema_id = std::string());

} // utils
} // test

#endif
