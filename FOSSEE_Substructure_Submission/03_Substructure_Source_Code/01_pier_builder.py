"""
Pier Component Builder (Geometry & Reinforcement)
Vertical circular concrete pier with internal longitudinal rebars and circular ties.
"""

import math
try:
    from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeTorus
    from OCC.Core.BRep import BRep_Builder
    from OCC.Core.TopoDS import TopoDS_Compound
except ImportError:
    pass


def build_pier(
    *,
    diameter=800.0,
    height=3000.0,
    center_x=0.0,
    center_y=0.0,
    top_z=0.0,
    rebar_main_diameter=16.0,
    rebar_spacing_longitudinal=150.0,
    rebar_transverse_diameter=8.0,
    rebar_spacing_transverse=200.0,
    rebar_cover=40.0
):
    """
    Builds a parametric vertical cylindrical concrete pier with internal steel cage.

    Orientation:
        - Cylinder axis: (0, 0, -1) from top_z downwards by height.
    """
    radius = diameter / 2.0
    bot_z = top_z - height

    # 1. Concrete cylinder
    origin = gp_Pnt(center_x, center_y, bot_z)
    axis = gp_Ax2(origin, gp_Dir(0, 0, 1))
    concrete_solid = BRepPrimAPI_MakeCylinder(axis, radius, height).Shape()

    # 2. Reinforcement
    rebar_shapes = []
    r_main = rebar_main_diameter / 2.0
    r_trans = rebar_transverse_diameter / 2.0

    # Radius of main longitudinal rebar cage
    cage_radius = radius - rebar_cover - r_trans - r_main
    if cage_radius < 50.0:
        cage_radius = radius - rebar_cover

    # Number of longitudinal bars based on perimeter and spacing
    perimeter = 2.0 * math.pi * cage_radius
    n_bars = max(8, int(round(perimeter / rebar_spacing_longitudinal)))
    angle_step = 2.0 * math.pi / n_bars

    bar_len = max(100.0, height - 2.0 * rebar_cover)
    bar_bot_z = bot_z + rebar_cover

    for i in range(n_bars):
        angle = i * angle_step
        bx = center_x + cage_radius * math.cos(angle)
        by = center_y + cage_radius * math.sin(angle)
        bar_axis = gp_Ax2(gp_Pnt(bx, by, bar_bot_z), gp_Dir(0, 0, 1))
        bar = BRepPrimAPI_MakeCylinder(bar_axis, r_main, bar_len).Shape()
        rebar_shapes.append(bar)

    # Transverse circular ties/hoops
    hoop_radius = radius - rebar_cover - r_trans
    n_hoops = max(2, int(bar_len / rebar_spacing_transverse) + 1)
    dz_hoop = bar_len / max(1, (n_hoops - 1))

    for k in range(n_hoops):
        hz = bar_bot_z + k * dz_hoop
        hoop_axis = gp_Ax2(gp_Pnt(center_x, center_y, hz), gp_Dir(0, 0, 1))
        # Torus: major radius = hoop_radius, minor radius = r_trans
        if hoop_radius > r_trans:
            hoop = BRepPrimAPI_MakeTorus(hoop_axis, hoop_radius, r_trans).Shape()
            rebar_shapes.append(hoop)

    # Compound reinforcement
    rebar_compound = None
    if rebar_shapes:
        b = BRep_Builder()
        c = TopoDS_Compound()
        b.MakeCompound(c)
        for shp in rebar_shapes:
            b.Add(c, shp)
        rebar_compound = c

    return {
        "concrete": concrete_solid,
        "rebar": rebar_shapes,
        "rebar_compound": rebar_compound,
        "parameters": {
            "diameter": diameter,
            "height": height,
            "center_x": center_x,
            "center_y": center_y,
            "top_z": top_z,
            "bot_z": bot_z,
            "cage_radius": cage_radius,
            "n_bars": n_bars
        }
    }
