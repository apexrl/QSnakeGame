//
// Created by 陈竞潇 on 2022/4/16.
//

#include "MapInfo.h"
#include <string.h>
#include <assert.h>
#include <random>
#include "Utils.h"

#include "iostream"

MapInfo::MapInfo(int playerNum, int width, int height)
{
    this->width = width;
    this->height = height;
    this->playerNum = playerNum;

    // At least 1.
    map_redundancy = 1;

    initMapData();
    mapReset();
}
void MapInfo::initMapData()
{
    // init map
    int map_size = (width + map_redundancy*2) * (height + map_redundancy*2) * sizeof(short);
    mapHead = (short *)malloc(map_size);
    memset(mapHead, 0, map_size);

    int map_array_size = (height + map_redundancy*2) * sizeof(short*);
    mapArrayHead = (short **)malloc(map_array_size);

    mapData = mapArrayHead + map_redundancy; // 0-based
    short *currentMapPointer = mapHead;
    for(int i= 0 - map_redundancy; i <= height + map_redundancy - 1; ++i)

    {
        mapData[i] = currentMapPointer;
        currentMapPointer += (width + map_redundancy*2);
    }
    assert(currentMapPointer - mapHead == (width + map_redundancy*2) * (height + map_redundancy*2));
}

void MapInfo::mapReset()
{
    for(int i=0;i<height;++i) {
        assert(&mapData[i] - mapArrayHead < (height + map_redundancy*2));
        assert(&mapData[i] - mapArrayHead >= 0);
        for(int j = 0; j < width ;++j) {
            assert(&mapData[i][j] - mapHead < (width + map_redundancy*2) * (height + map_redundancy*2));
            assert(&mapData[i][j] - mapHead >= 0);
            mapData[i][j] = Empty;
        }
    }
    wall_expand_time = 0;

}

void MapInfo::getItemList(std::vector<MapInfo::Item> &itemList)
{
    auto starList = std::vector<Pos>();
    auto speedItemList = std::vector<Pos>();
    auto shieldItemPos = std::vector<Pos>();
    auto doubleItemPos = std::vector<Pos>();

    for(int i=0;i<height;++i) {
        for(int j = 0; j < width ;++j)
        {
            if(Star == mapData[i][j]){
                starList.emplace_back(Pos(i, j));
            }
            if(SpeedItem == mapData[i][j]){
                speedItemList.emplace_back(Pos(i, j));
            }
            if(ShieldItem == mapData[i][j]){
                shieldItemPos.emplace_back(Pos(i, j));
            }
            if(DoubleItem == mapData[i][j]){
                doubleItemPos.emplace_back(Pos(i, j));
            }
        }
    }

    itemList = std::vector<Item>();
    for(auto p: starList)
        itemList.push_back(Item{Star, p});
    for(auto p: speedItemList)
        itemList.push_back(Item{SpeedItem, p});
    for(auto p: shieldItemPos)
        itemList.push_back(Item{ShieldItem, p});
    for(auto p: doubleItemPos)
        itemList.push_back(Item{DoubleItem, p});
}

MapInfo::~MapInfo()
{
//    int map_size = (width + map_redundancy) * (height + map_redundancy) * sizeof(short);
//    int map_array_size = (height + map_redundancy) * sizeof(short);
    free(mapHead);
    free(mapArrayHead);
}

void MapInfo::wallExpand()
{
    for(int i=wall_expand_time; i<=height-1-wall_expand_time; ++i)
    {
        if(mapData[i][wall_expand_time] == Empty)
            mapData[i][wall_expand_time] = Wall;
        if(mapData[i][width-1-wall_expand_time] == Empty)
            mapData[i][width-1-wall_expand_time] = Wall;
    }
    for(int j=wall_expand_time; j<=width-1-wall_expand_time; ++j)
    {
        if(mapData[wall_expand_time][j] == Empty)
            mapData[wall_expand_time][j] = Wall;
        if(mapData[height-1-wall_expand_time][j] == Empty)
            mapData[height-1-wall_expand_time][j] = Wall;
    }

    wall_expand_time += 1;
}

void MapInfo::generateItems(std::vector<int> max_num, std::vector<int> repeat_num, bool isUniform)
{
    std::normal_distribution<double> dist(0,10.0);
    std::uniform_int_distribution<int> dist_h(0, height), dist_w(0, width);
    for(int type=Star; type <= DoubleItem; type++)
    {
        // count on item num
        int cnt = 0;
        for(int i=0; i<height-1;i++)
            for(int j=0; j<width-1;j++)
                if(mapData[i][j] == type)
                    cnt += 1;
        for(int i = 0; i < repeat_num[type-Star] && cnt < max_num[type-Star]; ++i) {
            int x, y;
            // [0, height-1]
            if(isUniform)
            {
                x = dist_h(Utils::rand_gen);
                y = dist_w(Utils::rand_gen);
            }else{
                x = int(dist(Utils::rand_gen) + height / 2.);
                y = int(dist(Utils::rand_gen) + width / 2.);
            }

            if(0<=x && x< height && 0<=y && y<width && mapData[x][y] == Empty)
            {
                mapData[x][y] = type;
                cnt += 1;
            }
        }
    }
}