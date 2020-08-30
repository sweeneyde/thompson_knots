from writhe_and_whitney import words_to_writhe, words_to_whitney
from oriented import is_oriented



if __name__ == '__main__':
    unlink_trees = (tuple(line.split(" / ")) for line in
                    open("trefoil_trees9.txt").read().splitlines())
    unlink_trees = (pair for pair in unlink_trees if is_oriented(*pair))

    # wanted = {(2, 0), (0, 2), (-2, 0), (0, -2)}
    for pair in unlink_trees:
        writhe = words_to_writhe(*pair)
        whitney = words_to_whitney(*pair)
        # if (writhe, whitney-1) in wanted:
        print(' / '.join(pair), f"writhe={writhe}", f"whitney-1={whitney-1}")