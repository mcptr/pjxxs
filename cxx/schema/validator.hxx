#ifndef NIX_SCHEMA_VALIDATOR_HXX
#define NIX_SCHEMA_VALIDATOR_HXX

#include <jsoncpp/value.h>
#include <string>
#include <unordered_map>
#include <vector>
#include <memory>

namespace nix {

class Schema;
class SchemaManager;

class SchemaValidator
{
public:
	static constexpr int DISABLE_SUPERFLUOUS_CHECK = 1;

	typedef std::vector<std::string> ErrorsList_t;
	typedef std::unordered_map<std::string, ErrorsList_t> ErrorsMap_t;

	SchemaValidator() = default;
	SchemaValidator(std::weak_ptr<SchemaManager> mgr, int mask = 0);
	virtual ~SchemaValidator() = default;

	bool validate(const Schema& schema,
				  const Json::Value& data);

	bool validate(const Json::Value& schema,
				  const Json::Value& data);

	inline const ErrorsMap_t& get_errors() const
	{
		return errors_;
	}

	inline const std::string& get_schema_id() const
	{
		return schema_id_;
	}

protected:
	std::weak_ptr<SchemaManager> mgr_;
	const int mask_ = 0;
	std::string data_path_;
	ErrorsMap_t errors_;
	std::string schema_id_;

	void set_schema_id(const Json::Value& root);

	void register_error(const std::string& msg,
						const std::string& k = std::string(),
						int idx = -1);

	bool recurse_validate(const Json::Value& root,
						  const Json::Value& data);

	bool validate_required(const Json::Value& properties,
						   const Json::Value& data,
						   const std::string& k);

	bool validate_nullable(const Json::Value& properties,
						   const Json::Value& data,
						   const std::string& k);

	bool validate_allowed_types(const Json::Value& properties,
								const Json::Value& data,
								const std::string& k);

	bool validate_allowed_values(const Json::Value& properties,
								 const Json::Value& data,
								 const std::string& k);

	bool validate_field(const Json::Value& properties,
						const Json::Value& data,
						const std::string& k);

	bool validate_constraints(const Json::Value& properties,
							  const Json::Value& data,
							  const std::string& k);

	bool validate_schemas(const Json::Value& data,
						  const std::string& k);

	bool validate_schema_type(const Json::Value& value);

	bool validate_superfluous_data(const Json::Value& root,
								   const Json::Value& data);

	bool is_type_allowed(const std::string& type,
						 const Json::Value& data);

	bool is_value_allowed(const Json::Value& data,
						  const Json::Value& choices);

	bool find_in_allowed_types(const Json::Value& value,
							   const Json::Value& choices);

	bool is_configured(int option) const;

	// type specific validators
	bool validate_string_constraints(const Json::Value& properties,
									 const Json::Value& data,
									 const std::string& k);

};

} // nix

#endif
