# FOSSEE IIT Bombay Screening Assignment Submission

**Candidate:** Sumedha Mandloi  
**Project:** Parametric 3D CAD Modeling of Bridge Substructure and IFC Workflow Integration  
**Repository:** [github.com/sumedhamandloi/OsdagBridge](https://github.com/sumedhamandloi/OsdagBridge/tree/dev)  
**Google Document Report:** [https://docs.google.com/document/d/17vBZN5IohWHVWvcs1RoEHBPne3BkyIvVWuaAx2ROdVE/edit](https://docs.google.com/document/d/17vBZN5IohWHVWvcs1RoEHBPne3BkyIvVWuaAx2ROdVE/edit)  

---

## Folder Organization

- **`01_BIM_and_IFC_Models/`**:
  - `OsdagBridge_Substructure_Complete.ifc`: Validated IFC4 BIM model with all 5 substructure components and 48 reinforcement entities.
  - `README_IFC_MODELS.txt`: Schema and coordinate hierarchy specifications.

- **`02_Technical_Reports/`**:
  - `FOSSEE_Technical_Report_GoogleDocs.pdf`: Exported directly from the live Google Document.
  - `FOSSEE_Technical_Report_GoogleDocs.docx`: Editable Word document.
  - `FOSSEE_Technical_Report.md`: 10-chapter academic Markdown source.
  - `GOOGLE_DOC_REPORT_LINK.url`: Desktop one-click shortcut to the live Google Doc.

- **`03_Substructure_Source_Code/`**:
  - Numbered, standalone copies of all 10 core substructure builder, CAD assembly, GUI rendering, and IFC modules for convenient grading.

- **`04_Verification_and_Tests/`**:
  - `test_substructure_and_ifc.py`: Integration test suite.
  - `test_execution_log.txt`: Recorded passing output across all test cases.

- **`05_Documentation_and_Instructions/`**:
  - Architecture overview, setup steps, and parameter documentation.

---

## Parametric Component Specifications

| Component | Parameter | Value |
|---|---|---:|
| Pier | Diameter | 800 mm |
| Pier | Height | 3000 mm |
| Pier Cap | Top Width | 3000 mm |
| Pier Cap | Bottom Width | 1200 mm |
| Pier Cap | Depth | 600 mm |
| Pile Cap | Length | 2200 mm |
| Pile Cap | Width | 1200 mm |
| Pile Cap | Depth | 600 mm |
| Piles | Count | 4 (2 x 2 matrix) |
| Piles | Diameter | 400 mm |
| Piles | Length | 5000 mm |
| Piles | Center Spacing | 600 mm |
| Rebar | Main Diameter | 16 mm |
| Rebar | Transverse Diameter | 8 mm |
| Rebar | Concrete Cover | 40 mm |
