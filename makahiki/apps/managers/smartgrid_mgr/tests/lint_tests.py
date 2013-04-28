'''
Created on Mar 26, 2013

@author: Cam Moore
'''
import unittest
from apps.managers.smartgrid_mgr import unlock_lint


class Test(unittest.TestCase):
    """Tests for unlock_lint."""

    def testDesignerActions(self):
        """Prints out the longer dependency trees."""
        trees = unlock_lint.build_designer_trees()
        for k in list(trees):
            t = trees[k]
#            if len(t.nodes) > 1:
#            t.show()
            if len(t.nodes) > 3:
                print t.tostring()

    def testUnreachable(self):
        """Returns the unreachable actions."""
        slugs = unlock_lint.get_unreachable_designer_actions()
        print "Unreachable actions: %s" % slugs

    def testFalseUnlock(self):
        """Returns the actions with False unlock_conditions."""
        slugs = unlock_lint.get_false_unlock_designer_actions()
        print "False unlock conditions: %s" % slugs

    def testMissmatchedLevel(self):
        """Returns the actions with a level lower than the action they depend on."""
        slugs = unlock_lint.get_missmatched_designer_level()
        print "Mismatched levels: %s" % slugs

#    def testLibraryActions(self):
#        print "*****************************************"
#        trees = build_trees(LibraryAction)
#        for k in list(trees):
#            t = trees[k]
#            if len(t.nodes) > 1:
#                t.show()
#        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
