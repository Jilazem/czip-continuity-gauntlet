# Czip Continuity Gauntlet — Run Report

*Public copy: local endpoint redacted; original results.json SHA-256 `b0b5a3de3252fbbb96c47254d4fd975487f2dd42ee1e49a950ac959061d84cea`.*

- Dataset SHA-256: `b56342843efc1434fc094d2b464bb3169082447f33043e698fd0ef6a4f3bfa2e`
- Czip engine SHA-256: `a219624cc2e1b24af3d194c5bc7994ba4a226f7bf0e18eb87bb5feb99799347e`
- Model: `GLM-5.3-Flash-EXL3`
- Endpoint: `local endpoint (redacted)`
- Generated: `2026-09-30T05:10:06.348491+00:00`

| Arm | Completed | Correct / total | Grounded / total | Prompt tokens incl. setup | Input chars incl. setup | Median latency (s) |
|---|---:|---:|---:|---:|---:|---:|
| czip | 8/8 | 8/8 | 8/8 | 73004 | 258665 | 3.252 |
| tail | 8/8 | 1/8 | 1/8 | 15864 | 72816 | 0.675 |
Czip full-pack preparation: 72640 bytes on disk, 0.81 seconds. This is outside model prompt tokens.


## Per-question results

| Arm | Probe | Category | Answer | Expected | Correct | Grounded | Calls |
|---|---|---|---|---|---|---|---:|
| czip | early_exact | early_exact | RB-HMSYN3DE | RB-HMSYN3DE | yes | yes | 2 |
| czip | two_hop | two_hop | ESC-JN7GAHTZ | ESC-JN7GAHTZ | yes | yes | 5 |
| czip | tool_evidence | tool_evidence | SHA-2CE6QGG6 | SHA-2CE6QGG6 | yes | yes | 2 |
| czip | superseded_region | update | ap-southeast-2 (superseding the earlier eu-west-1 draft) | ap-southeast-2 | yes | yes | 2 |
| czip | revoked_fallback | revocation | NO | NO | yes | yes | 2 |
| czip | reopened_issue | temporal | OPEN | OPEN | yes | yes | 3 |
| czip | approval_boundary | instruction | USER | USER | yes | yes | 2 |
| czip | unknown_pin | abstention | UNKNOWN | UNKNOWN | yes | yes | 6 |
| tail | early_exact | early_exact | UNKNOWN | RB-HMSYN3DE | no | no | 0 |
| tail | two_hop | two_hop | UNKNOWN | ESC-JN7GAHTZ | no | no | 0 |
| tail | tool_evidence | tool_evidence | UNKNOWN | SHA-2CE6QGG6 | no | no | 0 |
| tail | superseded_region | update | UNKNOWN | ap-southeast-2 | no | no | 0 |
| tail | revoked_fallback | revocation | UNKNOWN | NO | no | no | 0 |
| tail | reopened_issue | temporal | UNKNOWN | OPEN | no | no | 0 |
| tail | approval_boundary | instruction | UNKNOWN | USER | no | no | 0 |
| tail | unknown_pin | abstention | UNKNOWN | UNKNOWN | yes | yes | 0 |

## Interpretation

Grounded accuracy requires the exact short answer, every required source index, and proof that the cited source was exposed to the answering model. Missing or failed probes count against the total. Prompt tokens are reported only when the API supplies usage for every completed request.

This is a synthetic, single logical conversation replay with per-question API calls. It measures retrieval-assisted continuity; it does not prove an infinite native context window, or that a competing memory system cannot match the result.
