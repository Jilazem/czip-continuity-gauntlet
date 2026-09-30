# Czip Continuity Gauntlet — Run Report

*Public copy: local endpoint redacted; original results.json SHA-256 `510b59a4a51d59863609feaa7ae3220569ca81a767babb9cf3a903310448f559`.*

- Dataset SHA-256: `cb9c60a876803e6fc07831afeba0014aad18c7605381961b8fb61c5f008fe97d`
- Czip engine SHA-256: `not used`
- Model: `GLM-5.3-Flash-EXL3`
- Endpoint: `local endpoint (redacted)`
- Generated: `2026-09-30T05:11:37.974506+00:00`

| Arm | Completed | Correct / total | Grounded / total | Prompt tokens incl. setup | Input chars incl. setup | Median latency (s) |
|---|---:|---:|---:|---:|---:|---:|
| full | 8/8 | 8/8 | 8/8 | 369536 | 1736400 | 0.917 |

## Per-question results

| Arm | Probe | Category | Answer | Expected | Correct | Grounded | Calls |
|---|---|---|---|---|---|---|---:|
| full | early_exact | early_exact | RB-QWHKS8W4 | RB-QWHKS8W4 | yes | yes | 0 |
| full | two_hop | two_hop | ESC-5FTCNL43 | ESC-5FTCNL43 | yes | yes | 0 |
| full | tool_evidence | tool_evidence | SHA-BY9Q5UAB | SHA-BY9Q5UAB | yes | yes | 0 |
| full | superseded_region | update | ap-southeast-2 | ap-southeast-2 | yes | yes | 0 |
| full | revoked_fallback | revocation | NO | NO | yes | yes | 0 |
| full | reopened_issue | temporal | OPEN | OPEN | yes | yes | 0 |
| full | approval_boundary | instruction | USER | USER | yes | yes | 0 |
| full | unknown_pin | abstention | UNKNOWN | UNKNOWN | yes | yes | 0 |

## Interpretation

Grounded accuracy requires the exact short answer, every required source index, and proof that the cited source was exposed to the answering model. Missing or failed probes count against the total. Prompt tokens are reported only when the API supplies usage for every completed request.

This is a synthetic, single logical conversation replay with per-question API calls. It measures retrieval-assisted continuity; it does not prove an infinite native context window, or that a competing memory system cannot match the result.
