'''Helper functions for the Smart Grid Game Library and grid instance.
Created on Mar 15, 2013

@author: Carleton Moore
'''

from django.db.models.deletion import Collector
from django.db.models.fields.related import ForeignKey
from apps.widgets.smartgrid.models import Action, Activity, Commitment, Event, Filler, ColumnName, \
    Level, TextPromptQuestion, Grid, ColumnGrid
from django.shortcuts import get_object_or_404
from apps.widgets.smartgrid_library.models import LibraryAction, LibraryActivity, \
    LibraryCommitment, LibraryEvent, LibraryColumnName, LibraryTextPromptQuestion
from django.http import Http404
from apps.widgets.smartgrid_design.models import DesignerAction, DesignerColumnName, \
    DesignerActivity, DesignerCommitment, DesignerEvent, DesignerFiller, DesignerLevel,\
    DesignerTextPromptQuestion, DesignerGrid, DesignerColumnGrid
import os
from django.core.management import call_command


def duplicate(obj, value=None, field=None, duplicate_order=None):  # pylint: disable=R0914
    """
    Duplicate all related objects of obj setting
    field to value. If one of the duplicate
    objects has an FK to another duplicate object
    update that as well. Return the duplicate copy
    of obj.
    duplicate_order is a list of models which specify how
    the duplicate objects are saved. For complex objects
    this can matter. Check to save if objects are being
    saved correctly and if not just pass in related objects
    in the order that they should be saved.
    """
    collector = Collector({})
    collector.collect([obj])
    collector.sort()
    related_models = collector.data.keys()
    data_snapshot = {}
    for key in collector.data.keys():
        data_snapshot.update({key: dict(zip([item.pk for item in collector.data[key]], \
                                            [item for item in collector.data[key]]))})
    root_obj = None

    # Sometimes it's good enough just to save in reverse deletion order.
    if duplicate_order is None:
        duplicate_order = reversed(related_models)

    for model in duplicate_order:

        # Find all FKs on model that point to a related_model.
        fks = []
        for f in model._meta.fields:
            if isinstance(f, ForeignKey) and f.rel.to in related_models:
                fks.append(f)
        # Replace each `sub_obj` with a duplicate.
        if model not in collector.data:
            continue
        sub_objects = collector.data[model]
        for obj in sub_objects:
            for fk in fks:
                fk_value = getattr(obj, "%s_id" % fk.name)
                # If this FK has been duplicated then point to the duplicate.
                fk_rel_to = data_snapshot[fk.rel.to]
                if fk_value in fk_rel_to:
                    dupe_obj = fk_rel_to[fk_value]
                    setattr(obj, fk.name, dupe_obj)
            # Duplicate the object and save it.
            obj.id = None
            if field is None or field != 'slug':
                slug = obj.slug
                obj.slug = slug + '-copy'
            if field is not None:
                setattr(obj, field, value)
            obj.save()
            if root_obj is None:
                root_obj = obj
    return root_obj
# pylint: enable=R0914


def check_designer_vs_library():
    """Checks the slugs in the designer vs the library. Returns
list of slugs in designer not in library."""
    l = []
    for des_action in DesignerAction.objects.all():
        slug = des_action.slug
        try:
            get_library_action(slug)
        except Http404:
            l.append(slug)
    return l


def is_library(obj):
    """Returns True if the object is a Library instance."""
    cls = type(obj).__name__
    return cls.startswith('Library')


def is_designer(obj):
    """Returns True if the object is a Designer instance."""
    cls = type(obj).__name__
    return cls.startswith('Designer')


def is_smartgrid(obj):
    """Returns True if the object is a SmartGrid instance."""
    return not (is_library(obj) or is_designer(obj))


def _copy_fields(orig, copy):
    """Copies the field values from orig to copy and saves the copy."""
    for f in orig._meta.fields:
        if f.name != 'id':
            value = getattr(orig, f.name)
            setattr(copy, f.name, value)
    copy.save()


