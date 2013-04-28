'''
Created on Mar 26, 2013

@author: makahiki
'''
import unittest
from apps.managers.smartgrid_mgr.unlock_lint import Tree

(_ADD, _DELETE, _INSERT) = range(3)
(_ROOT, _DEPTH, _WIDTH) = range(3)


class TestTree(unittest.TestCase):
    """Test cases for Tree class."""
    def setUp(self):
        """Empty setup."""
        pass

    def test_initialization(self):
        """Test initialization of a tree."""
        tree = Tree()
        tree.create_node("Harry", 1, 'event', "True", "harry")  # root node
        tree.create_node("Jane", 2, 'event', "True", "jane", parent="harry")
        tree.create_node("Bill", 3, 'event', "True", "bill", parent="harry")
        tree.create_node("Diane", 1, 'event', "True", "diane", parent="jane")
        tree.create_node("George", 1, 'event', "True", "george", parent="diane")
        tree.create_node("Mary", 1, 'event', "True", "mary", parent="diane")
        tree.create_node("Jill", 1, 'event', "True", "jill", parent="george")
        tree.create_node("Mark", 1, 'event', "True", "mark", parent="jane")
        tree.show()
        print("=" * 80)
        for node in tree.expand_tree(mode=_DEPTH):
            print tree[node].name

    def tearDown(self):
        """Empty teardown."""
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']

    unittest.main()
