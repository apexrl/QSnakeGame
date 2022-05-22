//
// Created by 陈竞潇 on 2022/4/17.
//

#ifndef QSNAKEENV_SNAKEINFO_H
#define QSNAKEENV_SNAKEINFO_H
#include <string>
#include <vector>
#include "GameStruct.h"

class SnakeInfo {
public:
    SnakeInfo();
    bool alive, hasSpeed, hasShield, hasDouble;
    std::string lastAct, curAct;
    short headDir;
    int saveLength, length, aliveTime;
    double killScore, lengthScore, timeScore;
    int speed;
    int speedItemTime, shieldItemTime, doubleItemTime;
    std::vector<Pos> bodyPos, headPos;

    int id, killNum;
    std::vector<short> killList, killedList;
    bool nowDead, delAct;
    std::string name;

    void reset();
    void eat(short star, short speedItem, short shieldItem, short doubleItem);
    void move(const std::vector<Pos> &moveTrace);
    void head2Body(bool hitHead);
    void itemCountDown();
    void updateStatus();

    double getScore();

};


#endif //QSNAKEENV_SNAKEINFO_H
