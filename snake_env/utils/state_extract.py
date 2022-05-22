

def get_kill_info(game_info, move_num, main_id):
    """
    Return infos which help killing.

    :param game_info:
    :param move_num: length of actions took in current step.
    :param main_id: id of current player
    :return:
    """
    num = len(game_info["Player"])
    final_length = [0] * num
    for i in range(num):
        if i == main_id:
            final_length[i] = min(move_num, game_info["Player"][i]["SaveLength"]) + game_info["Player"][i]["Length"]
        elif game_info["Player"][i]["NowDead"]:
            final_length[i] = 0
        else:
            final_length[i] = min(game_info["Player"][i]["SaveLength"], game_info["Player"][i]["Speed"]) \
                              + game_info["Player"][i]["Length"]
    # if can kill the opponent in current
    killable = []
    # if can kill the opponent with continuous attack
    killable_f = []
    has_strong = (game_info["Player"][main_id]["Prop"]["strong"] > 0)

    left_length_if_no_hit = final_length[main_id] / game_info["Player"][main_id]["Length"]

    if (has_strong):
        left_length_if_hit = max(0, final_length[main_id] - move_num) / game_info["Player"][main_id]["Length"]
    else:
        left_length_if_hit = 0

    for i in range(num):
        if i == main_id:
            continue
        if game_info["Player"][i]["NowDead"]:
            killable.append(False)
            killable_f.append(False)
            continue

        oppo_has_strong = (game_info["Player"][i]["Prop"]["strong"] > 0)
        if (not has_strong) and (not oppo_has_strong):
            killable.append(final_length[main_id] > final_length[i])
            killable_f.append(final_length[main_id] > final_length[i])
            # left_length_if_hit.append(1. if final_length[main_id] > final_length[i] else 0.)
        elif (not has_strong) and (oppo_has_strong):
            killable.append(False)
            killable_f.append(False)
        elif (has_strong) and (not oppo_has_strong):
            killable.append(True)
            killable_f.append(True)
            # left_length_if_hit.append()
        elif (has_strong) and (oppo_has_strong):
            killable.append(False)

            main_value = min(game_info["Player"][main_id]["Prop"]["strong"],
                             (game_info["Player"][main_id]["Length"] + game_info["Player"][main_id]["SaveLength"]) / move_num)
            oppo_value = min(game_info["Player"][i]["Prop"]["strong"],
                             game_info["Player"][i]["Length"] + game_info["Player"][i]["SaveLength"],)
            killable_f.append(main_value > oppo_value)

    return killable, killable_f, left_length_if_no_hit, left_length_if_hit
