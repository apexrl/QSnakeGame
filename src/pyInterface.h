//
// Created by 陈竞潇 on 2022/4/19.
//

#ifndef QSNAKEENV_PYINTERFACE_H
#define QSNAKEENV_PYINTERFACE_H

#include "SnakeGame.h"
#include <map>

class pyInterface {
public:
    pyInterface(int playerNum);
    SnakeGame snakeGame;
    // get infos
    std::vector<std::map<std::string, std::string> > getSnakeStringInfos();
    std::vector<std::map<std::string, int> > getSnakeIntInfos();
    std::vector<std::map<std::string, double> > getSnakeDoubleInfos();

    std::vector<std::vector<std::pair<int, int> > > getMapPosition();
    std::map<std::string, int> getMapInfo();

    // wrap the method of snakeGame
    void reset();
    void step(const std::vector<std::string> &actions);
    bool isGameOver();

};


#endif //QSNAKEENV_PYINTERFACE_H
