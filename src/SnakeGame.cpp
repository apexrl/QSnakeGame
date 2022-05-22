//
// Created by 陈竞潇 on 2022/4/16.
//

#include <algorithm>

#include "SnakeGame.h"
#include "assert.h"
#include "Utils.h"
#include "sstream"
#include "iostream"

constexpr const short SnakeGame::Dir[4][2] = {{1, 0}, {-1, 0}, {0, -1}, {0, 1}};

void SnakeGame::getAllPos(std::vector<Pos> &ret, short type)
{
    ret = std::vector<Pos>();
    for(int i=0;i<mapInfo.height; ++i)
    for(int j=0;j<mapInfo.width; ++j)
    if(mapInfo.mapData[i][j] == type){
        ret.emplace_back(Pos(j, i));
    }
}

void* SnakeGame::getPyState()
{
//    for(int i=0;i<=playerNum;++i) {
//        snakes[i].name;
//        snakes[i].id;
//        snakes[i].lastAct;
//        snakes[i].curAct;
//        !snakes[i].alive;
//        snakes[i].nowDead;
//        snakes[i].killNum;
//        snakes[i].killList;
//        snakes[i].killedList;
//        snakes[i].saveLength;
//        snakes[i].speedItemTime;
//        snakes[i].shieldItemTime;
//        snakes[i].doubleItemTime;
//        snakes[i].delAct;
//        snakes[i].lengthScore;
//        snakes[i].killScore;
//        snakes[i].timeScore;
//        snakes[i].getScore();
//    }
//    mapInfo.height;
//    mapInfo.width;
//    for(int i=0;i<=playerNum; ++i) {
//        for(auto p: snakes[i].bodyPos) {
//            p.x;
//            p.y;
//        }
//    }
//    std::vector<Pos> posVec;
//    getAllPos(posVec, MapInfo::Star);
//    // ...
//    getAllPos(posVec, MapInfo::Wall);
//    // ...
//    getAllPos(posVec, MapInfo::SpeedItem);
//    // ...
//    getAllPos(posVec, MapInfo::ShieldItem);
//    // ...
//    getAllPos(posVec, MapInfo::DoubleItem);
//
//    round;
//    for(int i=0;i<playerNum;++i)
//    {
//        snakes[i].getScore();
//    }
//
//    // ignore tableinfo
//    // Return fake info is enough
//
//    // Return a pointer to python data instance if you want.
    return NULL;
}

short SnakeGame::action2dir(char c)
{
    if(c == 'w') return Up;
    if(c == 's') return Down;
    if(c == 'a') return Left;
    if(c == 'd') return Right;
    assert(false);
}

char SnakeGame::dir2action(short d)
{
    if(d == Up) return 'w';
    if(d == Down) return 's';
    if(d == Left) return 'a';
    if(d == Right) return 'd';
    assert(false);
}

SnakeGame::SnakeGame(int playerNum):
    mapInfo(playerNum), playerNum(playerNum), round(0)
{
    for(int i=0;i<=playerNum;++i) {
        snakes.emplace_back(SnakeInfo());
    }
    reset();
}
SnakeGame::~SnakeGame()
{

}
void SnakeGame::reset()
{
    round = 0;
    // reset map
    mapInfo.mapReset();

    // reset snake position
    resetSnakePos();

    // build the first wall
    mapInfo.wallExpand();

    // generate items
    std::vector<int> Ns({200, 50, 50, 50}), Rs({400, 100, 100, 100});
    mapInfo.generateItems(Ns, Rs, true);
    calcScore();
}

bool SnakeGame::gameover()
{
    bool all_snake_die = true;
    for(int i=0; i < playerNum; ++i)
    if(snakes[i].alive){
        all_snake_die = false;
    }

    return all_snake_die || round >= 150;
}

