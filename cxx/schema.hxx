#ifndef NIX_SCHEMA_HXX
#define NIX_SCHEMA_HXX

#include "schema/data.hxx"
#include "schema/validator.hxx"

#include <string>
#include <memory>

#include <jsoncpp/reader.h>
#include <jsoncpp/value.h>

namespace nix {

class SchemaManager;

class Schema
{
public:
	typedef SchemaValidator::ErrorsMap_t ErrorsMap_t;

	Schema() = delete;
	Schema(std::shared_ptr<const SchemaData> data_ptr,
		   std::weak_ptr<SchemaManager> mgr);

	virtual ~Schema() = default;

	bool validate(const Json::Value& data, int mask = 0);

	const ErrorsMap_t& get_errors() const;

	inline const Json::Value& as_data() const
	{
		return data_ptr_->as_data();
	}

	inline const std::string& path() const
	{
		return data_ptr_->path();
	}

	inline const std::string& name() const
	{
		return data_ptr_->name();
	}

	inline const Json::Value& raw() const
	{
		return data_ptr_->raw();
	}

	static std::string extract_id(const std::string& type_id);

protected:
	const std::shared_ptr<const SchemaData> data_ptr_;
	std::weak_ptr<SchemaManager> mgr_;
	std::unique_ptr<SchemaValidator> validator_;
};

} // nix


#endif
