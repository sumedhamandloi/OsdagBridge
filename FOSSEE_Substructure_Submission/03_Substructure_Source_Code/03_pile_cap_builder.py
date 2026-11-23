"""
Pile Cap Component Builder (Geometry & Reinforcement)
Rectangular prism concrete pile cap with top and bottom reinforcement mats.
"""

try:
    from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
    from OCC.Core.BRep import BRep_Builder
    from OCC.Core.TopoDS import TopoDS_Compound
except ImportError:
    pass


def build_pile_cap(
    *,
    length=2200.0,
    width=1200.0,
    depth=600.0,
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
    Builds a parametric rectangular prism concrete pile cap with internal rebar mats.

    Dimensions:
        - length: along X-axis (span direction)
        - width: along Y-axis (transverse direction)
        - depth: along Z-axis (downwards from top_z)
    """
    bot_z = top_z - depth
    x_min = center_x - length / 2.0
    y_min = center_y - width / 2.0

    # 1. Concrete rectangular solid
    p1 = gp_Pnt(x_min, y_min, bot_z)
    concrete_solid = BRepPrimAPI_MakeBox(p1, length, width, depth).Shape()

    # 2. Reinforcement Mats (Bottom & Top)
    rebar_shapes = []
    r_main = rebar_main_diameter / 2.0

    x_bar_min = x_min + rebar_cover
    x_bar_len = max(100.0, length - 2.0 * rebar_cover)

    y_bar_min = y_min + rebar_cover
    y_bar_len = max(100.0, width - 2.0 * rebar_cover)

    # Number of bars
    n_x = max(2, int(round(y_bar_len / rebar_spacing_longitudinal)) + 1)
    dy_x = y_bar_len / (n_x - 1)

    n_y = max(2, int(round(x_bar_len / rebar_spacing_longitudinal)) + 1)
    dx_y = x_bar_len / (n_y - 1)

    # Bottom Mat
    z_bot_mat = bot_z + rebar_cover + r_main
    # Bars along X (bottom)
    for i in range(n_x):
        y_pos = y_bar_min + i * dy_x
        axis = gp_Ax2(gp_Pnt(x_bar_min, y_pos, z_bot_mat), gp_Dir(1, 0, 0))
        rebar_shapes.append(BRepPrimAPI_MakeCylinder(axis, r_main, x_bar_len).Shape())

    # Bars along Y (bottom, layer 2)
    for j in range(n_y):
        x_pos = x_bar_min + j * dx_y
        axis = gp_Ax2(gp_Pnt(x_pos, y_bar_min, z_bot_mat + 2.0 * r_main), gp_Dir(0, 1, 0))
        rebar_shapes.append(BRepPrimAPI_MakeCylinder(axis, r_main, y_bar_len).Shape())

    # Top Mat
    z_top_mat = top_z - rebar_cover - r_main
    for i in range(n_x):
        y_pos = y_bar_min + i * dy_x
        axis = gp_Ax2(gp_Pnt(x_bar_min, y_pos, z_top_mat), gp_Dir(1, 0, 0))
        rebar_shapes.append(BRepPrimAPI_MakeCylinder(axis, r_main, x_bar_len).Shape())

    for j in range(n_y):
        x_pos = x_bar_min + j * dx_y
        axis = gp_Ax2(gp_Pnt(x_pos, y_bar_min, z_top_mat - 2.0 * r_main), gp_Dir(0, 1, 0))
        rebar_shapes.append(BRepPrimAPI_MakeCylinder(axis, r_main, y_bar_len).Shape())

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
            "length": length,
            "width": width,
            "depth": depth,
            "center_x": center_x,
            "center_y": center_y,
            "top_z": top_z,
            "bot_z": bot_z
        }
    }
