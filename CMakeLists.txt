cmake_minimum_required(VERSION 3.10)
project(Test)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenCV REQUIRED)

add_subdirectory(common)
add_subdirectory(modules)

add_executable(test main.cpp)
target_link_libraries(test PRIVATE M1 M2 math ${OpenCV_LIBS})
