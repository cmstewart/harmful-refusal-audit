# Revised Notebook Submission Archive

This folder contains the revised notebook for the manuscript
`Searching for Harmful Refusal: A Psychometric Audit of an AI Safety Benchmark`.

## Contents

- `Harmful Refusal Construct Validity.ipynb`: manuscript-aligned notebook.
- `figures/`: standalone copy of the manuscript figure used in the notebook.
- `results/`: small CSV files backing the manuscript result tables.
- `requirements.txt`: Python packages used by the notebook and analysis.

The parallel-analysis figure is also embedded directly in the notebook, so the
notebook should render without relying on a local image path.

## Reproducibility

The setup cells download HELM Safety `v1.17.0` data from Stanford CRFM's public
storage bucket and rebuild the strict binary HarmBench response matrix. The
model-comparison, factor-correlation, and DIF result CSVs are included in
`results/` so the submitted archive contains the table artifacts used in the
manuscript.

Large downloaded HELM run files and fitted parameter caches are not included in
this archive because they are bulky and regenerable.

## Suggested Run Steps

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

Open `Harmful Refusal Construct Validity.ipynb`.
