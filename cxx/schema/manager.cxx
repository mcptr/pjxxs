#include "manager.hxx"
#include "nix/schema.hxx"
#include "nix/common.hxx"
#include "nix/util/fs.hxx"

#include <fstream>

namespace nix {

SchemaManager::SchemaManager(const std::string& path)
	: base_path_(path)
{
}

SchemaManager::~SchemaManager()
{
	schemas_.clear();
}

void SchemaManager::load_all()
{
	if(loaded_) {
		return;
	}

	util::fs::walk_files(
		base_path_,
		[this](const std::string& fpath) {
			this->load_from_file(fpath);
		}
	);

	loaded_  = true;
}

void SchemaManager::load_from_file(const std::string& path)
{
	// LOG(INFO) << "Loading schema: " << path;
	std::unique_ptr<SchemaData> schema_ptr(new SchemaData(shared_from_this()));
	schema_ptr->load(path);
	// LOG(INFO) << "Schema loaded: " << schema_ptr->name();
	if(this->schemas_.count(schema_ptr->name())) {
		throw std::runtime_error("Duplicate schema: " + schema_ptr->name());
	}
	this->schemas_.emplace(schema_ptr->name(), std::move(schema_ptr));
}

void SchemaManager::load(const std::string& schema_id)
{
	std::string full_path = base_path_ + "/" + schema_id + ".json";
	load_from_file(full_path);
}

std::unique_ptr<Schema> SchemaManager::get(const std::string& schema_id)
{
	if(!schemas_.count(schema_id)) {
		load(schema_id);
	}

	if(!schemas_.count(schema_id)) {
		throw std::runtime_error("Schema not found: " + schema_id);
	}
	std::unique_ptr<Schema> ptr(new Schema(schemas_[schema_id], shared_from_this()));
	return std::move(ptr);
								
}

} // nix
