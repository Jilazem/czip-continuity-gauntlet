# Czip Continuity Gauntlet — Run Report

*Public copy: local endpoint redacted; original results.json SHA-256 `817be24db98e570f0ab9958f901dea588c3c1e541e79df02271991a4996e8fef`.*

- Dataset SHA-256: `4d4081624c8ecdf1c9789b5714107c8839eb6f7e43ea5f7db3c72c69493197cb`
- Czip engine SHA-256: `a219624cc2e1b24af3d194c5bc7994ba4a226f7bf0e18eb87bb5feb99799347e`
- Model: `GLM-5.3-Flash-EXL3`
- Endpoint: `local endpoint (redacted)`
- Generated: `2026-09-30T04:57:48.267682+00:00`

| Arm | Completed | Correct / total | Grounded / total | Prompt tokens incl. setup | Input chars incl. setup | Median latency (s) |
|---|---:|---:|---:|---:|---:|---:|
| czip | 8/8 | 6/8 | 0/8 | 32790 | 118632 | 2.088 |
| summary | 0/8 | 0/8 | 0/8 | unavailable | 0 | None |
| tail | 8/8 | 1/8 | 1/8 | 15640 | 72360 | 1.074 |

Rolling summary preparation: failed: model returned no assistant content

Czip full-pack preparation: 13120 bytes on disk, 0.091 seconds. This is outside model prompt tokens.


## Per-question results

| Arm | Probe | Category | Answer | Expected | Correct | Grounded | Calls |
|---|---|---|---|---|---|---|---:|
| czip | early_exact | early_exact | RB-QWHKS8W4 | RB-QWHKS8W4 | yes | no | 1 |
| czip | two_hop | two_hop | ESC-5FTCNL43 | ESC-5FTCNL43 | yes | no | 3 |
| czip | tool_evidence | tool_evidence | SHA-BY9Q5UAB | SHA-BY9Q5UAB | yes | no | 1 |
| czip | superseded_region | update | ap-southeast-2 (superseding the earlier eu-west-1 draft) | ap-southeast-2 | no | no | 1 |
| czip | revoked_fallback | revocation | NO | NO | yes | no | 1 |
| czip | reopened_issue | temporal | OPEN | OPEN | yes | no | 1 |
| czip | approval_boundary | instruction | USER | USER | yes | no | 1 |
| czip | unknown_pin | abstention | UNKNOWN — the transcript never states the ORION release approval PIN. It only records (index 493) that the approval must be entered by the user on their own phone and that the assistant may never enter the PIN. | UNKNOWN | no | no | 2 |
| summary | early_exact | error | — | — | no | no | 0 |
| summary | two_hop | error | — | — | no | no | 0 |
| summary | tool_evidence | error | — | — | no | no | 0 |
| summary | superseded_region | error | — | — | no | no | 0 |
| summary | revoked_fallback | error | — | — | no | no | 0 |
| summary | reopened_issue | error | — | — | no | no | 0 |
| summary | approval_boundary | error | — | — | no | no | 0 |
| summary | unknown_pin | error | — | — | no | no | 0 |
| tail | early_exact | early_exact | UNKNOWN | RB-QWHKS8W4 | no | no | 0 |
| tail | two_hop | two_hop | UNKNOWN | ESC-5FTCNL43 | no | no | 0 |
| tail | tool_evidence | tool_evidence | UNKNOWN | SHA-BY9Q5UAB | no | no | 0 |
| tail | superseded_region | update | UNKNOWN | ap-southeast-2 | no | no | 0 |
| tail | revoked_fallback | revocation | UNKNOWN | NO | no | no | 0 |
| tail | reopened_issue | temporal | UNKNOWN | OPEN | no | no | 0 |
| tail | approval_boundary | instruction | UNKNOWN | USER | no | no | 0 |
| tail | unknown_pin | abstention | UNKNOWN | UNKNOWN | yes | yes | 0 |

## Interpretation

Grounded accuracy requires the exact short answer, every required source index, and proof that the cited source was exposed to the answering model. Missing or failed probes count against the total. Prompt tokens are reported only when the API supplies usage for every completed request.

This is a synthetic, single logical conversation replay with per-question API calls. It measures retrieval-assisted continuity; it does not prove an infinite native context window, or that a competing memory system cannot match the result.
