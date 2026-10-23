# Result-to-Claim Audit & Evidence Verification Report
**Status:** PASSED (All Claims Deterministically Verified)

## Executive Summary
All empirical claims in the paper roadmap were mechanically checked against the real solver execution logs. Zero synthetic or mock evidence was detected.

## Claim-by-Claim Verification Matrix

| Claim ID | Claim Statement | Target / Claimed | Actual in Data | Source File | Status | Verdict |
| :--- | :--- | :---: | :---: | :--- | :---: | :---: |
| `CLAIM_1_CEG_SUCCESS_RATE` | CEG-OMR achieves 100% repair success across multi-fault benchmark configurations. | 1.0 | 1.0 | `benchmark_outputs/statistical_analysis_report.json` | `verified` | **YES** |
| `CLAIM_2_CEG_PESR` | CEG-OMR recovers 100% Plan Execution Success Rate (PESR) after repair. | 1.0 | 1.0 | `benchmark_outputs/statistical_analysis_report.json` | `verified` | **YES** |
| `CLAIM_3_SAM_CONSERVATIVE_GAP` | Passive Safe Action Model (SAM, M=50) achieves only 65.22% PESR across multi-fault settings due to conservative over-constraining. | 0.6522 | 0.6522 | `benchmark_outputs/statistical_analysis_report.json` | `verified` | **YES** |
| `CLAIM_4_BIDIRECTIONAL_FAMILY_B_SOLVE_RATE` | CEG-OMR achieves 100% solve rate on Family B (spurious preconditions), where monotonic OLAM and SAM achieve 0%. | 100.0 | 100.0 | `benchmark_outputs/bidirectional_and_compound_repair_benchmark.json` | `verified` | **YES** |
| `CLAIM_5_BACKTRACKING_NECESSITY_LOGISTICS` | Disabling backtracking collapses repair success in Logistics from 100% to 0%. | 0.0 | 0 | `benchmark_outputs/ablation_study_results.json` | `verified` | **YES** |
