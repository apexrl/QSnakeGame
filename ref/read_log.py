import pickle as pkl
import numpy as np
f = open("obs_list.pkl", "rb")
data = pkl.load(f)
f.close()

for d in data:
    for s in d['gameinfo']['Player']:
        i = s["Num"]
        if s['IsDead']:
            print("round {}, snake {} dead.".format(d["gameinfo"]["Map"]["Time"], s["Num"]))
            print("Snake pos", d["gameinfo"]["Map"]["SnakePosition"][i])
            print("Last act", s["Act"])
            for ss in d['gameinfo']['Player']:
                print(ss)
            quit()
        else:
            if s["Num"] == 5 or i == 0:
                print("pos", i, d["gameinfo"]["Map"]["Time"], d["gameinfo"]["Map"]["SnakePosition"][i])
                print("SaveLength", d["gameinfo"]["Player"][i]["SaveLength"])

    # d['gameinfo']['Map']['SnakePosition']
