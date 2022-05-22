//
// Created by Jingxiao Chen on 2022/4/16.
//

#ifndef QSNAKEENV_SNAKEGAME_H
#define QSNAKEENV_SNAKEGAME_H

#include "MapInfo.h"
#include "SnakeInfo.h"
#include <vector>
#include <string>
#include <map>
#include <set>

class SnakeGame {
public:
    MapInfo mapInfo;
    std::vector<SnakeInfo> snakes;
    int playerNum;

    // Pos, {[snake_id, head/body]}
    std::map<Pos, std::set< std::pair<short, short> > > hitMap;

    // Move direction related.
    static const short Dir[4][2];
    static short action2dir(char c);
    static char dir2action(short d);

    explicit SnakeGame(int playerNum);
    ~SnakeGame();

    // reset game
    void reset();
    void step(const std::vector<std::string> &actions);
    void render(std::string &buf);

    void* getPyState();
    void getAllPos(std::vector<Pos> &ret, short type);

    bool gameover();

    int round;

private:

    std::map< std::pair<short, short>, short > hitCheckTable;
    std::map< std::pair<short, short>, short > hitStateTable;
    enum HitState{
        NoHit,
        HitWin,  // hit, no need to delete head
        HitBack, // hit (with shield), but delete head later
        HitLose, // hit and be killed
        HitWall, // die immediately
    };
    std::vector<short> hitStates;
    std::vector<short> diePlayers;

    void resetSnakePos();
    void simulate(const std::vector<std::string> &actions);
    void countDownItemTime();
    void moveSnakes(const std::vector<std::string> &actions);
    void hitCheck();
    void hitDeal(int si, int sj, short hit_type);
    void flashbackLength();
    void snake2Star();
    void itemJudgement();
    void mapUpdate();

    void calcScore();

    void load_state();
    void load_state_from_obs();



};


#endif //QSNAKEENV_SNAKEGAME_H