void SnakeGame::resetSnakePos()
{
    // TODO: support players != 6
//    [[[26, 13], [26, 14]],
//    [[13, 26], [14, 26]],
//    [[39, 13], [39, 14]],
//    [[13, 13], [14, 13]],
//    [[26, 26], [27, 26]],
//    [[39, 26], [38, 26]]]
    std::vector<Pos> pVec;
    for(int i=0;i<2;++i)
        for(int j=0;j<3;++j)
            pVec.push_back(Pos(13*(i+1), 13*(j+1)));
    std::shuffle(pVec.begin(), pVec.begin()+6, Utils::rand_gen);

    for(int i=0; i<playerNum; ++i) {
        snakes[i].reset();
        snakes[i].id = i;
        snakes[i].name = std::string("Bot_") + std::to_string(i);

        while(true) {
            int x, y, d;
//            x = Utils::uniform(1, mapInfo.height-2);
//            y = Utils::uniform(1, mapInfo.width-2);
            x = pVec[i].x;
            y = pVec[i].y;
            d = Utils::uniform(0,3);
            if(mapInfo.mapData[x][y] != MapInfo::Empty)
                continue;
            snakes[i].bodyPos[0] = Pos(x, y);
            x -= Dir[d][0];
            y -= Dir[d][1];
            if(mapInfo.mapData[x][y] != MapInfo::Empty)
                continue;
            snakes[i].bodyPos[1] = Pos(x, y);
            snakes[i].headDir = d;
            break;
        }
        for(auto p: snakes[i].bodyPos)
            mapInfo.mapData[p.x][p.y] = MapInfo::Snake + i;
    }
}

void SnakeGame::step(const std::vector<std::string> &actions)
{
    simulate(actions);
}

void SnakeGame::simulate(const std::vector<std::string> &actions)
{
//    std::cout << "countDownItemTime" << std::endl;
    countDownItemTime();
//    std::cout << "moveSnakes" << std::endl;
    moveSnakes(actions);
//    std::cout << "hitCheck" << std::endl;
    hitCheck();
//    std::cout << "flashbackLength" << std::endl;
    flashbackLength();
//    std::cout << "snake2Star" << std::endl;
    snake2Star();
//    std::cout << "itemJudgement" << std::endl;
    itemJudgement();
//    std::cout << "mapUpdate" << std::endl;
    mapUpdate();
    calcScore();
}

void SnakeGame::calcScore()
{
    std::vector<std::pair<int,int> > vec(playerNum);
    int lastVal=-1, lastIdx=-1, sum=0;

    for(int i=0;i<playerNum;++i)
    {
        vec[i] = std::make_pair(snakes[i].killNum, i);
    }
    std::sort(vec.begin(), vec.end(), std::greater<>());
    for(int i=0;i<playerNum;++i)
    {
        if(lastVal != vec[i].first)
        {
            if(lastIdx >= 0)
            {
//                std::cout << "calc " << sum << " "<< i-lastIdx << std::endl;
                for(int j=lastIdx; j<i ;j++)
                    snakes[vec[j].second].killScore = 1.*sum/(i - lastIdx);
                sum = 0;
            }
            lastVal = vec[i].first;
            lastIdx = i;
//            std::cout << "calc " << sum << " "<< i-lastIdx << std::endl;
//            snakes[vec[i].second].killScore = playerNum-i;
        }
        sum += playerNum-i;
    }
    if(sum > 0)
    {
        for(int j=lastIdx; j<playerNum ;j++)
            snakes[vec[j].second].killScore = 1.*sum/(playerNum - lastIdx);
        sum = 0;
    }
    lastVal = -1; lastIdx = -1;

    for(int i=0;i<playerNum;++i)
    {
        vec[i] = std::make_pair(snakes[i].length,i);
    }
    std::sort(vec.begin(), vec.end(), std::greater<>());
    for(int i=0;i<playerNum;++i)
    {
        if(lastVal != vec[i].first)
        {
            if(lastIdx >= 0)
            {
                for(int j=lastIdx; j<i ;j++)
                    snakes[vec[j].second].lengthScore = 1.*sum/(i - lastIdx);
                sum = 0;
            }
            lastVal = vec[i].first;
            lastIdx = i;
        }
        sum += playerNum-i;
    }
    if(sum > 0)
    {
        for(int j=lastIdx; j<playerNum ;j++)
            snakes[vec[j].second].lengthScore = 1.*sum/(playerNum - lastIdx);
        sum = 0;
    }

    lastVal = -1; lastIdx = -1;
    for(int i=0;i<playerNum;++i)
    {
        vec[i] = std::make_pair(snakes[i].aliveTime,i);
    }
    std::sort(vec.begin(), vec.end(), std::greater<>());
    for(int i=0;i<playerNum;++i)
    {
        if(lastVal != vec[i].first)
        {
            if(lastIdx >= 0)
            {
                for(int j=lastIdx; j<i ;j++)
                    snakes[vec[j].second].timeScore = 1.*sum/(i - lastIdx);
                sum = 0;
            }
            lastVal = vec[i].first;
            lastIdx = i;
        }
        sum += playerNum-i;
    }
    if(sum > 0)
    {
        for(int j=lastIdx; j<playerNum ;j++)
            snakes[vec[j].second].timeScore = 1.*sum/(playerNum - lastIdx);
        sum = 0;
    }
}

