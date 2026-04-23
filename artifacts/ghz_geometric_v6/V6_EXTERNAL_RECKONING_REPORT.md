# V6 External Reckoning

## What was done
- Extracted count dictionaries from IBM GHZ notebook outputs.
- Built strict shot file (`ZZZ`) and proxy shot file (`XXX`) for connector compatibility.
- Ran v5 closure with proxy external shots.

## Important caveat
- The source notebook is computational-basis GHZ benchmarking; it does not directly provide the full GHZ Mermin context set (`XXX`,`XYY`,`YXY`,`YYX`).
- Therefore strict mode cannot close full Mermin F; proxy mode is a transport/integration check only.

## Actual extraction outcome
- No 3-qubit context table was embedded; extractor found 5-qubit counts and projected first 3 bits as a transparent fallback.
- Extracted 5-qubit snapshot has `p(00000)=0.406`, `p(11111)=0.417`, total shots `2000`.
- Strict connector result (`ZZZ`) => all GHZ-audit contexts absent (`n_total_audit_contexts=0`), so `F=0, R=0`.
- Proxy connector result (`XXX`) => only `E(XXX)=-0.049` available; `XYY/YXY/YYX` missing, thus no valid full Mermin closure.
- Conclusion: v6 successfully closed the **data pipeline**, but did not close the **physics audit** for Mermin GHZ because external notebook lacks required context-resolved measurements.

## Files
- `IBM_GHZ_COUNT_CANDIDATES.json`
- `IBM_GHZ_EXTRACTION_SUMMARY.json`
- `IBM_GHZ_REAL_DATA_STRICT.json`
- `IBM_GHZ_REAL_DATA_PROXY_XXX.json`
- `V6_EXTERNAL_RECKONING_RESULTS.json`