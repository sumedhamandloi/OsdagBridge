# OsdagBridge: Substructure CAD & IFC Integration

OsdagBridge is a modular, shared-core software plugin for the analysis, design, and 3D CAD/BIM modeling of steel bridges within the Osdag ecosystem (FOSSEE / IIT Bombay).

---

## Screening Assignment Implementation Overview

This repository includes the complete implementation of the screening assignment:
**"Parametric 3D CAD Modeling of Bridge Substructure and IFC Workflow Integration"**.

### What Was Implemented:
1. **Parametric 3D CAD Modeling of Substructure Components (`pythonOCC` / OpenCASCADE)**:
   - **Piers (Circular Columns)**: Parametric vertical concrete cylinder (`diameter = 800 mm`, `height = 3000 mm`) with circular rebar cage.
   - **Pier Cap (Hammerhead / Trapezoidal)**: Cantilever hammerhead pier cap (`top_width = 3000 mm`, `bottom_width = 1200 mm`, `depth = 600 mm`, `length = 1200 mm`) with top/bottom longitudinal mats and transverse stirrups.
   - **Pile Cap (Rectangular Prism)**: Solid footing (`length = 2200 mm`, `width = 1200 mm`, `depth = 600 mm`) with orthogonal top and bottom reinforcement grids.
   - **Piles (Circular Piles in 2×2 Grid)**: 4 circular foundation piles (`diameter = 400 mm`, `length = 5000 mm`, `spacing = 600 mm` center-to-center) with internal rebar cages and spiral ties.
   - **Reinforcement (Internal Steel Solids)**: Complete cylindrical & hoop steel reinforcement (`rebar_main_diameter = 16 mm`, `rebar_spacing_longitudinal = 150 mm`, `rebar_transverse_diameter = 8 mm`, `rebar_spacing_transverse = 200 mm`, `rebar_cover = 40 mm`). All rebars remain strictly enclosed within their respective concrete volumes.

2. **Strict Coordinate System Consistency**:
   - **X-axis**: Longitudinal bridge span direction.
   - **Y-axis**: Transverse deck width direction (centered at $Y = 0$).
   - **Z-axis**: Vertical elevation.
   - Origin: Center of span at deck level ($Z = 0$ reference top, bottom flange at $Z_{\text{contact}} = -D/2 - T_{fb}$).
   - Substructure is placed flush under the girder supports at $X = 0$, with pier cap top matching girder bottom level, column extending downward, pile cap below column, and piles extending into the foundation.

3. **GUI Visualization & Transparency (`PySide6` + `cad_3d.py`)**:
   - **Concrete Solids**: Semi-transparent concrete rendering (`transparency = 0.35` / `opacity = 0.65`) using OCCT `DisplayShape` API.
   - **Reinforcement Solids**: Opaque metallic steel/rust color (`RGB: 180, 70, 40`), fully visible through the transparent concrete envelope.
   - **Component Toggles**: Updated `BridgeComponentCheckbox` with dedicated checkboxes: `Pier Cap`, `Pier`, `Pile Cap`, `Piles`, and `Reinforcement`.

4. **IFC4 BIM Export Pipeline Integration (`ifc_export_bridge/`)**:
   - Extended `PlateGirderIFCExtractor` to extract substructure items into unified metadata dictionary.
   - Enhanced `BridgeGeometryMapper` with `create_circle_profile(radius)` for circular extrusions.
   - Updated `BridgeIfcGenerator` to generate native IFC4 building elements:
     - Pier Cap &rarr; `IfcBeam` (Cap Beam)
     - Pier &rarr; `IfcColumn`
     - Pile Cap &rarr; `IfcFooting`
     - Piles &rarr; `IfcPile` (4 Bored Piles)
     - Reinforcement &rarr; `IfcReinforcingBar` (48 swept solid bars with diameter and length)
   - Exported models adhere strictly to IFC4 spatial structure for full import into Autodesk Revit and automated BOQ extraction.

---

## File Structure & Code Modifications