void SnakeGame::countDownItemTime()
{
    round += 1;
    for(int i=0; i<playerNum; ++i)
    {
        if(snakes[i].alive){
            snakes[i].itemCountDown();
        }
        snakes[i].updateStatus();
    }
}

void SnakeGame::moveSnakes(const std::vector<std::string> &actions)
{
    for(int i=0; i<playerNum; ++i)
    if(snakes[i].alive){
        snakes[i].curAct = std::string(actions[i].begin(),
                                       actions[i].begin() + std::min((int)actions[i].size(), snakes[i].speed));
        snakes[i].lastAct = snakes[i].curAct[snakes[i].curAct.size()-1];

        // Erase snake body on the map
        for(auto p: snakes[i].bodyPos) {
            mapInfo.mapData[p.x][p.y] = MapInfo::Empty;
        }

        Pos p = snakes[i].bodyPos[0];
        std::vector<Pos> trace(std::min((int)actions[i].size(), snakes[i].speed));

        for(int j = 0; j < trace.size(); ++j) {
            short d = action2dir(actions[i][j]);
            p.x += Dir[d][0];
            p.y += Dir[d][1];
            trace[trace.size()-1-j] = p;
            snakes[i].headDir = d;
        }
        snakes[i].move(trace);
    }

}

// si's head hit sj
void SnakeGame::hitDeal(int si, int sj, short hit_type)
{
    const short HEAD = 0, BODY = 1, WALL = 2;
    if(hit_type == WALL)
    {
        hitStates[si] = HitWall;
        return;
    }

    auto hct_iter = hitCheckTable.find(std::make_pair(si, sj));
    bool body_before = false;
//    std::cout << "hit " << si << " " << sj << " " << hit_type << std::endl;
    if(hct_iter != hitCheckTable.end()) {
        if(hit_type == hct_iter->second)
            return;
        // hit_type is body, but deal with head before
        if(hit_type == BODY && hct_iter->second == HEAD)
            return;
        body_before = true;
    }
    assert(!body_before);
    hitCheckTable[std::make_pair(si, sj)] = hit_type;

    short hitState = NoHit;
    if(hit_type == HEAD) {
        if(!snakes[sj].hasShield) {
            // compare length
            if(snakes[si].length > snakes[sj].length) {
                hitState = HitWin;
            }else if(snakes[si].hasShield){
                hitState = HitWin;
            }else{
                hitState = HitLose;
            }
        }else {
            if(!snakes[si].hasShield) {
                hitState = HitLose;
            }else {
                hitState = HitBack;
            }
        }
    }else{
        if(snakes[si].hasShield) {
            hitState = HitBack;
        }else {
            hitState = HitLose;
        }
    }

    hitStateTable[std::make_pair(si, sj)] = hitState;
    if(hitState > hitStates[si]) {
        hitStates[si] = hitState;
    }
}

