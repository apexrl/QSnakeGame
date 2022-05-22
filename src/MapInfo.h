//
// Created by 陈竞潇 on 2022/4/16.
//

#ifndef QSNAKEENV_MAPINFO_H
#define QSNAKEENV_MAPINFO_H

#include <vector>
#include <string>
#include "GameStruct.h"
//message ActionResponse {
//        string user_id = 1;    //用户名
//        string user_pin = 2;  //密码
//
//        int32 user_pos = 3;     //玩家位置
//        int64 tp_number = 4;    //游戏总局数
//        int64 game_number = 5;  //玩家参与局数
//        double total_score = 6; //玩家总分
//        int64 table_round = 7;  //局内步数
//
//        enum RequestType {
//            GameDecision = 0;  //通知client决策
//            HeartBeat = 1;     //维持心跳
//            StateReady = 2;    //询问client是否准备
//            StateUpdate = 3;   //游戏状态更新
//            RoundEnd = 4;      //单局游戏结束
//            GameEnd = 5;  //全部游戏结束
//        }
//        string game_info = 8;        //游戏信息，server向client发送的游戏信息，格式为dump成字符串的dict，具体可参考example代码
//        RequestType msg_type = 9;   //命令类型
//}
const int MaxPlayerNumber = 10;

class MapInfo {
public:
    enum ItemType{
        Speed = 0,
        Shield = 1,
        Double = 2
    };
    struct Item {
        short type;
        Pos pos;
    };

    MapInfo(int playerNum, int width=55, int height=40);
    ~MapInfo();

    enum MapState{
        Wall = 0,
        Empty = 1,
        Star = 2,
        SpeedItem = 3,
        ShieldItem = 4,
        DoubleItem = 5,
        Snake = 6,
        SnakeHead = Snake + MaxPlayerNumber, // Maybe useless
        Unknown = SnakeHead + MaxPlayerNumber
    };

    short ** mapData;
    int height, width, playerNum;
//    std::vector<Pos> starPos, speedItemPos, shieldItemPos, doubleItemPos;
    int map_redundancy, wall_expand_time;

    void mapReset();
    void getItemList(std::vector<Item> &itemList);

    void wallExpand();
    void generateItems(std::vector<int> max_num, std::vector<int> repeat_num, bool isUniform=false);

    short *mapHead, **mapArrayHead; // used for free dynamic space

private:
    void initMapData();
};


#endif //QSNAKEENV_MAPINFO_H
