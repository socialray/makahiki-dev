'''
Created on Mar 26, 2013

@author: makahiki
'''
import unittest
from apps.managers.smartgrid_mgr.unlock_lint import Node


class Test(unittest.TestCase):
    """Tests for Node class."""

    def setUp(self):
        """set up a Node."""
        self.node1 = Node("Test One", 1, 'event', "True", identifier="ide ntifier 1 ")

    def tearDown(self):
        """Empty tearDown."""
        pass

    def test_initialization(self):
        """Tests initialization and identifier for nodes."""
        self.assertEqual(self.node1.name, "Test One")
        self.assertEqual(self.node1.identifier, "ide_ntifier_1")
        self.assertEqual(self.node1.expanded, True)

    def test_set_children(self):
        """Tests node children."""
        self.node1.update_children(" identi fier 2")
        self.assertEqual(self.node1.children, ['identi_fier_2'])

    def test_set_parent(self):
        """Tests setting the parent."""
        self.node1.parent = " identi fier  1"
        self.assertEqual(self.node1.parent, 'identi_fier__1')

    def test_set_data(self):
        """Tests setting the data for a Node."""
        self.node1.data = {1: 'hello', "two": 'world'}
        self.assertEqual(self.node1.data, {1: 'hello', "two": 'world'})


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