void SnakeGame::hitCheck()
{
    const short HEAD = 0, BODY = 1;

    hitStates = std::vector<short>(playerNum, 0);
    hitCheckTable.clear();
    hitStateTable.clear();
    hitMap.clear();

    for(int i=0; i<playerNum; ++i)
    if(snakes[i].alive) {
        for (auto p : snakes[i].bodyPos) {
            auto iter = hitMap.find(p);
            if (iter != hitMap.end()) {
                iter->second.emplace(std::make_pair(i, BODY));
            } else {
                hitMap.emplace(p, std::set< std::pair<short, short> >());
                hitMap[p].emplace(std::make_pair(i, BODY));
            }
        }
    }

    for(int i=0; i<playerNum; ++i)
    if(snakes[i].alive) {
        for (auto p : snakes[i].headPos) {
            auto iter = hitMap.find(p);
            if (iter != hitMap.end()) {
                // hit founded
                for(auto set_iter : iter->second)
                if(set_iter.second == HEAD){
//                    std::cout << "hit!" << p.x <<","<<p.y << std::endl;
                    hitDeal(i, set_iter.first, HEAD);
                    hitDeal(set_iter.first, i, HEAD);
                }
//                for(auto set_iter : iter->second)
//                if(set_iter.second == BODY){
//                    hitDeal(i, set_iter.first, BODY);
//                }

                iter->second.emplace(std::make_pair(i, HEAD));
            } else {
                hitMap.emplace(p, std::set< std::pair<short, short> >());
                hitMap[p].emplace(std::make_pair(i, HEAD));
            }
        }
    }
    for(int i=0; i<playerNum; ++i)
    if(snakes[i].alive) {
        for (auto p : snakes[i].headPos) {
            auto iter = hitMap.find(p);
            if (iter != hitMap.end()) {
                for (auto set_iter : iter->second)
                    if (set_iter.second == BODY) {
//                        std::cout << "hit!" << p.x <<","<<p.y << std::endl;
                        hitDeal(i, set_iter.first, BODY);
                    }
            }
            if(mapInfo.mapData[p.x][p.y] == MapInfo::Wall)
            {
                hitDeal(i, -1, 2);
            }
        }
    }

    // Update kill score
    // TODO: update kill relations
    for(int i=0; i < playerNum; ++i)
    if(snakes[i].alive)
    for(int j=0; j < playerNum; ++j)
    if(snakes[j].alive){
        auto hct_iter = hitStateTable.find(std::make_pair(i, j));
        if(hct_iter != hitStateTable.end() && hct_iter->second == HitWin)
        {
            if(i!=j){
                snakes[i].killNum += 2;
                snakes[i].killList.push_back(j);
                snakes[j].killedList.push_back(i);
            }
        }
        else if(hct_iter == hitStateTable.end() || hct_iter->second != HitLose){
            auto r_hct_iter = hitStateTable.find(std::make_pair(j, i));
            if(r_hct_iter != hitStateTable.end() && r_hct_iter->second == HitLose) {
                if(i!=j){
                    snakes[i].killNum += 1;
                    snakes[i].killList.push_back(j);
                    snakes[j].killedList.push_back(i);
                }
            }
        }
    }

    // update alive status for all snakes
//    diePlayers.clear();
    for(int i=0; i<playerNum; ++i)
    if(snakes[i].alive){
        if(hitStates[i] == HitLose || hitStates[i] == HitWall)
        {
            snakes[i].alive = false;
            snakes[i].nowDead = true;
//            diePlayers.push_back(i);
        }
        if(hitStates[i] == HitBack)
        {
            snakes[i].delAct = true;
        }
    }
}

void SnakeGame::flashbackLength()
{
    for(int i=0; i<playerNum; ++i)
    if(snakes[i].alive){
        snakes[i].head2Body(hitStates[i] == HitBack);
    }
}
void SnakeGame::snake2Star()
{
    for(int i=0; i<playerNum; ++i)
    if(hitStates[i] == HitLose || hitStates[i] == HitWall)
    {
//        std::cout << "head2body " << i << std::endl;
        snakes[i].head2Body(false);
        for(auto p: snakes[i].bodyPos)
        {
//            std::cout << p.x << " "<< p.y << std::endl;
            if(mapInfo.mapData[p.x][p.y] == MapInfo::Empty){
                mapInfo.mapData[p.x][p.y] = MapInfo::Star;
            }
        }
    }
}

