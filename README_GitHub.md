# GeoAI Public Health Screening Code

This repository contains the screening code, regex dictionaries, and extraction logic used to reconstruct the corpus-based analytical workflow for the manuscript:

**“A Governance Framework for GeoAI in Public Health”**

The repository is designed to support transparency and reproducibility for the literature screening and descriptive corpus mapping procedures reported in the manuscript.

## Contents

- `geoai_screening_notebook_ready.ipynb` — main Jupyter Notebook with the full workflow
- `regex_patterns.json` — regex dictionaries used for screening and dictionary-based coding
- `requirements.txt` — minimal Python dependencies
- `Data/` — folder for the input Scopus CSV export
- `output/` — generated output tables

## What the notebook does

The notebook reconstructs the following steps:

1. Load a Scopus CSV export.
2. Detect relevant metadata fields (`Title`, `Abstract`, `Keywords`, `DOI`, `EID`).
3. Deduplicate records using DOI, EID, and title fields.
4. Identify a GeoAI-related corpus using title-based filtering.
5. Identify health-related and stricter public-health subsets using transparent keyword rules.
6. Identify a governance-relevant subset using governance-related regex patterns.
7. Apply dictionary-based coding for:
   - governance
   - validation
   - intelligence
   - processing
   - design
   - choice
   - urban
   - rural
8. Export reconstructed summary tables as `.csv` files.

## Input data

Place the Scopus export file in the `Data/` folder.

Expected file path:

```text
Data/scopus_export_GEO AI.csv
```

If your file has a different name or location, edit the `INPUT_CSV` variable in the notebook.

## Output files

The notebook writes results to:

```text
output/repo_results/
```

This includes:

- `prisma_counts_reconstructed.csv`
- `table6_reconstructed.csv`
- `chi_square_results.csv`
- `deduplicated_corpus.csv`
- `geoai_core.csv`
- `health_related_subset.csv`
- `public_health_subset.csv`
- `governance_core_subset.csv`

## Requirements

Install the required Python packages before running the notebook:

```bash
pip install -r requirements.txt
```

Minimal dependencies:

- pandas
- scipy

## How to run

1. Clone or download this repository.
2. Place the Scopus CSV export into the `Data/` folder.
3. Open `geoai_screening_notebook_ready.ipynb` in Jupyter Notebook or JupyterLab.
4. Run the notebook from top to bottom.

## Important note

This repository contains a **reconstructed analytical workflow** based on the manuscript methods section. It is intended to provide transparent screening logic and reproducible corpus-processing steps.

If the final published version of the manuscript uses revised regex dictionaries, updated inclusion rules, or corrected record counts, the repository should be updated accordingly.

## Reproducibility statement

The notebook is provided to make the screening logic, regex dictionaries, and descriptive corpus mapping workflow inspectable and reusable. It is not presented as a validated software package, but as a transparent research companion for the manuscript.

## Citation

If you use or adapt this notebook, please cite the associated manuscript.

## Author

Nikolai A. Grudtsyn  
St. Petersburg University
