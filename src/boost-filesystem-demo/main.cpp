#include <boost/filesystem.hpp>
#include <iostream>

int main() {

    std::string pathStr = "tut2.cpp";
    boost::filesystem::path p(pathStr); // avoid repeated path construction below

    if (boost::filesystem::exists(p)) // does path p actually exist?
    {
        if (boost::filesystem::is_regular_file(p)) // is path p a regular file?
            std::cout << p << " size is " << boost::filesystem::file_size(p) << '\n';

        else if (boost::filesystem::is_directory(p)) // is path p a directory?
            std::cout << p << " is a directory\n";

        else
            std::cout << p << " exists, but is not a regular file or directory\n";
    } else {
        std::cout << p << " does not exist\n";
    }

    return 0;
}