def _copy_fields_no_foriegn_keys(orig, copy):
    """Copies the field values from orig to copy and saves the copy."""
    fks = []
    for f in orig._meta.fields:
        if isinstance(f, ForeignKey):
            fks.append(f.name)
#    print fks
    for f in orig._meta.fields:
        if f.name != 'id' and not f.name in fks:
            value = getattr(orig, f.name)
            setattr(copy, f.name, value)


def _copy_action_fields(orig, copy):  # pylint: disable=R0912
    """Copies the field values from orig to copy and saves the copy."""
    # Find all FKs on model that point to a related_model.
    fks = []
    copy_fields = []
    for f in copy._meta.fields:
        copy_fields.append(f.name)
        if isinstance(f, ForeignKey):
            fks.append(f.name)
#     print copy_fields
    orig_fields = []
    for f in orig._meta.fields:
        orig_fields.append(f.name)
        if f.name in copy_fields:
            if f.name != 'id':
                if f.name not in fks:
                    value = getattr(orig, f.name)
                    setattr(copy, f.name, value)
                else:
                    print f.name
                    value = getattr(orig, f.name)
                    setattr(copy, f.name, value)
#     print orig_fields
    copy.save()  # pylint: enable=R0912


def _admin_link(action):
    """returns the hardcoded link to edit the action."""
    return "<a href='/challenge_setting_admin/smartgrid_design/designer%s/%s/'>%s</a>" % \
        (action.type, action.pk, action.name)


def instantiate_designer_column_from_library(slug):
    """Instantiates a DesignerColumnName from the LibraryColumnName with the given slug."""
    lib_cat = get_object_or_404(LibraryColumnName, slug=slug)
    des_col = None
    try:
        des_col = get_object_or_404(DesignerColumnName, slug=slug)
    except Http404:
        des_col = DesignerColumnName()
    _copy_fields(lib_cat, des_col)
    return des_col


def instantiate_designer_from_library(slug):
    """Instantiates a Smart Grid Game Design instance from the Smart Grid Game Library instance.
    slug is the slug value for the library instance. If the Design instance exists it is over
    written."""
    lib_obj = get_library_action(slug)
    action_type = lib_obj.type
    exist_obj = None
    try:
        exist_obj = get_designer_action(slug)
    except Http404:
        exist_obj = None
    design_obj = None
    if exist_obj == None:
        if action_type == 'activity':
            design_obj = DesignerActivity()
            lib_obj = LibraryActivity.objects.get(slug=slug)
        if action_type == 'commitment':
            design_obj = DesignerCommitment()
            lib_obj = LibraryCommitment.objects.get(slug=slug)
        if action_type == 'event':
            design_obj = DesignerEvent()
            lib_obj = LibraryEvent.objects.get(slug=slug)
        if action_type == 'filler':
            design_obj = DesignerFiller()
    else:  # use the existing instance.
        design_obj = exist_obj

    _copy_action_fields(lib_obj, design_obj)

    # Copy all the LibraryTextPropmtQuestions
    for question in LibraryTextPromptQuestion.objects.filter(libraryaction=lib_obj):
        des_obj = DesignerTextPromptQuestion()
        _copy_fields_no_foriegn_keys(question, des_obj)
        des_obj.action = get_designer_action(slug)
        des_obj.save()

    return design_obj


def instantiate_designer_column_from_grid(slug):
    """Creates a DesignerColumnName from the ColumnName with the given slug."""
    cat = get_object_or_404(ColumnName, slug=slug)
    des_cat = None
    try:
        des_cat = get_object_or_404(DesignerColumnName, slug=slug)
    except Http404:
        des_cat = DesignerColumnName()
    _copy_fields(cat, des_cat)
    return des_cat


