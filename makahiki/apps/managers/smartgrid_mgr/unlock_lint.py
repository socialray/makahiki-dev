'''Lint for DesignerAction unlock_conditions.
Based upon pyTree by caesar0301, https://github.com/caesar0301/pyTree

Created on Mar 26, 2013

@author: Cam Moore
'''
import uuid
from collections import deque
from apps.widgets.smartgrid_design.models import DesignerAction, DesignerGrid, DesignerEvent
from apps.managers.challenge_mgr.models import RoundSetting
from apps.managers.challenge_mgr import challenge_mgr

(_ADD, _DELETE, _INSERT) = range(3)
(_ROOT, _DEPTH, _WIDTH) = range(3)


def sanitize_string(s):
    """Creates a slug out of a string by replacing spaces with _."""
    return s.strip().replace(" ", "_")


class Node(object):  # pylint: disable=R0902
    """Node in unlock condition tree. Name is the slug of the action, parent is slug of
    condition dependance."""

    def __init__(self, name, pk, action_type, unlock_condition, level=None, identifier=None, \
                 expanded=True):
        """initializer."""
        self.__identifier = (str(uuid.uuid1()) if identifier is None else
                             sanitize_string(str(identifier)))
        self.name = name
        self.pk = pk
        self.action_type = action_type
        self.unlock_condition = unlock_condition
        self.level = level
        self.expanded = expanded
        self.__parent = None
        self.__children = []

    def __unicode__(self):
        return "%s[%s]" % (self.name, self.unlock_condition)

    def __str__(self):
        return "%s[%s]" % (self.name, self.unlock_condition)

    def __repr__(self):
        return "<Node: %s[%s]>" % (self.name, self.unlock_condition)

    def admin_link(self):
        """returns the hardcoded link to edit the action."""
        return "<a href='/challenge_setting_admin/smartgrid_design/designer%s/%s/'>%s</a>" % \
            (self.action_type, self.pk, self.name)

    @property
    def identifier(self):
        """Gets the Identifier property."""
        return self.__identifier

    @property
    def parent(self):
        """Gets the Parent property."""
        return self.__parent

    @parent.setter
    def parent(self, value):
        """Sets the Parent property."""
        if value is not None:
            self.__parent = sanitize_string(value)

    @property
    def children(self):
        """Gets the Children property."""
        return self.__children

    @children.setter
    def children(self, value):
        """Sets the Children property."""
        if value is not None and isinstance(value, list):
            self.__children = value

    def update_children(self, identifier, mode=_ADD):
        """Updates the children with the given identifier and mode."""
        sane = sanitize_string(identifier)
        if mode is _ADD:
            if sane not in self.__children:
                self.__children.append(sane)
        elif mode is _DELETE:
            if sane in self.__children:
                self.__children.remove(sane)
        elif mode is _INSERT:
            self.__children = [sane]
# pylint: enable=R0902


class MultipleRootError(Exception):
    """Multiple Root problem in Tree."""
    pass