void SnakeGame::itemJudgement()
{
    for(int i=0; i<playerNum; ++i)
    if(snakes[i].alive){
        int nums[4] = {0,0,0,0};
        for(auto p: snakes[i].bodyPos)
        {
            int x = mapInfo.mapData[p.x][p.y];
            if(MapInfo::Star <= x && x <= MapInfo::DoubleItem){
//                std::cout <<"eat! "<<i <<" "<< p.x << ", " << p.y << std::endl;
                nums[x - MapInfo::Star] += 1;
            }
            mapInfo.mapData[p.x][p.y] = MapInfo::Empty;
        }
        snakes[i].eat(nums[0], nums[1], nums[2], nums[3]);
    }
}

void SnakeGame::mapUpdate()
{
//    std::cout << "[mapUpdate] update snake body" << std::endl;
    // update snake body on map
    for(int i=0; i<playerNum; ++i)
    if(snakes[i].alive){
        for(auto p: snakes[i].bodyPos) {
            mapInfo.mapData[p.x][p.y] = MapInfo::Snake + i;
        }
    }

    // Expand walls
//    std::cout << "[mapUpdate] Expand Walls" << std::endl;
    int empty_space = 0;
    for(int i=0; i<mapInfo.height; i++)
        for(int j=0; j<mapInfo.width; j++)
        {
            assert(&mapInfo.mapData[i][j] - mapInfo.mapHead < (mapInfo.width + 2) * (mapInfo.height + 2));
            assert(&mapInfo.mapData[i] - mapInfo.mapArrayHead < (mapInfo.height + 2));

//            std::cout << i<< ", " << j << std::endl;
            if(mapInfo.mapData[i][j] != MapInfo::Wall &&
                mapInfo.mapData[i][j] != MapInfo::Star)
                empty_space += 1;
        }

//    std::cout << "[mapUpdate] Expand Walls2" << std::endl;
    if(round % 5 == 0){
        if(empty_space < 400 && round < 100){
            ;
        }else{
            mapInfo.wallExpand();
        }
    }

    // Generate items
//    std::cout << "[mapUpdate] Gen items" << std::endl;
    std::vector<int> Ns(4), Rs(4);
    Ns[0] = 200+round;
    Ns[1] = 60+int(round*0.2);
    Ns[2] = 40;
    Ns[3] = 50;
    Rs[0] = 100+std::min(200, round*10);
    Rs[1] = Rs[2] = Rs[3] = 100+std::min(100, round*10);
    mapInfo.generateItems(Ns, Rs);
}

void SnakeGame::render(std::string &buf)
{
//    char *cbuf[mapInfo.height*(mapInfo.width+1)+10];
    std::stringstream ss;
//    int ci = 0;
    for(int i=0;i<mapInfo.height; ++i){
        for(int j=0;j<mapInfo.width; ++j)
        {
            char c='@';
            short m = mapInfo.mapData[i][j];
            if(m == MapInfo::Empty){
                c = ' ';
            }
            if(m >= MapInfo::Snake && m < MapInfo::SnakeHead){
                c = '0' + m - MapInfo::Snake;
            }
            if(m == MapInfo::Wall){
                c = '#';
            }
            if(m == MapInfo::Star){
                c = '+';
            }
            if(m == MapInfo::SpeedItem){
                c = '*';
            }
            if(m == MapInfo::ShieldItem){
                c = 'O';
            }
            if(m == MapInfo::DoubleItem){
                c = 'X';
            }
            // set head
            for(int k=0;k<playerNum; ++k)
            if(snakes[k].alive){
                Pos p = snakes[k].bodyPos[0];
                if(p.x == i && p.y == j)
                {
                    int d = snakes[k].headDir;
                    if(d == 0)
                        c = '^';
                    if(d == 1)
                        c = 'v';
                    if(d == 2)
                        c = '<';
                    if(d == 3)
                        c = '>';
                }
            }
            ss << c ;
//            ss << c << " ";
        }
        ss << "\n";
    }
    buf = ss.str();
}
