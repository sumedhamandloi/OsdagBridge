"""
Pile Component Builder (Geometry & Reinforcement)
Parametric circular concrete piles arranged in a 2x2 grid with internal steel reinforcement cages.
"""

import math
try:
    from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeTorus
    from OCC.Core.BRep import BRep_Builder
    from OCC.Core.TopoDS import TopoDS_Compound
except ImportError:
    pass


def build_piles(
    *,
    n_piles_per_cap=4,
    pile_diameter=400.0,
    pile_length=5000.0,
    pile_spacing=600.0,
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
    Builds a 2x2 grid of circular concrete piles extending downwards from top_z.

    Grid offsets (center-to-center):
        dx = +/- pile_spacing / 2
        dy = +/- pile_spacing / 2
    """
    radius = pile_diameter / 2.0
    bot_z = top_z - pile_length

    # Determine pile center coordinates (2x2 grid)
    half_s = pile_spacing / 2.0
    pile_centers = [
        (center_x - half_s, center_y - half_s),
        (center_x + half_s, center_y - half_s),
        (center_x - half_s, center_y + half_s),
        (center_x + half_s, center_y + half_s),
    ]

    concrete_solids = []
    all_rebar_shapes = []

    r_main = rebar_main_diameter / 2.0
    r_trans = rebar_transverse_diameter / 2.0
    cage_radius = radius - rebar_cover - r_trans - r_main
    if cage_radius < 30.0:
        cage_radius = radius - rebar_cover

    # Circular bar layout
    perimeter = 2.0 * math.pi * cage_radius
    n_bars = max(6, int(round(perimeter / rebar_spacing_longitudinal)))
    angle_step = 2.0 * math.pi / n_bars

    bar_len = max(100.0, pile_length - 2.0 * rebar_cover)
    bar_bot_z = bot_z + rebar_cover

    n_hoops = max(2, int(bar_len / rebar_spacing_transverse) + 1)
    dz_hoop = bar_len / max(1, (n_hoops - 1))

    for px, py in pile_centers:
        # Concrete cylinder
        origin = gp_Pnt(px, py, bot_z)
        axis = gp_Ax2(origin, gp_Dir(0, 0, 1))
        cyl = BRepPrimAPI_MakeCylinder(axis, radius, pile_length).Shape()
        concrete_solids.append(cyl)

        # Longitudinal rebar
        for i in range(n_bars):
            ang = i * angle_step
            bx = px + cage_radius * math.cos(ang)
            by = py + cage_radius * math.sin(ang)
            bar_axis = gp_Ax2(gp_Pnt(bx, by, bar_bot_z), gp_Dir(0, 0, 1))
            all_rebar_shapes.append(BRepPrimAPI_MakeCylinder(bar_axis, r_main, bar_len).Shape())

        # Transverse hoops
        hoop_radius = radius - rebar_cover - r_trans
        if hoop_radius > r_trans:
            for k in range(n_hoops):
                hz = bar_bot_z + k * dz_hoop
                hoop_axis = gp_Ax2(gp_Pnt(px, py, hz), gp_Dir(0, 0, 1))
                all_rebar_shapes.append(BRepPrimAPI_MakeTorus(hoop_axis, hoop_radius, r_trans).Shape())

    # Compound concrete
    b = BRep_Builder()
    c_conc = TopoDS_Compound()
    b.MakeCompound(c_conc)
    for c_shp in concrete_solids:
        b.Add(c_conc, c_shp)

    # Compound reinforcement
    c_rebar = None
    if all_rebar_shapes:
        c_rebar = TopoDS_Compound()
        b.MakeCompound(c_rebar)
        for r_shp in all_rebar_shapes:
            b.Add(c_rebar, r_shp)

    return {
        "concrete": concrete_solids,
        "concrete_compound": c_conc,
        "rebar": all_rebar_shapes,
        "rebar_compound": c_rebar,
        "parameters": {
            "n_piles": n_piles_per_cap,
            "pile_diameter": pile_diameter,
            "pile_length": pile_length,
            "pile_spacing": pile_spacing,
            "pile_centers": pile_centers,
            "center_x": center_x,
            "center_y": center_y,
            "top_z": top_z,
            "bot_z": bot_z
        }
    }
