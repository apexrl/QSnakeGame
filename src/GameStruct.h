//
// Created by 陈竞潇 on 2022/4/17.
//

#ifndef QSNAKEENV_GAMESTRUCT_H
#define QSNAKEENV_GAMESTRUCT_H

struct Pos
{
    Pos(short xx=0, short yy=0){
        x = xx;
        y = yy;
    }
    short x, y;
};
bool operator < (const Pos&a, const Pos&b);

enum Direction
{
    Up = 0,
    Down = 1,
    Left = 2,
    Right = 3
};

#endif //QSNAKEENV_GAMESTRUCT_H
