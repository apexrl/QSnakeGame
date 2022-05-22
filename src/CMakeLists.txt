cmake_minimum_required(VERSION 3.16)
project(QSnakeEnv)

set(CMAKE_CXX_STANDARD 14)

# if(NOT TARGET spdlog)
#     # Stand-alone build
#     find_package(spdlog REQUIRED)
# endif()
#add_library(QSnakeEnv SHARED library.cpp library.h SnakeGame.cpp
#        SnakeGame.h main.cpp MapInfo.cpp MapInfo.h GameStruct.h
#        EnvState.cpp EnvState.h SnakeInfo.cpp SnakeInfo.h Utils.cpp
#        Utils.h GameStruct.cpp)
SET(CMAKE_BUILD_TYPE "Debug")
SET(CMAKE_CXX_FLAGS_DEBUG "$ENV{CXXFLAGS} -Wall -g2 -ggdb")
SET(CMAKE_CXX_FLAGS_RELEASE "$ENV{CXXFLAGS} -O3 -Wall")

set(PROJECT_HEADER_FILES
    SnakeGame.h
    MapInfo.h
    GameStruct.h
    EnvState.h
    SnakeInfo.h
    Utils.h
    GameStruct.h
    pyInterface.h
    )
set(PROJECT_SRC_FILES
    SnakeGame.cpp
    main.cpp
    MapInfo.cpp
    GameStruct.cpp
    EnvState.cpp
    SnakeInfo.cpp
    Utils.cpp
    pyInterface.cpp
    )

set(PROJECT_LIB_NAME ${PROJECT_NAME}_lib CACHE INTERNAL "")

add_executable(${PROJECT_NAME} ${PROJECT_HEADER_FILES} ${PROJECT_SRC_FILES})
add_library(${PROJECT_LIB_NAME} ${PROJECT_HEADER_FILES} ${PROJECT_SRC_FILES})
set_target_properties(${PROJECT_LIB_NAME} PROPERTIES CXX_VISIBILITY_PRESET "hidden")

# target_link_libraries(${PROJECT_NAME} PRIVATE spdlog::spdlog)
# target_link_libraries(${PROJECT_LIB_NAME} PRIVATE spdlog::spdlog)