def instantiate_designer_from_grid(slug):
    """Creates a designer instance from the Smart Grid instance."""
    grid_obj = get_smartgrid_action(slug)
    action_type = grid_obj.type
    old_obj = None
    try:
        old_obj = get_designer_action(slug)
    except Http404:
        old_obj = None
    designer_obj = None
    if old_obj == None:
        if action_type == 'activity':
            designer_obj = DesignerActivity()
            grid_obj = Activity.objects.get(slug=slug)
        if action_type == 'commitment':
            designer_obj = DesignerCommitment()
            grid_obj = Commitment.objects.get(slug=slug)
        if action_type == 'event':
            designer_obj = DesignerEvent()
            grid_obj = Event.objects.get(slug=slug)
        if action_type == 'filler':
            designer_obj = DesignerFiller()
            grid_obj = Filler.objects.get(slug=slug)
    else:
        designer_obj = old_obj
    _copy_action_fields(grid_obj, designer_obj)

    # Copy all the TextPropmtQuestions
    for question in TextPromptQuestion.objects.filter(action=grid_obj):
        des_obj = DesignerTextPromptQuestion()
        _copy_fields_no_foriegn_keys(question, des_obj)
        des_obj.action = get_designer_action(slug)
        des_obj.save()

    return designer_obj


def instantiate_grid_level_from_designer(designer_level):
    """Creates a Smart Grid Level from the DesignerLevel."""
    level = None
    try:
        level = get_smartgrid_level(designer_level.slug)
    except Http404:
        level = Level()
    _copy_fields(designer_level, level)
    return level


def instantiate_grid_column_from_designer(designer_col):
    """Creates a Smart Grid ColumnName from the DesignerColumnName."""
    col = None
    try:
        col = get_smartgrid_column_name(designer_col.slug)
    except Http404:
        col = ColumnName()
    _copy_fields(designer_col, col)
    return col


def instantiate_grid_action_from_designer(designer_action):
    """Creates a Smart Grid instance from the designer instance."""
    action_type = designer_action.type
    old_obj = None
    try:
        old_obj = get_smartgrid_action(designer_action.slug)
    except Http404:
        old_obj = None
    grid_action = None
    if old_obj == None:
        if action_type == 'activity':
            grid_action = Activity()
        if action_type == 'commitment':
            grid_action = Commitment()
        if action_type == 'event':
            grid_action = Event()
        if action_type == 'filler':
            grid_action = Filler()
    else:
        grid_action = old_obj
    _copy_action_fields(designer_action, grid_action)

    # Copy all the DesignerTextPropmtQuestions
    for question in DesignerTextPromptQuestion.objects.filter(action=designer_action):
        des_obj = TextPromptQuestion()
        _copy_fields_no_foriegn_keys(question, des_obj)
        des_obj.action = get_smartgrid_action(designer_action.slug)
        des_obj.save()

    return grid_action


def get_designer_action(slug):
    """Returns the Smart Grid Game Designer Action for the given slug."""
    action = get_object_or_404(DesignerAction, slug=slug)
    if action.type == 'activity':
        return DesignerActivity.objects.get(slug=slug)
    if action.type == 'commitment':
        return DesignerCommitment.objects.get(slug=slug)
    if action.type == 'event':
        return DesignerEvent.objects.get(slug=slug)
    if action.type == 'filler':
        return DesignerFiller.objects.get(slug=slug)
    return action


def get_designer_action_slugs():
    """Returns the DesignerAction slugs that are currently in the Smart Grid Designer.
    This includes the actions in the palette that don't have levels or categories."""
    action_list = []
    for action in DesignerAction.objects.all():
        action_list.append(action.slug)
    return action_list


def get_designer_column_name(slug):
    """Return the Smart Grid Game DesignerColumnName for the given slug."""
    return get_object_or_404(DesignerColumnName, slug=slug)


def get_designer_column_name_slugs():
    """Returns the DesignerColumnName slugs that are currently in the Smart Grid Designer."""
    slugs = []
    for cat in DesignerColumnGrid.objects.all():
        slugs.append(cat.name.slug)
    return slugs


