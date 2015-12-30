#ifndef NIX_SCHEMA_DATA_HXX
#define NIX_SCHEMA_DATA_HXX

#include <string>
#include <memory>

#include <jsoncpp/reader.h>
#include <jsoncpp/value.h>

namespace nix {

class SchemaManager;

class SchemaData
{
public:
	SchemaData() = default;
	SchemaData(std::weak_ptr<SchemaManager> mgr);

	explicit SchemaData(const Json::Value& data);
	explicit SchemaData(const std::string& data);
	virtual ~SchemaData() = default;

	int version() const;
	void load(const std::string& path);
	void parse(const std::string& data);
	const Json::Value& as_data() const;

	inline const std::string& path() const
	{
		return path_;
	}

	inline const std::string& name() const
	{
		return name_;
	}

	inline const Json::Value& raw() const
	{
		return root_;
	}

protected:
	std::string path_ = std::string();
	std::string name_ = std::string();
	int version_ = 0;
	Json::Value root_ = Json::nullValue;
	Json::Value data_ = Json::nullValue;

	// need this to build able to load nested schemas
	std::weak_ptr<SchemaManager> mgr_;

	void build();
	void build_data(Json::Value& root,
					Json::Value& data,
					const std::string& k = std::string());

	void build_field(Json::Value& root,
					 Json::Value& data,
					 const std::string& k = std::string());

	template<class T>
	void set_field_default(const Json::Value& prop,
						   Json::Value& data,
						   const T& default_value = T()) const
	{
		
		if(prop["nullable"].asBool()) {
			data = Json::nullValue;
		}
		else if(prop.isMember("default")) {
			data = prop["default"];
		}
		else {
			data  = default_value;
		}
	}
};

} // nix


#endif
