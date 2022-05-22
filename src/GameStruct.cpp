//
// Created by 陈竞潇 on 2022/4/18.
//

#include "GameStruct.h"

bool operator < (const Pos&a, const Pos&b)
{
    if(a.x != b.x) return a.x < b.x;
    return a.y < b.y;
}