def get_designer_level(slug):
    """Return the DesignerLevel for the given slug."""
    return get_object_or_404(DesignerLevel, slug=slug)


def get_library_action(slug):
    """Returns the Smart Grid Game Library Action for the given slug."""
    action = get_object_or_404(LibraryAction, slug=slug)
    pk = action.pk
    if action.type == 'activity':
        return LibraryActivity.objects.get(pk=pk)
    if action.type == 'commitment':
        return LibraryCommitment.objects.get(pk=pk)
    if action.type == 'event':
        return LibraryEvent.objects.get(pk=pk)
    return action


def get_library_column_name(slug):
    """Return the Smart Grid Game LibraryColumnName for the given slug."""
    return get_object_or_404(LibraryColumnName, slug=slug)


def get_smartgrid_action(slug):
    """returns the action object by slug."""
    action = get_object_or_404(Action, slug=slug)
    pk = action.pk
    if action.type == 'activity':
        try:
            return Activity.objects.get(pk=pk)
        except Activity.DoesNotExist:
            print "%s, pk = %s" % (slug, pk)
    if action.type == 'commitment':
        return Commitment.objects.get(pk=pk)
    if action.type == 'event':
        return Event.objects.get(pk=pk)
    if action.type == 'filler':
        return Filler.objects.get(pk=pk)
    return action


def get_smartgrid_action_slugs():
    """Returns the Actions that are currently in the Smart Grid."""
    action_list = []
    for grid in Grid.objects.all():
        if grid.action.slug not in action_list:
            action_list.append(grid.action.slug)
    return action_list


def get_smartgrid_column_name(slug):
    """returns the ColumnName object by slug."""
    return get_object_or_404(ColumnName, slug=slug)


def get_smartgrid_level(slug):
    """Returns the Level for the given slug."""
    return get_object_or_404(Level, slug=slug)


def get_smartgrid():
    """Returns the currently defined smart grid."""
    levels = []
    return levels


def get_designer_grid():
    """Returns the smart grid as defined in the Smart Grid Designer. The
    grid is a list of lists with the format [<DesignerLevel>, [<DesignerColumnName>*],
    [<DesignerAction>*], [active columns]"""
    ret = []
    for level in DesignerLevel.objects.all():
        level_ret = []
        level_ret.append(level)
        level_ret.append(DesignerColumnGrid.objects.filter(level=level))
        level_ret.append(DesignerGrid.objects.filter(level=level))
        columns = []
        for cat in level_ret[1]:
            if cat.column not in columns:
                columns.append(cat.column)
        for act in level_ret[2]:
            if act.column not in columns:
                columns.append(act.column)
        level_ret.append(columns)
        ret.append(level_ret)
    return ret


def get_designer_palette():
    """Returns the DesignerActions with no Level or no Column.  These actions will not
    appear in the grid if published."""
    palette = []
    for action in DesignerAction.objects.all():
        if len(DesignerGrid.objects.filter(action=action)) == 0:
            palette.append(action)
    return palette


def clear_designer():
    """Deletes all the instances in the designer."""
    for obj in DesignerLevel.objects.all():
        obj.delete()
    for obj in DesignerColumnName.objects.all():
        obj.delete()
    for obj in DesignerAction.objects.all():
        obj.delete()
    for obj in DesignerColumnGrid.objects.all():
        obj.delete()
    for obj in DesignerGrid.objects.all():
        obj.delete()


