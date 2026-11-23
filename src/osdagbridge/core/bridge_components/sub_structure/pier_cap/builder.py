"""
Pier Cap Component Builder (Geometry & Reinforcement)
Hammerhead / Trapezoidal concrete pier cap with internal steel reinforcement.
"""

import math
try:
    from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Ax2, gp_Dir, gp_Trsf
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder
    from OCC.Core.BRepBuilderAPI import (
        BRepBuilderAPI_MakePolygon,
        BRepBuilderAPI_MakeFace,
        BRepBuilderAPI_Transform
    )
    from OCC.Core.BRep import BRep_Builder
    from OCC.Core.TopoDS import TopoDS_Compound
except ImportError:
    pass


def build_pier_cap(
    *,
    top_width=3000.0,
    bottom_width=1200.0,
    depth=600.0,
    length=1200.0,
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
    Builds a parametric hammerhead/trapezoidal concrete pier cap and internal rebar.

    Orientation:
        - X-axis: along bridge span (length of pier cap)
        - Y-axis: transverse / deck width (tapers from bottom_width to top_width)
        - Z-axis: vertical (top_z downward by depth)
    """
    # 1. Concrete Trapezoidal Solid
    # In Y-Z plane at X = 0:
    # Top face: Z = top_z, Y from -top_width/2 to +top_width/2
    # Bottom face: Z = top_z - depth, Y from -bottom_width/2 to +bottom_width/2
    z_top = top_z
    z_bot = top_z - depth
    y_top_half = top_width / 2.0
    y_bot_half = bottom_width / 2.0

    poly = BRepBuilderAPI_MakePolygon()
    poly.Add(gp_Pnt(0.0, -y_bot_half, z_bot))
    poly.Add(gp_Pnt(0.0,  y_bot_half, z_bot))
    poly.Add(gp_Pnt(0.0,  y_top_half, z_top))
    poly.Add(gp_Pnt(0.0, -y_top_half, z_top))
    poly.Close()

    face = BRepBuilderAPI_MakeFace(poly.Wire()).Face()
    prism = BRepPrimAPI_MakePrism(face, gp_Vec(length, 0.0, 0.0)).Shape()

    # Translate so centered at (center_x, center_y)
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(center_x - length / 2.0, center_y, 0.0))
    concrete_solid = BRepBuilderAPI_Transform(prism, trsf, True).Shape()

    # 2. Reinforcement
    rebar_shapes = []
    r_main = rebar_main_diameter / 2.0
    r_trans = rebar_transverse_diameter / 2.0

    # Longitudinal rebars (running in X direction)
    # Placed near top and bottom faces, respecting cover
    x_start = center_x - length / 2.0 + rebar_cover
    rebar_len = max(100.0, length - 2.0 * rebar_cover)

    # Top mat: Z = z_top - rebar_cover - r_main
    z_top_mat = z_top - rebar_cover - r_main
    y_top_limit = y_top_half - rebar_cover - r_main

    # Bottom mat: Z = z_bot + rebar_cover + r_main
    z_bot_mat = z_bot + rebar_cover + r_main
    y_bot_limit = y_bot_half - rebar_cover - r_main

    # Generate top layer longitudinal bars
    n_top = max(2, int(round((2 * y_top_limit) / rebar_spacing_longitudinal)) + 1)
    if n_top > 1:
        dy_top = (2 * y_top_limit) / (n_top - 1)
        for i in range(n_top):
            y_bar = center_y - y_top_limit + i * dy_top
            axis = gp_Ax2(gp_Pnt(x_start, y_bar, z_top_mat), gp_Dir(1, 0, 0))
            bar = BRepPrimAPI_MakeCylinder(axis, r_main, rebar_len).Shape()
            rebar_shapes.append(bar)

    # Generate bottom layer longitudinal bars
    n_bot = max(2, int(round((2 * y_bot_limit) / rebar_spacing_longitudinal)) + 1)
    if n_bot > 1:
        dy_bot = (2 * y_bot_limit) / (n_bot - 1)
        for i in range(n_bot):
            y_bar = center_y - y_bot_limit + i * dy_bot
            axis = gp_Ax2(gp_Pnt(x_start, y_bar, z_bot_mat), gp_Dir(1, 0, 0))
            bar = BRepPrimAPI_MakeCylinder(axis, r_main, rebar_len).Shape()
            rebar_shapes.append(bar)

    # Transverse stirrups (closed rectangular/trapezoidal ties or cross bars)
    # Placed along X at rebar_spacing_transverse intervals
    n_trans = max(2, int(rebar_len / rebar_spacing_transverse) + 1)
    dx_trans = rebar_len / max(1, (n_trans - 1))

    for k in range(n_trans):
        x_pos = x_start + k * dx_trans
        # Top transverse bar
        axis_t = gp_Ax2(gp_Pnt(x_pos, center_y - y_top_limit, z_top_mat - r_main - r_trans), gp_Dir(0, 1, 0))
        bar_t = BRepPrimAPI_MakeCylinder(axis_t, r_trans, 2 * y_top_limit).Shape()
        rebar_shapes.append(bar_t)

        # Bottom transverse bar
        axis_b = gp_Ax2(gp_Pnt(x_pos, center_y - y_bot_limit, z_bot_mat + r_main + r_trans), gp_Dir(0, 1, 0))
        bar_b = BRepPrimAPI_MakeCylinder(axis_b, r_trans, 2 * y_bot_limit).Shape()
        rebar_shapes.append(bar_b)

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
            "top_width": top_width,
            "bottom_width": bottom_width,
            "depth": depth,
            "length": length,
            "center_x": center_x,
            "center_y": center_y,
            "top_z": top_z,
            "bot_z": z_bot
        }
    }
