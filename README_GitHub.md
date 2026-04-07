# Reconstructed analysis pipeline for "A Governance Framework for GeoAI in Public Health"

This repository package reconstructs the empirical workflow described in the manuscript.
It is intended for transparency and GitHub archiving.

## What the script does
1. Reads a Scopus CSV export.
2. Deduplicates records by DOI, EID, and title.
3. Filters a GeoAI core using title terms such as `geoai`, `geospatial`, `spatial`, and `gis`.
4. Identifies health-related and stricter public-health subsets using title keywords.
5. Applies transparent regex dictionaries for governance, validation, Intelligence, Processing, Design, Choice, urban, and rural signals.
6. Reconstructs Table 6-style descriptive percentages.
7. Runs chi-square tests for selected binary indicators.
8. Saves all outputs as CSV files.

## Files
- `analysis_pipeline.py` — main script
- `regex_patterns.json` — transparent dictionaries used by the script
- `requirements.txt` — Python dependencies

## Expected input
A Scopus CSV export with columns similar to:
- `Title`
- `Abstract`
- `Author Keywords` and/or `Index Keywords`
- `DOI`
- `EID`

## Run
```bash
python analysis_pipeline.py --input data/scopus_export.csv --out results
```

## Important note
This package is a reconstruction from the manuscript description. If you have the author's exact screening code or Appendix regex dictionaries, replace the current patterns with those final versions before public release.