class Tree(object):
    """Tree of Nodes."""
    def __init__(self):
        """initializer."""
        self.nodes = {}
        self.root = None

    def add_node(self, node, parent=None):
        """Adds a Node to the Tree."""
        if parent is None:
            if self.root is not None:
                raise MultipleRootError
            else:
                self.root = node.identifier
        try:
            self.nodes[node.identifier]
        except KeyError:
            self.nodes.update({node.identifier: node})
        self.__update_children(parent, node.identifier, _ADD)
        node.parent = parent

    def create_node(self, name, pk, action_type, unlock_condition, level=None, identifier=None, \
                    parent=None):
        """Create a child node for the node indicated by the 'parent' parameter"""
        node = Node(name, pk, action_type, unlock_condition, level=level, identifier=identifier)
        self.add_node(node, parent)
        return node

    def expand_tree(self, nid=None, mode=_DEPTH, filter_fn=None):
        """expands the tree."""
        # Python generator. Loosly based on an algorithm from 'Essential LISP' by
        # John R. Anderson, Albert T. Corbett, and Brian J. Reiser, page 239-241
        def real_true(pos):
            """always return True."""
            _ = pos
            return True

        if nid is None:
            nid = self.root
        if filter_fn is None:
            filter_fn = real_true

        if filter_fn(nid):
            yield nid
            queue = self[nid].children
            while queue:
                if filter_fn(queue[0]):
                    yield queue[0]
                    expansion = self[queue[0]].children
                    if mode is _DEPTH:
                        queue = expansion + queue[1:]  # depth-first
                    elif mode is _WIDTH:
                        queue = queue[1:] + expansion  # width-first
                else:
                    queue = queue[1:]

    def get_node(self, nid):
        """Returns the node with the given nid, or None if node is not in the tree."""
        try:
            return self.nodes[nid]
        except KeyError:
            return None

    def is_branch(self, nid):
        """Return the following nodes of [nid]"""
        return self[nid].children

    def move_node(self, source, destination):
        """Move a node indicated by the 'source' parameter to the parent node
        indicated by the 'dest' parameter"""
        parent = self[source].parent
        self.__update_children(parent, source, _DELETE)
        self.__update_children(destination, source, _ADD)
        self.__update_parent(source, destination)

    def paste(self, nid, new_tree):
        """Paste a new tree to the original one by linking the root
of new tree to nid."""
        assert isinstance(new_tree, Tree)

        # check identifier replication

        if set(new_tree.nodes) & set(self.nodes):
            # error, duplicate node identifier
            raise ValueError('Duplicated nodes exists.')

        new_tree[new_tree.root].parent = nid
        self.__update_children(nid, new_tree.root, _ADD)
        self.nodes.update(new_tree.nodes)

    def remove_node(self, identifier):
        """Remove a node indicated by 'identifier'. All the successors are removed, too."""
        parent = self[identifier].parent
        remove = []  # temp. list for nodes which will be removed
        for pid in self.expand_tree(identifier):
            # check if node has children
            # true -> run remove_node with child_id
            # no -> delete node
            remove.append(pid)

        for pid in remove:
            del(self.nodes[pid])

        self.__update_children(parent, identifier, _DELETE)

    def rsearch(self, nid, filter_fn=None):
        """Search the tree from nid to the root along links reversedly."""

        def real_true(p):
            """always return True."""
            _ = p
            return True

        if filter_fn is None:
            filter_fn = real_true
        current = nid
        while current is not None:
            if filter_fn(current):
                yield current
            current = self[current].parent

    def show(self, nid=None, level=_ROOT):
        """"Another implementation of printing tree using Stack
Print tree structure in hierarchy style.
For example:
Root
|___ C01
| |___ C11
| |___ C111
| |___ C112
|___ C02
|___ C03
| |___ C31
A more elegant way to achieve this function using Stack structure,
for constructing the Nodes Stack push and pop nodes with additional level info."""
        leading = ''
        lasting = '|___ '

        if nid is None:
            nid = self.root
        label = "{0}:{1}[{2}]".format(self[nid].level, self[nid].name, self[nid].unlock_condition)

        queue = self[nid].children
        #print level
        if level == _ROOT:
            print(label)
        else:
            if level <= 1:
                leading += ('|' + ' ' * 4) * (level - 1)
            else:
                leading += ('|' + ' ' * 4) + (' ' * 5 * (level - 2))
            print("{0}{1}{2}".format(leading, lasting, label))

        if self[nid].expanded:
            level += 1
            for element in queue:
                self.show(element, level)  # recursive call

    def tohtmlstring(self, nid=None):
        """builds string like show w/o recursion."""
        s = ''
        lvl = _ROOT
        nodes_to_visit = deque([])
        if nid is None:
            nid = self.root
        nodes_to_visit.append((self[nid], lvl))
        while len(nodes_to_visit) > 0:
            leading = ''
            lasting = '|___ '
            current_node, lvl = nodes_to_visit.popleft()
            for c in current_node.children:
#                print "child {0} lvl{1}".format(self[c], lvl + 1)
                nodes_to_visit.appendleft((self[c], lvl + 1))
#            print "process = {0} lvl{1}".format(current_node, lvl)

            label = "{0}: <b>{1}</b>[{2}]".format(current_node.level, \
                                                  current_node.admin_link(), \
                                                  current_node.unlock_condition)
            if lvl == _ROOT:
                s += label + '<br/>'
            else:
                if lvl <= 1:
                    leading += ('|' + '&nbsp' * 4) * (lvl - 1)
                else:
                    leading += ('|' + '&nbsp' * 4) + ('&nbsp' * 5 * (lvl - 2))
                s += "{0}{1}{2}".format(leading, lasting, label) + '<br/>'
        return s

    def subtree(self, nid):
        """Return a COPY of subtree of the whole tree with the nid being the new root.
And the structure of the subtree is maintained from the old tree."""
        st = Tree()
        st.root = nid
        for node_n in self.expand_tree(nid):
            st.nodes.update({self[node_n].identifier: self[node_n]})
        return st

    def __contains__(self, identifier):
        """Returns something."""
        return [node.identifier for node in self.nodes
                if node.identifier is identifier]

    def __getitem__(self, key):
        """Returns something."""
        return self.nodes.get(key)

    def __len__(self):
        """Returns something."""
        return len(self.nodes)

    def __setitem__(self, key, item):
        """Returns something."""
        self.nodes.update({key: item})

    def __update_parent(self, nid, identifier):
        """Returns something."""
        self[nid].parent = identifier

    def __update_children(self, nid, identifier, mode):
        """Returns something."""
        if nid is None:
            return False
        else:
            if self[nid]:
                self[nid].update_children(identifier, mode)
                return True
            return False

    def __repr__(self):
        return "<Tree: %s>" % (self.root)


