from moves import *

def test_move_local1():
    assert list(move_local1(TreePair("((oo)o) / (o(oo))"))) \
           == []
    assert list(move_local1(TreePair("((o(oo))o) / ((oo)(oo))"))) \
           == [TreePair("((oo)o) / (o(oo))")]
    assert list(move_local1(TreePair("(((oo)o)((oo)o)) / (o((o(oo))(oo)))"))) \
           == []
    assert list(move_local1(TreePair("(((oo)o)((o(oo))o)) / (o((o(o(oo)))(oo)))"))) \
           == [TreePair("(((oo)o)((oo)o)) / (o((o(oo))(oo)))")]

def test_move_outside1():
    assert list(move_outside1(TreePair("((oo)o) / (o(oo))"))) \
           == [TreePair("(o(oo)) / ((oo)o)")]
    assert list(move_outside1(TreePair("(o(oo)) / ((oo)o)")))\
           == []
    slat_on_top = TreePair("(o(((oo)o)((oo)o)))", "((oo)((o(oo))(oo)))")
    slat_on_bottom = TreePair("((((oo)o)o)((oo)o))", "(o(o((o(oo))(oo))))")
    assert list(move_outside1(slat_on_bottom)) == [slat_on_top]
    assert list(move_outside1(slat_on_top)) == []

def test_move_local2():
    curled_up = TreePair("(o((o(oo))o)) / (((o(oo))o)o)")
    uncurled = TreePair("(o(oo)) / ((oo)o)")
    assert list(move_local2(curled_up)) == [uncurled]
    assert list(move_local2(uncurled)) == []

def test_move_local2_improved():
    (curled_up,) = move_rotate(TreePair("(o((o(oo))o)) / (((o(oo))o)o)"))
    (uncurled,) = move_rotate(TreePair("(o(oo)) / ((oo)o)"))
    assert list(move_local2_improved(curled_up)) == [uncurled]
    assert list(move_local2_improved(uncurled)) == []

    curled_up_2 = TreePair("((o((oo)(oo)))o) / ((((oo)o)o)(oo))")
    uncurled_2 = TreePair("((o(oo))o) / ((oo)(oo))")
    assert list(move_local2_improved(curled_up_2)) == [uncurled_2]
    assert list(move_local2_improved(uncurled_2)) == []

def test_move_local2_improved2():
    (curled_up,) = move_rotate(TreePair("(o((o(oo))o)) / (((o(oo))o)o)"))
    (uncurled,) = move_rotate(TreePair("(o(oo)) / ((oo)o)"))
    assert list(move_local2_improved2(curled_up)) == [uncurled]
    assert list(move_local2_improved2(uncurled)) == []

    curled_up_2 = TreePair("((o((oo)(oo)))o) / ((((oo)o)o)(oo))")
    uncurled_2 = TreePair("((o(oo))o) / ((oo)(oo))")
    assert list(move_local2_improved2(curled_up_2)) == [uncurled_2]
    assert list(move_local2_improved2(uncurled_2)) == []

    curled_up_3 = TreePair("(o((((oo)o)(oo))o)) / (((oo)o)((oo)(oo)))")
    uncurled_3 = TreePair("(((oo)(oo))o) / (o((oo)(oo)))")
    assert list(move_local2_improved2(curled_up_3)) == [uncurled_3]
    assert list(move_local2_improved2(uncurled_3)) == []

def test_move_outside2():
    no_extra = TreePair("((o((oo)o))(oo)) / (((oo)(o(oo)))o)")
    with_extra = TreePair("(o((o((oo)o))(oo))) / (((o(oo))(o(oo)))o)")
    assert list(move_outside2(with_extra)) == [no_extra]
    assert list(move_outside2(no_extra)) == []

    no_extra2 = TreePair("((oo)(oo)) / (((oo)o)o)")
    with_extra2 = TreePair("(o((oo)(oo))) / (((o(oo))o)o)")
    assert list(move_outside2(with_extra2)) == [no_extra2]
    assert list(move_outside2(no_extra2)) == []

def test_move_insert_block():
    template = "((({}{}){}){}) / ({}(({}{}){}))"

    noop = TreePair(template.format(*"o o o o o o o o".split()))
    assert list(move_insert_block(noop)) == []

    not_unlinks = TreePair(template.format(*"(oo) (oo) (oo) (oo) (oo) (oo) (oo) (oo)".split()))
    assert list(move_insert_block(not_unlinks)) == []

    at_2 = TreePair(template.format(*"o ((oo)o) o o o (o(oo)) o o".split()))
    at_4 = TreePair(template.format(*"o o o (o(oo)) o o o ((oo)o)".split()))
    at_24 = TreePair(template.format(*"o ((oo)o) o (o(oo)) o (o(oo)) o ((oo)o)".split()))
    assert set(move_insert_block(at_2)) == {noop}
    assert set(move_insert_block(at_4)) == {noop}
    assert set(move_insert_block(at_24)) == {at_2, at_4}

    unknot_a = TreePair("((oo)o) / (o(oo))")
    b_template = "(o(({}(oo))o)) / ((((o{})o)o)o)"
    unknot_b = TreePair(b_template.format("o", "o"))
    a_into_b = TreePair(b_template.format(*unknot_a))
    assert set(move_insert_block(a_into_b)) == {unknot_a, unknot_b}

def test_move_local3():
    before = TreePair("(o(o(oo))) / (((oo)o)o)")
    after = TreePair("((oo)o) / (o(oo))")
    assert list(move_local3(before)) == [after]
    assert list(move_local3(after)) == []

    before2 = TreePair("(o((o(o(oo)))o)) / ((o((oo)o))(oo))")
    after2 = TreePair("(o(((oo)o)o)) / ((oo)((oo)o))")
    assert list(move_local3(before2)) == [after2]
    assert list(move_local3(after2)) == []

def test_move_local4():
    before1 = TreePair("(o(o(o(oo)))) / ((((oo)o)o)o)")
    after1 = TreePair("(oo) / (oo)")
    assert list(move_local4(before1)) == [after1]

    before2 = TreePair("(o((o(o(o(o(oo)))))o)) / (o((((oo)o)o)(o(oo))))")
    after2 = TreePair("(o((o(oo))o)) / (o(o(o(oo))))")
    assert list(move_local4(before2)) == [after2]

def test_move_local5():
    before1 = TreePair("(o((oo)o)) / (((oo)o)o)")
    after1 = TreePair("(oo) / (oo)")
    assert list(move_local5(before1)) == [after1]

    before2 = TreePair("((o((oo)(oo)))o) / (((oo)o)(o(oo)))")
    after2 = TreePair("((o(oo))o) / (o(o(oo)))")
    assert list(move_local5(before2)) == [after2]

def test_move_local6():
    before1 = TreePair("(o(o((oo)o))) / ((((oo)o)o)o)")
    after1 = TreePair("(oo) / (oo)")
    assert list(move_local6(before1)) == [after1]

    before2 = TreePair("((o(o((oo)(oo))))o) / ((((oo)o)o)(o(oo)))")
    after2 = TreePair("((o(oo))o) / (o(o(oo)))")
    assert list(move_local6(before2)) == [after2]
