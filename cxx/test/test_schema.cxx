#include "tools/base.hxx"
#include "utils/validator.hxx"
#include "utils/file.hxx"

#include <nix/schema.hxx>
#include <nix/schema/manager.hxx>
#include <nix/schema/validator.hxx>

#include <string>
#include <iostream>


int main(int argc, char** argv)
{
	using std::string;
	using namespace test;

	UnitTest unit;

	unit.test_case(
		"Schema as_data()", 
		[](TestCase& test)
		{
			std::string exp_dir = (
				test.get_config().base_dir + "/data/json/expected"
			);

			// SchemaManager inherits 'enable_shared_from_this',
			// keep it in a shared_ptr
			std::shared_ptr<nix::SchemaManager> mgr(
				new nix::SchemaManager(
					test.get_config().base_dir + "/data/json/schema"
				)
			);

			mgr->load("main");

			auto const main_schema = mgr->get("main");
			auto const inner_schema = mgr->get("inner");

			std::string main_expected;
			std::string inner_expected;

			test::utils::read_file_contents(
				exp_dir + "/inner_schema_data.json",
				inner_expected
			);

			test::utils::read_file_contents(
				exp_dir + "/main_schema_data.json",
				main_expected
			);

			test.assert_equal(
				inner_schema->as_data().toStyledString(),
				inner_expected,
				"inner_schema.as_data()"
			);

			test.assert_equal(
				main_schema->as_data().toStyledString(),
				main_expected,
				"main_schema.as_data()"
			);

		}
	);

	unit.test_case(
		"Schema validate empty data", 
		[](TestCase& test)
		{
			std::string exp_dir = (
				test.get_config().base_dir + "/data/json/expected"
			);

			std::shared_ptr<nix::SchemaManager> mgr(
				new nix::SchemaManager(
					test.get_config().base_dir + "/data/json/schema"
				)
			);

			mgr->load("main");

			auto const main_schema = mgr->get("main");
			nix::SchemaValidator validator;
			bool ok  = validator.validate(*main_schema, main_schema->as_data());
			test::utils::dump_errors(validator);

			test.assert_true(ok, "Validates ok");
		}
	);

	return unit.run(argc, argv);
}