```
Osdag-Bridge/
├── src/osdagbridge/
│   ├── core/
│   │   ├── bridge_components/
│   │   │   ├── sub_structure/
│   │   │   │   ├── pier/
│   │   │   │   │   ├── builder.py            # [NEW] Pier cylindrical solid & circular rebar cage
│   │   │   │   │   └── __init__.py           # Exports build_pier
│   │   │   │   └── pier_cap/
│   │   │   │       ├── builder.py            # [NEW] Hammerhead trapezoidal solid & rebar mats
│   │   │   │       └── __init__.py           # Exports build_pier_cap
│   │   │   └── foundation/
│   │   │       ├── pile/
│   │   │       │   ├── builder.py            # [NEW] 2x2 circular piles & rebar cages
│   │   │       │   └── __init__.py           # Exports build_piles
│   │   │       └── pile_cap/
│   │   │           ├── builder.py            # [NEW] Rectangular pile cap & dual rebar mats
│   │   │           └── __init__.py           # Exports build_pile_cap
│   │   ├── bridge_types/plate_girder/
│   │   │   └── cad_generator.py              # [UPDATED] Substructure assembly & return dictionary
│   │   └── ifc_export_bridge/
│   │       ├── bridge_geometry_mapper.py     # [UPDATED] Added circular profile mapper
│   │       ├── bridge_cad_extraction.py      # [UPDATED] Added _extract_substructure()
│   │       └── bridge_ifc_generator.py       # [UPDATED] Mapped IfcBeam, IfcColumn, IfcFooting, IfcPile, IfcReinforcingBar
│   └── desktop/ui/
│       └── cad_3d.py                         # [UPDATED] Semi-transparent display (0.35) & checkbox toggles
├── tests/
│   └── test_substructure_and_ifc.py          # [NEW] Automated OCC shape & IFC verification tests
├── tools/
│   ├── test_ifc_export.py                    # [NEW] Headless IFC4 generation & entity audit test
│   ├── generate_report.py                    # [NEW] PDF technical report compiler
│   └── package_submission.py                 # [NEW] Clean ZIP submission builder
├── output/
│   └── OsdagBridge_Substructure_Complete.ifc # [GENERATED] Valid IFC4 export containing full bridge
└── OsdagBridge_Substructure_Technical_Report.pdf # [GENERATED] Technical submission report
```

---

## How to Run & Verify

### 1. Conda Environment Setup
Ensure the required conda environment is activated:
```powershell
conda activate osdagbridge-env
```

### 2. Run Automated Verification Tests
Run the complete test suite verifying both OpenCASCADE 3D solids and IFC4 generation:
```powershell
python tests/test_substructure_and_ifc.py
```
Expected output:
```
[PASS] test_pier_cap_builder
[PASS] test_pier_builder
[PASS] test_pile_cap_builder
[PASS] test_piles_builder
[PASS] test_cad_generator_substructure_integration
[PASS] test_ifc_export_integration
ALL VERIFICATION TESTS PASSED SUCCESSFULLY!
```

### 3. Run Headless IFC Audit
Generate and inspect the exported IFC model:
```powershell
python tools/test_ifc_export.py
```

### 4. Launch the Desktop Application GUI
Open the 3D interactive viewer to visually inspect the transparent concrete and rebar:
```powershell
python -m osdagbridge.desktop
```
In the GUI:
1. Generate the 3D CAD model.
2. Observe the semi-transparent Pier Cap, Pier, Pile Cap, and Piles with internal reinforcement visible.
3. Use the bottom component selector checkboxes to toggle individual components.
4. Export to IFC via **File &rarr; Save 3D CAD Model &rarr; Save as type: .ifc**.

---

## Known Limitations & Design Notes

1. **Rebar Representation in IFC**: Rebars are exported as swept solids (`IfcReinforcingBar`) with their true diameter, centroid path, and length. In very dense meshes, thousands of individual ties can increase IFC file size; grouping and selective representative spacing is used to maintain high performance in CAD/BIM tools.
2. **Multi-Span Configurations**: Currently, the single-span default generates substructure supports at $X = 0$. The builders are parameterized to accept any `(center_x, center_y, top_z)` coordinate for continuous multi-span expansion.
