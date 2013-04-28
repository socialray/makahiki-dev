"""Handle the rendering of the energy DEGG widget."""
from apps.widgets.status import status


def supply(request, page_name):
    """Supply the view_objects content."""
    _ = request
    _ = page_name

    return status.resource_goal_status("energy")
