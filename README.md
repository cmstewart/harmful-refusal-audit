# IRT-based contamination detection

This project aims to detect benchmark contamination in large language models by treating it as item preknowledge, a concept borrowed from psychometric test security. Under the proposed hypothesis, a model is a suspect on an item when it succeeds far beyond what its latent ability predicts. This repository holds the screening stage that surfaces suspects on [GSM8K](https://huggingface.co/datasets/openai/gsm8k) using item response theory (IRT), a reproduction stage that validates the inference harness, and a perturbation stage that confirms suspects.

## Idea

Contamination is a property of a model-item pair, not of an item alone, in the same way that a student having seen an exam question is a property of that student and that question. The method runs in three stages.

- Screen. We fit a 2PL IRT model to a large model-by-item response matrix, then compute the standardized residual for each cell. A large positive residual is a success the item difficulty cannot explain. This is a cheap correlational filter that surfaces suspects.
- Reproduce. We confirm that a local inference harness reproduces the stored benchmark scores before trusting any perturbation result. The check runs in both directions, on items a model passed and items it failed.
- Identify. We perturb a flagged item into a twin that keeps the arithmetic and changes the surface numbers, then re-run the suspect models. A model that passes the original and fails the twin memorized the item. A model that passes both has the underlying skill.

The screen on its own cannot separate genuine narrow skill from exposure, so no flagged item is a finding until perturbation confirms it.

## Repository layout

The repository is organized by the three stages. The README and the .gitignore sit at the root.

Screening holds the residual screen and its outputs.
- Screening/gsm8k_2pl_irt.ipynb. Builds the response matrix, checks unidimensionality, fits the 2PL, and runs the residual screen.
- Screening/gsm8k_matrix_filtered.parquet. The filtered binary response matrix, 6,014 models by 1,214 items.
- Screening/gsm8k_2pl_item_params.csv. Item difficulty and discrimination from the 2PL fit.
- Screening/gsm8k_2pl_abilities.csv. Estimated latent ability for each model.
- Screening/gsm8k_preknowledge_screen.csv. The one-sided preknowledge score per model.
- Screening/gsm8k_flagged_cells.csv. The flagged model-item cells from the screen.
- Screening/gsm8k_flagged_with_gold.csv. The recurring flagged items with question text and gold worked answers.

Reproduction holds the harness validation.
- Reproduction/gsm8k_reproduction_check.ipynb. Re-runs small flagged models on original items and compares against the stored matrix. Includes saved outputs.
- Reproduction/gsm8k_reproduction_results.csv. The per-run agreement results.

Perturbation holds the twin generation, the flip test, and the cloud execution path.
- Perturbation/gsm8k_twins_flip_test.ipynb. Generates numeric twins and runs the flip test.
- Perturbation/cloud/flip_runner.py. The batch runner that executed the flip test on a disposable VM.
- Perturbation/cloud/startup.sh. The VM startup script that installs, runs the runner, and uploads results.
- Perturbation/results/preliminary_flip_results.md. The full flip-test writeup, the control comparison, the twin validity audit, and the refuted case study.
- Perturbation/results/gsm8k_flip_all.csv. The per-pair flip results from the full sweep.
- Perturbation/results/gsm8k_twins.csv. The generated twins, retained here as the record of what was run.
- Perturbation/cloud/. The execution machinery. preflight.py resolves true model sizes from weight metadata, flip_task.py runs one model per task, and the Dockerfile and batch scripts drive GCP Batch.
- Control/. The matched control condition. build_control_plan.py selects difficulty-matched unflagged items per model, build_control_gold.py recovers their GSM8K solutions, and audit_twins.py checks which items can support a valid twin at all.

## Data

Response data comes from metabench (Kipnis et al.), which assembled item-wise correctness for the Open LLM Leaderboard v1 benchmarks across more than five thousand models. The GSM8K slice is used here. To reproduce the analysis, download data.tar.gz from the metabench Zenodo record 12819251 and extract it to benchmark-data. Question text and gold worked answers come from the GSM8K dataset on Hugging Face. These sources are not redistributed here.

## Results so far

- GSM8K survives as a near-unidimensional construct on this pool. The variance filter retains 1,214 of 1,319 items, and the item correlation scree gives a first-to-second eigenvalue ratio of about 11.9.
- The 2PL fit is well behaved, with a median discrimination of 1.83 and item parameters that reproduce observed item difficulty at a correlation of 0.999.
- The screen flags 848 model-item cells across 424 models and 63 distinct items, 57 of which are flagged by three or more models.
- The reproduction check passed at 100 percent agreement on 18 runs across two models, in both directions.
- The perturbation stage completed its full sweep. Flagged cells fail a number-changed twin 85.1 percent of the time, 86 of 101 pairs. This figure alone means nothing, because models degrade broadly when numbers change whether or not they saw the item.
- The matched control is the result. For each flagged cell we tested a different item the same model passed and was never flagged on, matched on 2PL difficulty. Control cells fail 56.1 percent of the time, 60 of 107 pairs. The gap is 29.0 points with an odds ratio of 4.49 and a p of 0.000005. A flagged cell has about four and a half times the odds of breaking under perturbation.
- Roughly 16 percent of GSM8K items cannot support a valid numeric twin, because the annotated solution trace does not reach the stated answer. Invalid twins score correct answers as failures and manufacture apparent memorization. Auditing them widened the gap, since they had been inflating the control rate rather than the treatment rate.
- A candidate single-item case study did not survive. Four models appeared to recite a stored answer to a changed question, but eight further twins showed that answer was reachable from the new numbers by a common omission error. There is no clean demonstration of retrieval in this data. See Perturbation/results for the full account.

## Running it

Each notebook reads its inputs by filename and resolves them across the stage folders. The screening notebook needs the metabench data extracted to benchmark-data and py-irt, which requires Python 3.9 to 3.11. The reproduction and perturbation notebooks additionally need torch, transformers, and accelerate, and they want a GPU. The flip test was executed at scale through the cloud scripts in Perturbation/cloud rather than in the notebook.

## Status

All three stages are complete and the main comparison is in place. The screen is best understood as a ranking instrument rather than a classifier. A companion simulation with planted ground-truth contamination puts its precision near 0.19, and independently predicts the empirical lift we measured, 1.54 against our 1.52.

Two directions remain. Anchoring ability and difficulty on secure items would address the circularity in the screen, and the simulation shows why it matters, since screen recall falls from 0.179 to 0.061 as contamination density rises and the fitted item parameters absorb the anomalous successes. Separately, fine-tuning a base model on known items would create ground-truth contamination in real text rather than in a response-process simulation, which would give sensitivity and specificity instead of an odds ratio against a proxy baseline.
