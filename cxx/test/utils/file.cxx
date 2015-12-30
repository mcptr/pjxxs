#include "file.hxx"
#include <fstream>
#include <stdexcept>

namespace test {
namespace utils {

void read_file_contents(const std::string& filename, std::string& dest)
{
  std::ifstream in(filename, std::ios::in | std::ios::binary);
  if(in)
  {
    in.seekg(0, std::ios::end);
    dest.resize(in.tellg());
    in.seekg(0, std::ios::beg);
    in.read(&dest[0], dest.size());
    in.close();
	return;
  }

  std::string msg = "Could not read contents of: ";
  msg.append(filename);
  throw std::runtime_error(msg);
}

} // utils
} // test