def _build_designer_nodes():
    """Builds a list of all the DesignerAction nodes."""
    nodes = []
    for action in DesignerAction.objects.all():
        locations = DesignerGrid.objects.filter(action=action)
        if len(locations) == 0:
            pass
        else:
            for loc in locations:
                nodes.append(Node(action.slug, action.pk, action.type, action.unlock_condition, \
                                  loc.level, identifier=action.slug))
    return nodes


def _is_in_round(date, roundsetting):
    """Returns True if the given date is in the given round."""
    return date >= roundsetting.start and date <= roundsetting.end


def _is_in_challenge(date):
    """Returns True if the given date is in any of the roundsettings."""
    ret = False
    for r in RoundSetting.objects.all():
        ret = ret or _is_in_round(date, r)
    return ret


def build_designer_trees():
    """Builds the unlock_trees for the DesignerActions in the Grid."""
    nodes = _build_designer_nodes()
    trees = {}
    for node in nodes:
        if node.unlock_condition == "True" or node.unlock_condition.find("or True") != -1 \
        or node.unlock_condition == "False" or node.unlock_condition.find("and False") != -1:
            t = Tree()
            t.create_node(node.name, node.pk, node.action_type, node.unlock_condition, \
                          level=node.level, identifier=node.identifier)
            trees[node.name] = t
    for node in nodes:
        slugs = get_submitted_action_slugs(node)
        for slug in slugs:
            for k in list(trees):
                if trees[k].get_node(slug):
                    trees[k].add_node(node, slug)
    # second pass because adding in the wrong order may cause problems
    for node in nodes:
        slugs = get_submitted_action_slugs(node)
        for slug in slugs:
            for k in list(trees):
                if trees[k].get_node(slug):
                    trees[k].add_node(node, slug)
#                else:
#                    print "%s doesn't have %s in it." % (k, slug)
    return trees


def get_submitted_action_slugs(node):
    """Returns the action slugs from the given node's unlock_condition."""
    ret = []
    l = node.unlock_condition.split('submitted_action(')
    if len(l) > 1:
        index = l[1].find(')')
        ret.append(l[1][:index].strip('"\''))
        if len(l) > 2:
            index = l[1].find(')')
            ret.append(l[2][:index].strip('"\''))
    return ret


def get_unreachable_designer_actions():
    """Returns the slug for actions that are not in any tree for DesignerActions
    These actions are not reachable so they will not be unlocked."""
    ret = []
    nodes = _build_designer_nodes()
    trees = build_designer_trees()
    # check all the nodes
    for node in nodes:
        in_tree = False
        for k in list(trees):
            tree = trees[k]
            if tree.get_node(node.identifier):
                in_tree = True
        if not in_tree:
            ret.append("%s: %s" % (node.admin_link(), node.unlock_condition))
    return ret


def get_false_unlock_designer_actions():
    """Returns the slug for DesignerActions whose root unlock_condition is False."""
    ret = []
    trees = build_designer_trees()
    for k in list(trees):
        tree = trees[k]
        root = tree.get_node(tree.root)
        if root:
            if root.unlock_condition == "False" or  root.unlock_condition.find("and False") != -1:
                # add all nodes in tree to list
                for node_key in list(tree.nodes):
                    node = tree.nodes[node_key]
                    if not node.name in ret and not node.name.startswith('filler'):
                        ret.append(node.name)
    return ret


def get_missmatched_designer_level():
    """Returns the slug for actions whose parent level is higher than their own."""
    ret = []
    trees = build_designer_trees()
    for k in list(trees):
        tree = trees[k]
        for node_key in list(tree.nodes):
            node = tree.nodes[node_key]
            if node.level:
                parent_name = node.parent
                if parent_name:
                    parent = tree.nodes[parent_name]
                    if parent and parent.level and parent.level.priority > node.level.priority:
                        if node.admin_link() not in ret:
                            ret.append(node.admin_link())
    return ret


def check_pub_exp_dates():
    """Returns a list of DesignerAction slugs whose pub_date or exp_date are not in the
     challenge."""
    ret = []
    trees = build_designer_trees()
    challenge_start = challenge_mgr.get_challenge_start()
    challenge_end = challenge_mgr.get_challenge_end()
    # check only DesignerActions in the grid?
    for action in DesignerAction.objects.all():
        if action.pub_date > challenge_end.date() or (action.expire_date and \
                                                      action.expire_date < challenge_start.date()):
            for k in list(trees):
                tree = trees[k]
                node = tree.get_node(action.slug)
                if node:
                    ret.append(node.admin_link())
    return ret


def check_event_dates():
    """Returns a list of DesignerEvent slugs whose event date are not in the challenge."""
    ret = []
    for event in DesignerEvent.objects.all():
        if not _is_in_challenge(event.event_date):
            ret.append(event.slug)
    return ret
