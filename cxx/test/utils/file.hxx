#ifndef TEST_UTILS_FILE_HXX
#define TEST_UTILS_FILE_HXX

#include <string>


namespace test {
namespace utils {

void read_file_contents(const std::string& filename, std::string& dest);

} // utils
} // test

#endif


