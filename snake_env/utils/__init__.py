def int_to_vec(int_num):
    vec = []
    cnt = 0
    while int_num > 0:
        if int_num % 2:
            vec.append(cnt)
        cnt += 1
        int_num //= 2
    return vec
