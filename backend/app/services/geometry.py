from typing import Sequence


def get_bottom_center(bbox: dict) -> tuple[float, float]:
    """
    Return the bottom-center point of a detection bounding box.

    Expected bbox:
    {
        "x1": 100,
        "y1": 150,
        "x2": 300,
        "y2": 450
    }
    """
    x1 = float(bbox["x1"])
    y1 = float(bbox["y1"])
    x2 = float(bbox["x2"])
    y2 = float(bbox["y2"])

    center_x = (x1 + x2) / 2
    bottom_y = y2

    return center_x, bottom_y


def point_in_polygon(
    point: tuple[float, float],
    polygon: Sequence[Sequence[float]],
) -> bool:
    """
    Return True when a point lies inside a polygon.

    Polygon format:
    [
        [x1, y1],
        [x2, y2],
        [x3, y3],
        ...
    ]
    """
    x, y = point
    inside = False

    j = len(polygon) - 1

    for i in range(len(polygon)):
        xi, yi = float(polygon[i][0]), float(polygon[i][1])
        xj, yj = float(polygon[j][0]), float(polygon[j][1])

        intersects = (
            (yi > y) != (yj > y)
            and x < (xj - xi) * (y - yi) / (yj - yi) + xi
        )

        if intersects:
            inside = not inside

        j = i

    return inside


def detection_is_inside_zone(
    bbox: dict,
    geometry: Sequence[Sequence[float]],
) -> bool:
    """
    Check whether the detection's bottom-center lies inside the zone.
    """
    point = get_bottom_center(bbox)

    return point_in_polygon(
        point=point,
        polygon=geometry,
    )