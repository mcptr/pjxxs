#include "tools/base.hxx"

#include <nix/schema.hxx>
#include <nix/schema/manager.hxx>
#include <string>
#include <iostream>


int main(int argc, char** argv)
{
	using std::string;
	using namespace test;

	UnitTest unit;

	unit.test_case(
		"SchemaManager::load/get",
		[](TestCase& test)
		{
			std::string data_dir = (
				test.get_config().base_dir + "/data/json/schema"
			);

			std::shared_ptr<nix::SchemaManager> mgr(
				new nix::SchemaManager(data_dir)
			);

			mgr->load("main");
			std::string main_schema_name = "main";
			std::string inner_schema_name = "inner";

			auto const main = mgr->get(main_schema_name);
			auto const inner = mgr->get(inner_schema_name);

			test.assert_true(
				!main->raw().toStyledString().empty(),
				"got data for " + main_schema_name
			);
			test.assert_true(
				!inner->raw().toStyledString().empty(),
				"got data for " + inner_schema_name
			);

			test.assert_equal(main->name(), main_schema_name);
			test.assert_equal(inner->name(), inner_schema_name);
		}
	);

	return unit.run(argc, argv);
}
