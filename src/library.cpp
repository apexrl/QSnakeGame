#include "pyInterface.h"
#include <pybind11/pybind11.h>
#include "pybind11/stl.h"

namespace py = pybind11;

PYBIND11_MODULE(snake_env_cpp, m) {
    py::class_<pyInterface>(m, "SnakeGame")
        .def(py::init<int &>())
        .def("reset", &pyInterface::reset)
        .def("step", &pyInterface::step)
        .def("get_snake_string_infos", &pyInterface::getSnakeStringInfos)
        .def("get_snake_int_infos", &pyInterface::getSnakeIntInfos)
        .def("get_snake_double_infos", &pyInterface::getSnakeDoubleInfos)
        .def("get_map_info", &pyInterface::getMapInfo)
        .def("get_map_position", &pyInterface::getMapPosition)
        .def("is_game_over", &pyInterface::isGameOver);

}
