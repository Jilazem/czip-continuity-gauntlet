# Czip Continuity Gauntlet — Run Report

*Public copy: local endpoint redacted; original results.json SHA-256 `dfd552fcceb4409a2413e67b0ec7de25ae76bdbb559fd7f669871928a396236f`.*

- Dataset SHA-256: `cb9c60a876803e6fc07831afeba0014aad18c7605381961b8fb61c5f008fe97d`
- Czip engine SHA-256: `a219624cc2e1b24af3d194c5bc7994ba4a226f7bf0e18eb87bb5feb99799347e`
- Model: `GLM-5.3-Flash-EXL3`
- Endpoint: `local endpoint (redacted)`
- Generated: `2026-09-30T05:09:05.915292+00:00`

| Arm | Completed | Correct / total | Grounded / total | Prompt tokens incl. setup | Input chars incl. setup | Median latency (s) |
|---|---:|---:|---:|---:|---:|---:|
| czip | 8/8 | 8/8 | 8/8 | 71243 | 257555 | 3.837 |
| summary | 8/8 | 8/8 | 8/8 | 88171 | 347975 | 0.774 |
| tail | 8/8 | 1/8 | 1/8 | 15592 | 72360 | 0.635 |

Rolling summary preparation: 26 model calls, 344.957 seconds, 312095 input characters; prompt tokens: 77243.

Czip full-pack preparation: 13120 bytes on disk, 0.093 seconds. This is outside model prompt tokens.


## Per-question results

| Arm | Probe | Category | Answer | Expected | Correct | Grounded | Calls |
|---|---|---|---|---|---|---|---:|
| czip | early_exact | early_exact | RB-QWHKS8W4 | RB-QWHKS8W4 | yes | yes | 2 |
| czip | two_hop | two_hop | ESC-5FTCNL43 | ESC-5FTCNL43 | yes | yes | 5 |
| czip | tool_evidence | tool_evidence | SHA-BY9Q5UAB | SHA-BY9Q5UAB | yes | yes | 2 |
| czip | superseded_region | update | ap-southeast-2 (superseding the earlier eu-west-1 draft) | ap-southeast-2 | yes | yes | 2 |
| czip | revoked_fallback | revocation | NO | NO | yes | yes | 5 |
| czip | reopened_issue | temporal | OPEN | OPEN | yes | yes | 5 |
| czip | approval_boundary | instruction | USER | USER | yes | yes | 2 |
| czip | unknown_pin | abstention | UNKNOWN — the conversation never states the actual ORION approval PIN. It only records the rule that the user must enter the approval PIN on their own phone and the assistant may never enter it. | UNKNOWN | yes | yes | 2 |
| summary | early_exact | early_exact | RB-QWHKS8W4 | RB-QWHKS8W4 | yes | yes | 0 |
| summary | two_hop | two_hop | ESC-5FTCNL43 | ESC-5FTCNL43 | yes | yes | 0 |
| summary | tool_evidence | tool_evidence | SHA-BY9Q5UAB | SHA-BY9Q5UAB | yes | yes | 0 |
| summary | superseded_region | update | ap-southeast-2 | ap-southeast-2 | yes | yes | 0 |
| summary | revoked_fallback | revocation | NO | NO | yes | yes | 0 |
| summary | reopened_issue | temporal | OPEN | OPEN | yes | yes | 0 |
| summary | approval_boundary | instruction | USER | USER | yes | yes | 0 |
| summary | unknown_pin | abstention | UNKNOWN — the PIN itself was never recorded; the user must enter it on their own phone (assistant may never enter it). | UNKNOWN | yes | yes | 0 |
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
