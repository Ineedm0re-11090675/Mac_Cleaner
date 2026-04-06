cmake_minimum_required(VERSION 3.16)
project(mac_cleaner_core LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(mac_cleaner
    cpp/src/main.cpp
    cpp/src/cleaner.cpp
)

target_include_directories(mac_cleaner PRIVATE cpp/include)
