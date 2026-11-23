"""
Comprehensive Verification Tests for Bridge Substructure CAD & IFC Integration
Tests:
1. Substructure component builders (Pier Cap, Pier, Pile Cap, Piles, Rebar)
2. Parametric dimensions and OCC TopoDS_Shape validity
3. Full integration into PlateGirderCADGenerator
4. IFC extraction and IFC4 generation with proper entities:
   - IfcBeam (Pier Cap)
   - IfcColumn (Pier)
   - IfcFooting (Pile Cap)
   - IfcPile (Piles)
   - IfcReinforcingBar (Rebar)
"""

import sys
import os
from pathlib import Path

# Ensure src and repo root are on sys.path
REPO_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_DIR / "src"
if str(REPO_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

def test_pier_cap_builder():
    from osdagbridge.core.bridge_components.sub_structure.pier_cap.builder import build_pier_cap
    res = build_pier_cap(
        top_width=3000.0,
        bottom_width=1200.0,
        depth=600.0,
        length=1200.0,
        center_x=0.0,
        center_y=0.0,
        top_z=-1000.0
    )
    assert res["concrete"] is not None
    assert not res["concrete"].IsNull()
    assert res["rebar_compound"] is not None
    assert len(res["rebar"]) > 0
    print("[PASS] test_pier_cap_builder")

def test_pier_builder():
    from osdagbridge.core.bridge_components.sub_structure.pier.builder import build_pier
    res = build_pier(
        diameter=800.0,
        height=3000.0,
        center_x=0.0,
        center_y=0.0,
        top_z=-1600.0
    )
    assert res["concrete"] is not None
    assert not res["concrete"].IsNull()
    assert res["rebar_compound"] is not None
    assert len(res["rebar"]) >= 8
    print("[PASS] test_pier_builder")

def test_pile_cap_builder():
    from osdagbridge.core.bridge_components.foundation.pile_cap.builder import build_pile_cap
    res = build_pile_cap(
        length=2200.0,
        width=1200.0,
        depth=600.0,
        center_x=0.0,
        center_y=0.0,
        top_z=-4600.0
    )
    assert res["concrete"] is not None
    assert not res["concrete"].IsNull()
    assert res["rebar_compound"] is not None
    assert len(res["rebar"]) > 0
    print("[PASS] test_pile_cap_builder")

def test_piles_builder():
    from osdagbridge.core.bridge_components.foundation.pile.builder import build_piles
    res = build_piles(
        n_piles_per_cap=4,
        pile_diameter=400.0,
        pile_length=5000.0,
        pile_spacing=600.0,
        center_x=0.0,
        center_y=0.0,
        top_z=-5200.0
    )
    assert len(res["concrete"]) == 4
    for c in res["concrete"]:
        assert not c.IsNull()
    assert res["concrete_compound"] is not None
    assert res["rebar_compound"] is not None
    assert len(res["rebar"]) > 0
    print("[PASS] test_piles_builder")

def test_cad_generator_substructure_integration():
    from osdagbridge.core.bridge_types.plate_girder.cad_generator import PlateGirderCADGenerator
    from tools.test_ifc_export import get_sample_bridge_params

    gen = PlateGirderCADGenerator()
    params = get_sample_bridge_params()
    model = gen.generate(params)

    assert "pier_cap" in model and model["pier_cap"]
    assert "pier" in model and model["pier"]
    assert "pile_cap" in model and model["pile_cap"]
    assert "piles" in model and model["piles"]
    assert "substructure_rebar" in model and model["substructure_rebar"]
    print("[PASS] test_cad_generator_substructure_integration")

def test_ifc_export_integration(tmp_path=None):
    import tempfile
    import ifcopenshell
    from osdagbridge.core.bridge_types.plate_girder.cad_generator import PlateGirderCADGenerator
    from osdagbridge.core.ifc_export_bridge.bridge_cad_extraction import PlateGirderIFCExtractor
    from osdagbridge.core.ifc_export_bridge.bridge_ifc_generator import BridgeIfcGenerator
    from tools.test_ifc_export import get_sample_bridge_params

    gen = PlateGirderCADGenerator()
    params = get_sample_bridge_params()
    gen._set_parameters(params)

    extractor = PlateGirderIFCExtractor(gen)
    extracted = extractor.extract()

    assert "substructure" in extracted
    assert len(extracted["substructure"]) > 0

    classes = [item._class_name for item in extracted["substructure"]]
    assert "SubstructurePierCap" in classes
    assert "SubstructurePier" in classes
    assert "SubstructurePileCap" in classes
    assert "SubstructurePile" in classes
    assert "SubstructureRebar" in classes

    output_path = tmp_path / "test_bridge_substructure.ifc" if tmp_path else Path(tempfile.gettempdir()) / "test_bridge_substructure.ifc"
    
    ifc_gen = BridgeIfcGenerator(str(output_path))
    ifc_gen.generate_from_extracted_data(extracted, gen)

    assert output_path.exists()
    assert output_path.stat().st_size > 0

    # Parse and verify entities inside the generated IFC
    ifc_file = ifcopenshell.open(str(output_path))
    beams = ifc_file.by_type("IfcBeam")
    columns = ifc_file.by_type("IfcColumn")
    footings = ifc_file.by_type("IfcFooting")
    piles = ifc_file.by_type("IfcPile")
    rebars = ifc_file.by_type("IfcReinforcingBar")

    assert len(beams) >= 1, "Pier Cap should be exported as IfcBeam"
    assert len(columns) >= 1, "Pier should be exported as IfcColumn"
    assert len(footings) >= 1, "Pile Cap should be exported as IfcFooting"
    assert len(piles) == 4, f"Expected 4 Piles, got {len(piles)}"
    assert len(rebars) > 0, f"Expected reinforcing bars, got {len(rebars)}"

    print(f"[PASS] test_ifc_export_integration (Exported to {output_path})")
    print(f"       Exported: {len(beams)} Beams, {len(columns)} Columns, {len(footings)} Footings, {len(piles)} Piles, {len(rebars)} Rebars")

if __name__ == "__main__":
    test_pier_cap_builder()
    test_pier_builder()
    test_pile_cap_builder()
    test_piles_builder()
    test_cad_generator_substructure_integration()
    test_ifc_export_integration()
    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
