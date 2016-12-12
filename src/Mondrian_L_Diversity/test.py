import unittest
import pdb
from models.gentree import GenTree
from mondrian_l_diversity import mondrian_l_diversity

ATT_TREE = {}


def init_tree():
    global ATT_TREE
    ATT_TREE = {}
    root = GenTree('*')
    ATT_TREE['*'] = root
    lt = GenTree('A', root)
    ATT_TREE['A'] = lt
    ATT_TREE['a1'] = GenTree('a1', lt, True)
    ATT_TREE['a2'] = GenTree('a2', lt, True)
    rt = GenTree('B', root)
    ATT_TREE['B'] = rt
    ATT_TREE['b1'] = GenTree('b1', rt, True)
    ATT_TREE['b2'] = GenTree('b2', rt, True)


class TestMondrianLDiversity(unittest.TestCase):
    def test_group(self):
        init_tree()
        att_trees = [ATT_TREE]

        data = [['a1', ['female', 'diabetes']],
                ['a1', ['female', 'cold']],
                ['b1', ['male', 'diabetes']],
                ['a2', ['male', 'cold']]]
        result, eval_result = mondrian_l_diversity(att_trees, data, 2)
        for row in result:
            print row

        print
        print
        self.assertTrue(abs(eval_result[0] - 0))

    def test_single(self):
        init_tree()
        att_trees = [ATT_TREE] * 2

        data = [['a1', 'b1', 'cold'],
                ['a2', 'b1', 'cold'],
                ['a1', 'b2', 'cold'],
                ['a1', 'b1', 'cold'],
                ['a1', 'b2', 'cancer'],
                ['a1', 'b1', 'cancer']]
        result, eval_result = mondrian_l_diversity(att_trees, data, 2)
        for row in result:
            print row
        self.assertTrue(abs(eval_result[0] - 0))


if __name__ == '__main__':
    unittest.main()
