//
// Created by 陈竞潇 on 2022/4/17.
//

#include "SnakeInfo.h"
#include <iostream>

SnakeInfo::SnakeInfo()
{
    reset();
}

void SnakeInfo::reset()
{
    alive = true;
    hasSpeed = hasShield = hasDouble = false;
    lastAct  = curAct = "";
    saveLength = 0;
    length = 2;
    killNum = 0;
    aliveTime = 0;
    speed = 1;
    speedItemTime = shieldItemTime = doubleItemTime = 0;
    headDir = Up;
    bodyPos = std::vector<Pos>(2);
    bodyPos[0] = Pos(0, 0);
    bodyPos[1] = Pos(0, 1);

    nowDead = false;
    delAct = false;
    killList.clear();
    killedList.clear();
    headPos.clear();
}

void SnakeInfo::eat(short star, short speedItem, short shieldItem, short doubleItem)
{
    if(alive == false)
    {
        return;
    }
    if(star > 0 || speedItem >0 || shieldItem >0 || doubleItem > 0)
    {
//        std::cout << "[eat] "<< id << " " << star << " " << speedItem << " " << shieldItem << " "<< doubleItem << std::endl;
    }
    saveLength += star;
    speedItemTime += speedItem * 5;
    shieldItemTime += shieldItem * 5;
    doubleItemTime += doubleItem * 5;
    speed += speedItem;
}
void SnakeInfo::itemCountDown()
{
    aliveTime += 1;
    speedItemTime = std::max(speedItemTime-1, 0);
    shieldItemTime = std::max(shieldItemTime-1, 0);
    doubleItemTime = std::max(doubleItemTime-1, 0);
    hasSpeed = (speedItemTime > 0);
    hasShield = (shieldItemTime > 0);
    hasDouble = (doubleItemTime > 0);
    if(speedItemTime == 0)
        speed = 1;
}
void SnakeInfo::updateStatus()
{
    nowDead = false;
    delAct = false;
//    lastAct = curAct;
}

void SnakeInfo::move(const std::vector<Pos> &moveTrace)
{
    int finalLength = length + std::min((int)moveTrace.size(), saveLength);
    saveLength -= std::min((int)moveTrace.size(), saveLength);
//    std::cout << "h" << moveTrace.size() << " " << bodyPos.size() << " " << length << " "<< finalLength << std::endl;
    headPos = std::vector<Pos>(moveTrace.begin(),
                               moveTrace.begin() + std::min((int)moveTrace.size(), finalLength));
//    std::cout << "body" << std::endl;
    bodyPos = std::vector<Pos>(bodyPos.begin(), bodyPos.begin()+(finalLength - headPos.size()));
//    std::cout << "moveTrace ";
//    for(auto p: moveTrace)
//    {
//        std::cout << p.x <<", "<<p.y << " ";
//    }std::cout << std::endl;
//    std::cout << "bodyPos ";
//    for(auto p: bodyPos)
//    {
//        std::cout << p.x <<", "<<p.y << " ";
//    }std::cout << std::endl;
    length = finalLength;
}

void SnakeInfo::head2Body(bool hitHead)
{
    if(hitHead) {
        length -= headPos.size();
        headPos.clear();
        if(length == 0) {
            nowDead = true;
            alive = false;
        }
        return;
    }
    std::vector<Pos> newBody(headPos);
    for(int i = 0; i < length-headPos.size(); ++i) {
        newBody.push_back(bodyPos[i]);
    }
    headPos.clear();

    // CHECK: std::move may cause error?
    bodyPos = std::move(newBody);
}

double SnakeInfo::getScore()
{
    return (killScore*1.5 + lengthScore + timeScore) / 3.5;
}