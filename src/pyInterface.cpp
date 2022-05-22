//
// Created by 陈竞潇 on 2022/4/19.
//

#include "pyInterface.h"
#include "Utils.h"
#include <unistd.h>

pyInterface::pyInterface(int playerNum):snakeGame(playerNum) {
    int *tmp_pointer = new int(0);
    Utils::set_random_seed(getpid() ^ time(NULL) ^ (long)tmp_pointer);
    free(tmp_pointer);
}

std::vector<std::map<std::string, std::string> > pyInterface::getSnakeStringInfos()
{
    std::vector<std::map<std::string, std::string> > ret;

    for(int i=0;i<snakeGame.playerNum; ++i) {
        std::map<std::string, std::string> sMap;
        sMap["Name"] = snakeGame.snakes[i].name;
        sMap["LastAct"] = snakeGame.snakes[i].lastAct;
        sMap["Act"] = snakeGame.snakes[i].curAct;
        ret.emplace_back(std::move(sMap));
    }

//    return std::move(ret);
    return ret;
}

std::vector<std::map<std::string, int>> pyInterface::getSnakeIntInfos()
{
    std::vector<std::map<std::string, int> > ret;

    for(int i=0;i<snakeGame.playerNum; ++i) {
        std::map<std::string, int> sMap;

        sMap["Num"] = snakeGame.snakes[i].id;
        sMap["IsDead"] = !snakeGame.snakes[i].alive;
        sMap["NowDead"] = snakeGame.snakes[i].nowDead;
        sMap["Speed"] = snakeGame.snakes[i].speed;
        sMap["Kill"] = snakeGame.snakes[i].killNum;
        sMap["KillList"] = Utils::vec2int(snakeGame.snakes[i].killList);
        sMap["KilledList"] = Utils::vec2int(snakeGame.snakes[i].killedList);
        sMap["SaveLength"] = snakeGame.snakes[i].saveLength;
        sMap["Prop_speed"] = snakeGame.snakes[i].speedItemTime;
        sMap["Prop_strong"] = snakeGame.snakes[i].shieldItemTime;
        sMap["Prop_double"] = snakeGame.snakes[i].doubleItemTime;
        sMap["DelAct"] = snakeGame.snakes[i].delAct;

        sMap["Score_len"] = snakeGame.snakes[i].length;
        sMap["Score_kill"] = snakeGame.snakes[i].killNum;
        sMap["Score_time"] = snakeGame.snakes[i].aliveTime;

        ret.emplace_back(std::move(sMap));
    }

//    return std::move(ret);
    return ret;
}

std::vector<std::map<std::string, double>> pyInterface::getSnakeDoubleInfos()
{
    std::vector<std::map<std::string, double>> ret;

    for(int i=0;i<snakeGame.playerNum; ++i)
    {
        std::map<std::string, double> sMap;

        sMap["Score"] = snakeGame.snakes[i].getScore();

        ret.emplace_back(std::move(sMap));
    }

//    return std::move(ret);
    return ret;
}

std::map<std::string, int> pyInterface::getMapInfo()
{
    std::map<std::string, int> ret;
    // Width and height is reversed here to match the web env.
    ret["Length"] = snakeGame.mapInfo.width;
    ret["Width"] = snakeGame.mapInfo.height;
    ret["Time"] = snakeGame.round;
//    return std::move(ret);
    return ret;
}

std::vector<std::vector<std::pair<int, int>>> pyInterface::getMapPosition()
{
    std::vector<std::vector<std::pair<int, int>>> ret(snakeGame.playerNum);
    for(int i=0;i<snakeGame.playerNum; ++i)
    if(snakeGame.snakes[i].alive)
    {
        std::vector<std::pair<int, int>> pos;
        for(auto p: snakeGame.snakes[i].bodyPos)
        {
            pos.emplace_back(std::make_pair((int)p.y, (int)p.x));
        }

        ret[i] = pos;
    }

    std::vector<Pos> posVec;
    std::vector<std::pair<int, int> > pos;
    snakeGame.getAllPos(posVec, MapInfo::Star);
    Utils::pos2pairVec(posVec, pos);
    ret.push_back(pos);
    snakeGame.getAllPos(posVec, MapInfo::Wall);
    Utils::pos2pairVec(posVec, pos);
    ret.push_back(pos);
    snakeGame.getAllPos(posVec, MapInfo::SpeedItem);
    Utils::pos2pairVec(posVec, pos);
    ret.push_back(pos);
    snakeGame.getAllPos(posVec, MapInfo::ShieldItem);
    Utils::pos2pairVec(posVec, pos);
    ret.push_back(pos);
    snakeGame.getAllPos(posVec, MapInfo::DoubleItem);
    Utils::pos2pairVec(posVec, pos);
    ret.push_back(pos);

//    return std::move(ret);
    return ret;
}

void pyInterface::reset()
{
    snakeGame.reset();
}

void pyInterface::step(const std::vector<std::string> &actions)
{
    snakeGame.step(actions);
}

bool pyInterface::isGameOver()
{
    return snakeGame.gameover();
}