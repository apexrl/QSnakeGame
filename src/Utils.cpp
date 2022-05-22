//
// Created by 陈竞潇 on 2022/4/17.
//

#include "Utils.h"
#include "iostream"

std::default_random_engine Utils::rand_gen = std::default_random_engine();

void Utils::set_random_seed(int seed) {
    std::cout <<"Set random seed: "<< seed << std::endl;
    rand_gen = std::default_random_engine(seed);
    srand(seed);
}
int Utils::uniform(int l, int r)
{
    return rand() % (r-l+1) + l;
}
int Utils::vec2int(std::vector<short> &v)
{
    int ret = 0;
    for(int i=0;i < v.size(); ++i)
        ret = (ret | (1<<v[i]));
    return ret;
}

void Utils::pos2pairVec(const std::vector<Pos> &posVec, std::vector<std::pair<int, int>> &pos)
{
    pos = std::vector<std::pair<int, int> >(posVec.size());
    for(int i=0;i<posVec.size();++i)
    {
        pos[i] = std::make_pair(posVec[i].x, posVec[i].y);
    }
}