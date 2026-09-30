# Czip Continuity Gauntlet — Run Report

*Public copy: local endpoint redacted; original results.json SHA-256 `ca9fc07bed407887a3fa8b1d55c607b2ac514f8a162696c95421b37377b19387`.*

- Dataset SHA-256: `c47e27ff03357761b9466727063de35ab9ef3b1d3fece24e075a6e3907378faa`
- Czip engine SHA-256: `a219624cc2e1b24af3d194c5bc7994ba4a226f7bf0e18eb87bb5feb99799347e`
- Model: `GLM-5.3-Flash-EXL3`
- Endpoint: `local endpoint (redacted)`
- Generated: `2026-09-30T05:13:42.830106+00:00`

| Arm | Completed | Correct / total | Grounded / total | Prompt tokens incl. setup | Input chars incl. setup | Median latency (s) |
|---|---:|---:|---:|---:|---:|---:|
| czip | 8/8 | 8/8 | 8/8 | 72547 | 258595 | 3.734 |
| tail | 8/8 | 1/8 | 1/8 | 17869 | 83084 | 0.684 |
Czip full-pack preparation: 72952 bytes on disk, 0.76 seconds. This is outside model prompt tokens.


## Per-question results

| Arm | Probe | Category | Answer | Expected | Correct | Grounded | Calls |
|---|---|---|---|---|---|---|---:|
| czip | early_exact | early_exact | RB-FE7MY7WR | RB-FE7MY7WR | yes | yes | 2 |
| czip | two_hop | two_hop | ESC-GNCWAGD6 | ESC-GNCWAGD6 | yes | yes | 5 |
| czip | tool_evidence | tool_evidence | SHA-JV562A6Q | SHA-JV562A6Q | yes | yes | 2 |
| czip | superseded_region | update | ap-southeast-2 (superseding the earlier eu-west-1 draft) | ap-southeast-2 | yes | yes | 2 |
| czip | revoked_fallback | revocation | NO | NO | yes | yes | 5 |
| czip | reopened_issue | temporal | OPEN | OPEN | yes | yes | 5 |
| czip | approval_boundary | instruction | USER | USER | yes | yes | 2 |
| czip | unknown_pin | abstention | UNKNOWN — the archive states the ORION release approval PIN must be entered by the user on their own phone and the assistant may never enter it; the PIN value itself was never given. | UNKNOWN | yes | yes | 2 |
| tail | early_exact | early_exact | UNKNOWN | RB-FE7MY7WR | no | no | 0 |
| tail | two_hop | two_hop | UNKNOWN | ESC-GNCWAGD6 | no | no | 0 |
| tail | tool_evidence | tool_evidence | UNKNOWN | SHA-JV562A6Q | no | no | 0 |
| tail | superseded_region | update | UNKNOWN | ap-southeast-2 | no | no | 0 |
| tail | revoked_fallback | revocation | UNKNOWN | NO | no | no | 0 |
| tail | reopened_issue | temporal | UNKNOWN | OPEN | no | no | 0 |
| tail | approval_boundary | instruction | UNKNOWN | USER | no | no | 0 |
| tail | unknown_pin | abstention | UNKNOWN | UNKNOWN | yes | yes | 0 |

## Interpretation

Grounded accuracy requires the exact short answer, every required source index, and proof that the cited source was exposed to the answering model. Missing or failed probes count against the total. Prompt tokens are reported only when the API supplies usage for every completed request.

This is a synthetic, single logical conversation replay with per-question API calls. It measures retrieval-assisted continuity; it does not prove an infinite native context window, or that a competing memory system cannot match the result.
