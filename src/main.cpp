//
// Created by 陈竞潇 on 2022/4/16.
//
#include "SnakeGame.h"
#include <string>
#include <iostream>
#include "Utils.h"
#include <time.h>
#include "pyInterface.h"

std::string get_action(int id, int round, SnakeGame* game, int player_num=0)
{

    int i = round;
    std::string act;
    if(id < player_num)
    {
        std::cout << "=== Player " << id << " status:" << std::endl;
//        std::cout << game->snakes[id].headPos.size();
//        for(auto p : game->snakes[id].bodyPos)
//        {
//            std::cout << p.x << ", "<< p.y << "| ";
//        }
//        std::cout << std::endl;
        std::cout << "s: " << game->snakes[id].speed
                  << " st: " << game->snakes[id].speedItemTime
                  << " strongt: " << game->snakes[id].shieldItemTime
                  << " dt: " << game->snakes[id].doubleItemTime << std::endl;
        std::cout << "saveLength: " << game->snakes[id].saveLength
                  << " kill: " << game->snakes[id].killNum
                  << " length: " << game->snakes[id].length
                  << " alive: " << game->snakes[id].aliveTime << std::endl;

        std::cin >> act;
        return act;
    }

    if(0<=id && id < 3) {
        act += SnakeGame::dir2action(i%2);
        return act;
    }else {
        char c='w';
        int d;
        for(int j=0; j<10;++j) {
            Pos p = game->snakes[id].bodyPos[0];
            d = Utils::uniform(0,3);
            short m = game->mapInfo.mapData[p.x + SnakeGame::Dir[d][0]][p.y + SnakeGame::Dir[d][1]];
            if(m == MapInfo::Wall || m >= MapInfo::Snake)
                continue;
            c = SnakeGame::dir2action(d);
            break;
        }
        act += c;
        return act;
    }
}

int main(int argc,char *argv[ ])
{
    int i, j, player_num = 0, max_round = 50;
    if(argc > 1)
        player_num = atoi(argv[1]);
    if(argc > 2)
        max_round = atoi(argv[2]);
    if(argc > 3)
        Utils::set_random_seed(atoi(argv[3]));
    else
        Utils::set_random_seed(time(0));

    max_round = std::min(max_round, 150);

    std::string displayBuf;

    std::cout << "new SGame" << std::endl;
    SnakeGame *game = new SnakeGame(6);
    // pyInterface interface(game);

    std::cout << "reset SGame" << std::endl;
    game->reset();
    std::cout << "render SGame" << std::endl;
    game->render(displayBuf);
    std::cout << displayBuf << std::endl;


    for(int i = 0; i < max_round; ++i)
    {
        std::cout << "step "<< i  << std::endl;
        for(int j=0;j<game->playerNum;++j)
        {
            std::cout << game->snakes[j].getScore() << " ";
        }
        std::cout << std::endl;
        for(int j=0;j<game->playerNum;++j)
        {
            std::cout << game->snakes[j].nowDead << "," << !game->snakes[j].alive << " ";
        }
        std::cout << std::endl;
//        for(int j=0;j<game->playerNum;++j)
//        {
//            std::cout << game->snakes[j].lengthScore << " ";
//        }
//        std::cout << std::endl;
//        for(int j=0;j<game->playerNum;++j)
//        {
//            std::cout << game->snakes[j].timeScore << " ";
//        }
//        std::cout << std::endl;

        std::vector<std::string> acts(game->playerNum);

        for(int j=0;j<game->playerNum; ++j)
            acts[j] = get_action(j, i, game, player_num);

        game->step(acts);
        std::cout << "render " << i << std::endl;
        game->render(displayBuf);
        std::cout << displayBuf;


        if(game->gameover())
            break;
    }
    return 0;
}