def copy_smartgrid_to_designer():
    """Copies the current Smart Grid Game to the designer instances."""
    # Clear out the Designer
    clear_designer()
    # Copy the levels
    for lvl in Level.objects.all():
        try:
            des_lvl = get_object_or_404(DesignerLevel, slug=lvl.slug)
        except Http404:
            des_lvl = DesignerLevel()
        _copy_fields(lvl, des_lvl)
    # Copy the ColumnNames
    for col in ColumnName.objects.all():
        try:
            des_col = get_object_or_404(DesignerColumnName, slug=col.slug)
        except Http404:
            des_col = DesignerColumnName()
        _copy_fields(col, des_col)
    # Copy the location information
    for grid in ColumnGrid.objects.all():
        col = DesignerColumnGrid()
        col.level = get_designer_level(grid.level.slug)
        col.column = grid.column
        col.name = get_designer_column_name(grid.name.slug)
        col.save()
    # Copy the Actions
    for action in Action.objects.all():
        instantiate_designer_from_grid(action.slug)
    # Copy the location information
    for grid in Grid.objects.all():
        loc = DesignerGrid()
        loc.level = get_designer_level(grid.level.slug)
        loc.column = grid.column
        loc.row = grid.row
        loc.action = get_designer_action(grid.action.slug)
        loc.save()


def clear_smartgrid():
    """Removes all the location information for the Smart Grid.
    Deletes the existing levels.  Does not affect the Smart Grid Actions."""
    for level in Level.objects.all():
        level.delete()
    for row in ColumnGrid.objects.all():
        row.delete()
    for row in Grid.objects.all():
        row.delete()


def deploy_designer_to_smartgrid(use_filler):  # pylint: disable=R0914
    """Clears the current Smart Grid Game and copies the designer instances to the
    Smart Grid Game. Clearing the grid does not delete the actions just clears their
    Levels and Categories."""
    clear_smartgrid()
    # deploy the ColumnNames
    for col in DesignerColumnName.objects.all():
        instantiate_grid_column_from_designer(col)
    # deploy the actions
    for action in DesignerAction.objects.all():
        instantiate_grid_action_from_designer(get_designer_action(action.slug))
    # deploy the Levels
    for level in DesignerLevel.objects.all():
        instantiate_grid_level_from_designer(level)
    # set the ColumnGrid objects.
    for des_col in DesignerColumnGrid.objects.all():
        col = ColumnGrid()
        col.column = des_col.column
        col.level = get_smartgrid_level(des_col.level.slug)
        col.name = get_smartgrid_column_name(des_col.name.slug)
        col.save()
    # set the Grid objects.
    for des_row in DesignerGrid.objects.all():
        row = Grid()
        row.row = des_row.row
        row.column = des_row.column
        row.level = get_smartgrid_level(des_row.level.slug)
        row.action = get_smartgrid_action(des_row.action.slug)
        row.save()
    if use_filler:
        # need to instantiate the filler objects and put them in the grid.
        filler_count = len(Filler.objects.all())
        sizes = get_smart_grid_size()
        for slug in list(sizes):
            level = Level.objects.get(slug=slug)
            for c in range(1, sizes[slug][0] + 1):
                for r in range(1, sizes[slug][1] + 1):
                    cell = Grid.objects.filter(level=level, column=c, row=r)
                    if not cell:
                        filler_count += 1
                        name = 'Filler %s' % filler_count
                        filler_slug = 'filler-%s' % filler_count
                        filler = Filler(name=name, slug=filler_slug, type='filler', title=name)
                        filler.save()
                        grid = Grid(level=level, column=c, row=r, action=filler)
                        grid.save()  # pylint: enable=R0914


def get_smart_grid_size():
    """Returns the maximum columns and rows for each level in the smartgrid as a dictionary with
    the keys being the level slug and values being [num_column, num_row]."""
    ret = {}
    for level in Level.objects.all():
        num_column = 0
        for grid in ColumnGrid.objects.filter(level=level):
            if grid.column > num_column:
                num_column = grid.column
        num_row = 0
        for grid in Grid.objects.filter(level=level):
            if grid.column > num_column:
                num_column = grid.column
            if grid.row > num_row:
                num_row = grid.row
        ret[level.slug] = [num_column, num_row]

    return ret


