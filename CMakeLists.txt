cmake_minimum_required(VERSION 3.16)
project(snake_env_cpp)

set(CMAKE_CXX_STANDARD "14" CACHE STRING "")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -DRAPIDJSON_HAS_STDSTRING=1")
set(CMAKE_CXX_FLAGS_RELEASE "-O2")
set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

SET(CMAKE_BUILD_TYPE "Debug")
SET(CMAKE_CXX_FLAGS_DEBUG "$ENV{CXXFLAGS} -Wall -g2 -ggdb")
SET(CMAKE_CXX_FLAGS_RELEASE "$ENV{CXXFLAGS} -O3 -Wall")

add_subdirectory(src)
find_package(pybind11 REQUIRED)
pybind11_add_module(${PROJECT_NAME} MODULE src/library.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${PROJECT_LIB_NAME})
