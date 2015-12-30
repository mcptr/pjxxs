#ifndef NIX_SCHEMA_MANAGER_HXX
#define NIX_SCHEMA_MANAGER_HXX

#include "data.hxx"

#include <string>
#include <unordered_map>
#include <memory>

#include <jsoncpp/reader.h>
#include <jsoncpp/value.h>

namespace nix {

class Schema;

/*
 * NOTE: SchemaManager passes itself to Schema objects in order to allow
 * them to mgr->get() other schemas when needed.
 * It inherits std::enable_shared_from_this and thus must itself be owned
 * by std::shared_ptr (as in Module::API)
 */

class SchemaManager : public std::enable_shared_from_this<SchemaManager>
{
public:
	SchemaManager() = delete;
	explicit SchemaManager(const std::string& path);
	virtual ~SchemaManager();

	std::unique_ptr<Schema> get(const std::string& schema_id);
	void load_all();
	void load(const std::string& schema_id);
	void load_from_file(const std::string& path);
protected:

	typedef std::unordered_map<
		std::string, const std::shared_ptr<const SchemaData>> SchemaMap_t;

	const std::string base_path_;
	SchemaMap_t schemas_;
	bool loaded_ = false;

};

} // nix


#endif