def is_diff_between_designer_and_grid_action(slug):
    """Returns True if there is a difference between the Designer Action and
    Grid Action with the given slug."""
    grid = get_smartgrid_action(slug)
    fks = []
    for f in grid._meta.fields:
        if isinstance(f, ForeignKey):
            fks.append(f.name)
    designer = get_designer_action(slug)
    for f in grid._meta.fields:
        if f.name in fks:
            if not f.name.endswith('_ptr'):
                grid_val = getattr(grid, f.name).name
                designer_val = getattr(designer, f.name).name
                if grid_val != designer_val:
                    return True
        elif f.name != 'id':
            grid_val = getattr(grid, f.name)
            designer_val = getattr(designer, f.name)
            if grid_val != designer_val:
                return True
    return False


def diff_between_designer_and_grid_action(slug):  # pylint: disable=R0912
    """Returns a list of the fields that are different between the Designer Action and
    Grid Action with the given slug."""
    grid = None
    designer = None
    t = 'action'
    try:
        designer = get_designer_action(slug)
        t = designer.type
        grid = get_smartgrid_action(slug)
        t = grid.type
        fks = []
        for f in grid._meta.fields:
            if isinstance(f, ForeignKey):
                fks.append(f.name)
    except Http404:
        if grid == None:
            return ['is new ' + t + ' in grid']
        if designer == None:
            return ['not in designer but is in grid']
    diff = []
    for f in grid._meta.fields:
        if f.name in fks:
            if not f.name.endswith('_ptr'):
                grid_val = getattr(grid, f.name)
                if grid_val:
                    grid_val = grid_val.name
                designer_val = getattr(designer, f.name)
                if designer_val:
                    designer_val = designer_val.name
                if grid_val != designer_val:
                    diff.append(f.name)
        elif f.name != 'id':
            grid_val = getattr(grid, f.name)
            designer_val = getattr(designer, f.name)
            if grid_val != designer_val:
                diff.append(f.name)
    des_loc = DesignerGrid.objects.filter(action=designer)
    grid_loc = Grid.objects.filter(action=grid)
    if len(des_loc) == 1 and len(grid_loc) == 1:
        if des_loc[0].level.slug != grid_loc[0].level.slug:
            diff.append("moved from level %s to %s" % (grid_loc[0].level, des_loc[0].level))
        if des_loc[0].column != grid_loc[0].column:
            diff.append("column changed from %s to %s" % (grid_loc[0].column, des_loc[0].column))
        if des_loc[0].row != grid_loc[0].row:
            diff.append("row changed from %s to %s" % (grid_loc[0].row, des_loc[0].row))
    if len(des_loc) == 1 and len(grid_loc) == 0:
        diff.append("moved to %s from the palette" % des_loc[0].get_loc_str())
    if len(des_loc) == 0 and len(grid_loc) == 1:
        diff.append("moved out of the grid to the palette")
    return diff  # pylint: enable=R0912


def diff_between_designer_and_grid():
    """Returns a list of the action slugs and the changes for those slugs between the
    designer actions and smartgrid actions."""
    ret = []
    for action in DesignerAction.objects.all():
        slug = action.slug
        diff = diff_between_designer_and_grid_action(slug)
        if len(diff) > 0:
            inner = []
            inner.append(_admin_link(action))
            inner.append(diff)
            ret.append(inner)
    return ret


def load_example_grid(example_name):
    """Loads the Designer with the given example grid. If example_name doesn't exist, nothing
    is changed."""
#    manage_py = script_utils.manage_py_command()
#    manage_command = "python " + manage_py
    fixture_path = "fixtures"

    # Check to see if there is an example.
    for name in os.listdir(fixture_path):
        if name.startswith(example_name) and name.endswith("_designer.json"):
            # examples exists so clear the designer
            clear_designer()
            # load the example
            fixture = os.path.join(fixture_path, name)
            call_command('loaddata', '-v 0', fixture)
#            os.system("%s loaddata -v 0 %s" % (manage_command, fixture))
