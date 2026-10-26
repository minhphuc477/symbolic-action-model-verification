# Symbolic Action Model Repair — Thesis Codebase

**Status: rebuild in progress.** The previous codebase is preserved under git tag `legacy-v1`
(branch `legacy`). Its reported numbers are **not** carried over: they must be reproduced by the
new code under the new experimental protocol before being cited anywhere.

Reasons for the rebuild (verified by reading the legacy code):

1. The legacy oracle returned the full ground-truth state on failure, while the text claimed
   binary feedback only.
2. The partial-observability experiment produced identical results at every observability level
   (1 problem, 1 seed), so it did not test what it claimed.
3. The ablation study showed no difference between the full method and its ablations.
4. Most "100 %" results came from a single problem per domain with hand-picked faults.
5. The random-probing baseline read the ground-truth domain to enumerate applicable actions.

See `RESEARCH_RULES.md` for the integrity rules the new code follows.
