//
// Created by 陈竞潇 on 2022/4/17.
//

#ifndef QSNAKEENV_UTILS_H
#define QSNAKEENV_UTILS_H

#include <cstdlib>
#include <cmath>
#include <limits>
#include <random>
#include "GameStruct.h"

class Utils {
public:
    static std::default_random_engine rand_gen;
    static void set_random_seed(int seed);
    static int uniform(int l, int r);
    static int vec2int(std::vector<short> &v);
    static void pos2pairVec(const std::vector<Pos> &posVec,
                     std::vector<std::pair<int, int> > &pos);
};


#endif //QSNAKEENV_UTILS_H
