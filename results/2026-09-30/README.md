# Local GLM run — 30 September 2026

**Model returned by the API:** `GLM-5.3-Flash-EXL3`. The operator described
the serving setup as TP=2; the API verified the model ID but did not expose
tensor-parallel configuration or a context-window limit. All arms used the
same local OpenAI-compatible endpoint with temperature 0 and
`--disable-thinking`. The private LAN endpoint is redacted from the public
copies. The original local `runs/` files remain unchanged; each public JSON
records its original SHA-256.

## Answer and source accuracy

| History | Arm | Grounded correct | Total prompt tokens | Preparation |
|---|---|---:|---:|---|
| 615 messages, seed 20260930 | Czip | **8/8** | 71,243 | 0.093 s to pack; 13,120 B |
| 615 messages, seed 20260930 | Rolling summary | **8/8** | 88,171 including setup | 26 model calls; 344.957 s |
| 615 messages, seed 20260930 | Full history | **8/8** | 369,536 | Whole history sent for each question |
| 615 messages, seed 20260930 | Last 24 messages | **1/8** | 15,592 | No preparation |
| 4,015 messages, seed 20261001 | Czip | **8/8** | 73,004 | 0.810 s to pack; 72,640 B |
| 4,015 messages, seed 20261001 | Last 24 messages | **1/8** | 15,864 | No preparation |
| 4,015 messages, seed 20261002 | Czip | **8/8** | 72,547 | 0.760 s to pack; 72,952 B |
| 4,015 messages, seed 20261002 | Last 24 messages | **1/8** | 17,869 | No preparation |

The 615-message corpus contains 186,617 characters of message content. The
two 4,015-message corpora contain 1,240,803 and 1,240,779 characters. These
are character counts, **not GLM token counts**. The serving API did not expose
a tokenizer endpoint or native context-limit metadata. We do not claim from
these runs that the larger corpus definitively exceeded the model's context
window. The full-history and summary arms were not run on the larger corpora.

On the 615-message development seed, Czip used **5.19× fewer prompt tokens**
than resending full history for all eight questions. Czip and the rolling
summary tied on accuracy; Czip used **19.2% fewer total prompt tokens** and
had much shorter preparation in this run. Its answer calls were slower per
question because they included retrieval steps. The last-message baseline
was cheaper but answered only the abstention item correctly.

## Reproduce and inspect

Each directory contains a per-question [report](615-comparison/report.md)
and a JSON trace. The four final run copies are:

- [615-message Czip, summary, and tail](615-comparison/results.json)
- [615-message full-history arm](615-full/results.json)
- [4,015-message seed 20261001](4015-seed-20261001/results.json)
- [4,015-message seed 20261002](4015-seed-20261002/results.json)

The dataset is generated from `bench.py`; it is not fetched from a private
conversation. Generator commands:

```bash
python bench.py generate --seed 20260930 --filler-per-gap 60 --output data/public-seed.json
python bench.py generate --seed 20261001 --filler-per-gap 400 --output data/deep-seed.json
python bench.py generate --seed 20261002 --filler-per-gap 400 --output data/deep-seed-2.json
```

All final runs used harness SHA-256
`a612f083d22d64bda66300ebdace2bc955500efbb58fd5d40773694fc9ed2542`.
Czip runs used engine SHA-256
`a219624cc2e1b24af3d194c5bc7994ba4a226f7bf0e18eb87bb5feb99799347e`
(Czip commit `6a2273fa53069c2dd2b436cc69c839f9fb03afb8`).

## Development history and limits

The [first development attempt](development-attempt/results.json) is retained
for transparency. It produced six short correct Czip answers out of eight,
zero answers under the original source-read rule, and a summary-preparation
failure. We then required explicit source reads, clarified which source is
required for a current-state answer, and disabled model thinking for the
limited output budget. That attempt is **not** comparable with the final
protocol, and its engine hash was captured after its source file changed
during the run. The 615-message final run used the development seed. The
larger seeds were run after the harness was frozen.

The eight probes are synthetic and share one template across seeds. This is
a transparent functional demo, not a statistical claim of universal memory
or superiority over every competing memory system. A finite context window
still exists, and both Czip and the rolling summary scored 8/8 at the
615-message scale.
