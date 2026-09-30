# Benchmark protocol

## Claims under test

1. A finite-window model with Czip can answer questions from a history that
   no longer fits in its immediate prompt.
2. It can identify the current user decision when prior messages disagree.
3. It can retrieve and cite the source messages for the answer.
4. It can abstain when the history never supplied the requested value.

These are empirical system claims. They do not imply an infinite native model
context or an ability unique to Czip.

## Controlled comparison

- Use the exact same model artifact/build, decoding parameters, seed datasets,
  question text, host, and server configuration for all arms.
- Run `czip`, `summary`, and `tail`. Add `full` only if the entire history fits;
  report context-overflow errors as failures, not silently omitted rows.
- Set and disclose `--tail-messages`, `--summary-budget-chars`,
  `--summary-chunk-messages`, `--tool-budget`, and `--disable-thinking`.
- Run at least three seeds, including one generated after the method was
  frozen. Keep the generation command and dataset SHA-256 for every run.
- Do not tune Czip search prompts on the evaluation seeds and then describe
  them as held out.
- Report both answer accuracy and grounded accuracy. The latter requires all
  gold evidence indices and proof they were accessible to the answering model.
- Include failed API calls and malformed model responses in the denominator.
- Report model usage tokens only if every completed API call returned usage;
  otherwise give measured input characters and mark tokens unavailable.
- Include summary preparation calls, prompt tokens, and time in total cost.
  HKP1 packing time and archive disk size should also be shown separately.

## Reproducibility metadata

Publish the dataset and Czip SHA-256 hashes, git commits, full command lines,
model weights/build identifier, quantization, context-window setting, inference
server/version, hardware, whether the endpoint was local, and the complete
`results.json` and `report.md`. Redact only secrets and personal data. Do not
substitute an unverifiable chart for the raw run.

## Interpretation

The public generator has eight probes and limited linguistic variety, so it
is a functional benchmark and demo. The `two_hop` item requires two source
messages; the update and revocation items intentionally include conflicting
history. Good performance on one seed is a reason to scale the experiment,
not a claim of universal memory or superiority over every other model.
