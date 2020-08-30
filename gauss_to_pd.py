def gauss_to_pd(_oriented_gauss_code):
    oriented_gauss_code = _oriented_gauss_code
    d_dic = {}
    if len(oriented_gauss_code[0]) > 1:
        d = sum(oriented_gauss_code[0], [])
        for i, j in enumerate(d):
            d_dic[j] = [i + 1, i + 2]
        # here we collect the final component in each Gauss code
        last_component = [i[-1] for i in oriented_gauss_code[0]]
        first_component = [i[0] for i in oriented_gauss_code[0]]
        # here we correct the last_component
        for i, j in zip(last_component, first_component):
            d_dic[i][1] = d_dic[j][0]
        crossing_dic = {}
        for i, x in enumerate(oriented_gauss_code[1]):
            if x == -1:
                crossing_dic[i + 1] = [d_dic[-(i + 1)][0], d_dic[i + 1][1],
                                       d_dic[-(i + 1)][1], d_dic[i + 1][0]]
            elif x == 1:
                crossing_dic[i + 1] = [d_dic[-(i + 1)][0], d_dic[i + 1][0],
                                       d_dic[-(i + 1)][1], d_dic[i + 1][1]]
    elif len(oriented_gauss_code[0]) == 1:
        for i, j in enumerate(oriented_gauss_code[0][0]):
            d_dic[j] = [i + 1, i + 2]
        d_dic[oriented_gauss_code[0][0][-1]][1] = 1
        crossing_dic = {}
        for i, x in enumerate(oriented_gauss_code[1]):
            if x == -1:
                crossing_dic[i + 1] = [d_dic[-(i + 1)][0], d_dic[i + 1][1],
                                       d_dic[-(i + 1)][1], d_dic[i + 1][0]]
            elif x == 1:
                crossing_dic[i + 1] = [d_dic[-(i + 1)][0], d_dic[i + 1][0],
                                       d_dic[-(i + 1)][1], d_dic[i + 1][1]]
    else:
        crossing_dic = {}

    return list(crossing_dic.keys())
