#!/usr/bin/env python3
"""Reproducible continuity benchmark for Czip and finite-context baselines.

No external Python packages are required. The Czip engine is loaded from an
explicit checkout; this repository does not redistribute it.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import random
import re
import statistics
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "czip-continuity-gauntlet/1"
SYSTEM = (
    "You are resuming one long-running engineering conversation. Answer only from "
    "the recorded messages. The memory may include corrections: prefer the latest "
    "explicit user instruction. Never invent a missing fact. Return a single JSON "
    "object. To request Czip memory, use {\"action\":\"search\",\"query\":\"...\"} "
    "or {\"action\":\"read\",\"index\":N}. To finish, use "
    "{\"action\":\"answer\",\"answer\":\"...\",\"evidence\":[N,...]}. "
    "Evidence contains zero-based message indices. If the requested fact was never "
    "given, answer UNKNOWN with no evidence. Give only the requested short value."
)


def _code(rng: random.Random, prefix: str) -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return prefix + "-" + "".join(rng.choices(alphabet, k=8))


def make_dataset(seed: int, filler_per_gap: int) -> dict:
    if filler_per_gap < 4:
        raise ValueError("filler_per_gap must be at least 4")
    rng = random.Random(seed)
    messages: list[dict] = []
    probes: list[dict] = []

    def add(role: str, content: str) -> int:
        index = len(messages)
        messages.append({"role": role, "content": content, "id": index + 1,
                         "timestamp": 1_780_000_000 + index})
        return index

    def filler(stage: str) -> None:
        topics = ("asset manifest", "UI labels", "staging telemetry", "log rotation",
                  "test fixture", "release notes", "on-call calendar", "cache warming")
        for j in range(filler_per_gap):
            item = _code(rng, "TASK")
            topic = topics[(j + len(stage)) % len(topics)]
            detail = " ".join(rng.choice(topics) for _ in range(14))
            add("user", f"{stage} / {item}: Please review the {topic}. Notes: {detail}. "
                        "This is routine project chatter, not a policy change.")
            add("assistant", f"Recorded {item}. I will keep the {topic} in the routine "
                             f"work queue. Review context: {detail}.")

    rollback = _code(rng, "RB")
    checksum = _code(rng, "SHA")
    escalation = _code(rng, "ESC")
    distractor = _code(rng, "RB")
    add("user", "We are continuing the ORION migration in this one project thread. "
                "Keep decisions and evidence as the work evolves.")
    rollback_i = add("user", f"For ORION only, the verified rollback code is {rollback}. "
                          f"The separate LYRA project uses {distractor}; never mix them.")
    add("assistant", "I recorded both project scopes and will cite the source when asked.")
    probes.append({"id": "early_exact", "category": "early_exact",
                   "question": "What is ORION's verified rollback code?",
                   "answer": rollback, "evidence": [rollback_i]})
    filler("Planning")

    region_old_i = add("user", "Initial ORION deployment region: eu-west-1. This is a draft "
                            "and may change after infrastructure review.")
    cloud_old_i = add("user", "During early prototyping, a cloud fallback was allowed for "
                           "ORION image processing. Revisit before release.")
    status_old_i = add("user", "Incident ORI-42 is OPEN while the checksum is being checked.")
    filler("Implementation")

    component_i = add("user", "In ORION, the owner of the Nimbus component is the "
                            "Delta operations team. This ownership link is authoritative.")
    owner_i = add("tool", f"Operations directory: Delta operations team -> escalation "
                        f"code {escalation}. Echo operations team -> escalation code "
                        f"{_code(rng, 'ESC')}.")
    probes.append({"id": "two_hop", "category": "two_hop",
                   "question": "What escalation code belongs to the owner of ORION's Nimbus component?",
                   "answer": escalation, "evidence": [component_i, owner_i]})
    checksum_i = add("tool", f"ORION artifact integrity report, release candidate 3: "
                           f"approved checksum label {checksum}. LYRA is unrelated.")
    probes.append({"id": "tool_evidence", "category": "tool_evidence",
                   "question": "What is the approved checksum label for ORION release candidate 3?",
                   "answer": checksum, "evidence": [checksum_i]})
    filler("Verification")

    region_new_i = add("user", "Correction to my earlier ORION region draft: the approved "
                            "deployment region is ap-southeast-2. Supersede eu-west-1.")
    cloud_new_i = add("user", "Final ORION release rule: cloud fallback is forbidden, even "
                           "if a local provider times out. This supersedes the prototype rule.")
    status_closed_i = add("user", "Incident ORI-42 is CLOSED after checksum review.")
    probes.extend([
        {"id": "superseded_region", "category": "update",
         "question": "What is ORION's currently approved deployment region?",
         "answer": "ap-southeast-2", "evidence": [region_new_i],
         "superseded_evidence": [region_old_i]},
        {"id": "revoked_fallback", "category": "revocation",
         "question": "Is cloud fallback currently allowed for ORION? Answer YES or NO.",
         "answer": "NO", "evidence": [cloud_new_i],
         "superseded_evidence": [cloud_old_i]},
    ])
    filler("Release")

    status_reopen_i = add("user", "Update: incident ORI-42 has REOPENED because the final "
                              "deployment check failed. Treat it as OPEN now.")
    approval_i = add("user", "ORION release approval must be entered by the user on their "
                          "own phone. The assistant may never enter the approval PIN.")
    probes.extend([
        {"id": "reopened_issue", "category": "temporal",
         "question": "What is the current status of incident ORI-42? Answer OPEN or CLOSED.",
         "answer": "OPEN", "evidence": [status_reopen_i],
         "superseded_evidence": [status_old_i, status_closed_i]},
        {"id": "approval_boundary", "category": "instruction",
         "question": "Who must enter the ORION release approval PIN? Answer USER or ASSISTANT.",
         "answer": "USER", "evidence": [approval_i]},
        {"id": "unknown_pin", "category": "abstention",
         "question": "What is the ORION release approval PIN?",
         "answer": "UNKNOWN", "evidence": []},
    ])
    filler("Post-release")
    add("assistant", "I am ready to continue this project from the recorded state.")
    dataset = {"schema": SCHEMA, "seed": seed, "filler_per_gap": filler_per_gap,
               "messages": messages, "probes": probes}
    validate_dataset(dataset)
    return dataset


def validate_dataset(data: dict) -> None:
    if data.get("schema") != SCHEMA:
        raise ValueError("unsupported dataset schema")
    messages = data.get("messages")
    probes = data.get("probes")
    if not isinstance(messages, list) or not isinstance(probes, list) or not probes:
        raise ValueError("invalid messages or probes")
    ids = set()
    for probe in probes:
        if probe["id"] in ids:
            raise ValueError("duplicate probe id")
        ids.add(probe["id"])
        if not isinstance(probe["answer"], str) or not probe["answer"]:
            raise ValueError("empty answer")
        if probe["category"] not in {"temporal", "revocation", "instruction", "abstention"}:
            if probe["answer"].lower() in probe["question"].lower():
                raise ValueError("answer leaked into question: " + probe["id"])
        for index in probe["evidence"]:
            if not isinstance(index, int) or not 0 <= index < len(messages):
                raise ValueError("invalid evidence index")
            if index >= len(messages) - 2:
                raise ValueError("probe evidence too near the end")
    if data["messages"][-1]["role"] != "assistant":
        raise ValueError("conversation must end with the assistant")


def load_czip(source: str):
    path = Path(source).expanduser().resolve() / "hkp.py"
    if not path.is_file():
        raise FileNotFoundError(f"Czip engine not found at {path}")
    spec = importlib.util.spec_from_file_location("czip_hkp_benchmark", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _post_chat(base_url: str, model: str, messages: list[dict], timeout: int,
               api_key: str | None, max_output_tokens: int,
               disable_thinking: bool = False) -> tuple[str, dict]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {"model": model, "messages": messages, "temperature": 0,
               "max_tokens": max_output_tokens, "stream": False}
    if disable_thinking:
        payload["chat_template_kwargs"] = {"enable_thinking": False}
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        snippet = exc.read(700).decode("utf-8", "replace")
        raise RuntimeError(f"model HTTP {exc.code}: {snippet}") from exc
    content = result["choices"][0]["message"].get("content") or ""
    if isinstance(content, list):
        content = "".join(x.get("text", "") for x in content if isinstance(x, dict))
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("model returned no assistant content")
    return content, result.get("usage") or {}


def _json_object(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I | re.S)
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("model did not return JSON")
        obj = json.loads(text[start:end + 1])
    if not isinstance(obj, dict):
        raise ValueError("model response is not a JSON object")
    return obj


def _norm(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().strip(".\"'` ")).upper()


def _answer_matches(actual: object, expected: str) -> bool:
    value = _norm(actual)
    target = _norm(expected)
    return bool(re.match(r"^" + re.escape(target) + r"(?=$|[\s(—,:;.])", value))


def grade(probe: dict, answer: object, evidence: object) -> dict:
    correct = _answer_matches(answer, probe["answer"])
    indices = evidence if isinstance(evidence, list) else []
    indices = [x for x in indices if isinstance(x, int) and not isinstance(x, bool)]
    evidence_ok = set(probe["evidence"]).issubset(set(indices))
    if probe["category"] == "abstention":
        evidence_ok = True
    return {"correct": correct, "evidence_ok": evidence_ok,
            "grounded": correct and evidence_ok}


def _indexed_messages(messages: list[dict], start: int = 0) -> str:
    return "\n".join(json.dumps({"index": i, "role": m["role"],
                                  "content": m["content"]}, ensure_ascii=False)
                     for i, m in enumerate(messages, start=start))


def build_rolling_summary(messages: list[dict], chat, chunk_messages: int,
                          budget_chars: int) -> tuple[str, dict]:
    """A stronger baseline: the same model compacts the chat as it arrives."""
    if chunk_messages < 2 or budget_chars < 200:
        raise ValueError("summary chunk must be >=2 messages and budget >=200 chars")
    summary = ""
    usage_total = {"prompt_tokens": 0, "completion_tokens": 0}
    usage_seen = True
    input_chars = 0
    calls = 0
    started = time.monotonic()
    total_calls = (len(messages) + chunk_messages - 1) // chunk_messages
    for start in range(0, len(messages), chunk_messages):
        chunk = _indexed_messages(messages[start:start + chunk_messages], start)
        prompt = (
            f"Update a durable engineering handoff note. Keep current user decisions, "
            f"superseded decisions with their order, exact codes, unresolved items, tool "
            f"evidence and source message indices in [N] notation. Never invent facts. Limit your output "
            f"to {budget_chars} characters.\n\nEXISTING NOTE:\n{summary}\n\nNEW MESSAGES:\n{chunk}"
        )
        input_chars += len(prompt)
        raw, usage = chat([{"role": "system", "content": "Write only the updated handoff note."},
                           {"role": "user", "content": prompt}])
        calls += 1
        summary = raw[:budget_chars]
        if calls == 1 or calls % 5 == 0 or calls == total_calls:
            print(f"summary preparation {calls}/{total_calls}", flush=True)
        if not usage:
            usage_seen = False
        else:
            for key in usage_total:
                usage_total[key] += int(usage.get(key) or 0)
    return summary, {"calls": calls, "input_chars": input_chars,
                     "seconds": round(time.monotonic() - started, 3),
                     "usage": usage_total if usage_seen else None}


def run_probe(probe: dict, messages: list[dict], arm: str, chat,
              czip=None, pack_path: str | None = None, tail_messages: int = 24,
              tool_budget: int = 6, summary: str | None = None) -> dict:
    start_time = time.monotonic()
    if arm == "czip":
        memory = "CZIP MAP:\n" + json.dumps(czip.harita(pack_path, son_n=2), ensure_ascii=False)
        memory += "\nYou may search or read the Czip archive. Do not assume the map is complete."
    elif arm == "tail":
        start = max(0, len(messages) - tail_messages)
        memory = "AVAILABLE RECENT MESSAGES:\n" + _indexed_messages(messages[start:], start)
        memory += "\nNo older messages or retrieval tools are available."
    elif arm == "full":
        memory = "FULL HISTORY:\n" + _indexed_messages(messages)
        memory += "\nNo retrieval tools are needed."
    elif arm == "summary":
        if summary is None:
            raise ValueError("summary arm requires a prepared handoff note")
        memory = "ROLLING HANDOFF NOTE:\n" + summary
        memory += "\nNo retrieval tools are available."
    else:
        raise ValueError("unknown arm")
    prompt = (memory + "\n\nQUESTION: " + probe["question"] +
              "\nReturn the answer JSON now, or a search/read JSON action if available.")
    conversation = [{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt}]
    tool_calls = 0
    read_indices = set()
    usage_total = {"prompt_tokens": 0, "completion_tokens": 0}
    usage_seen = False
    input_chars = 0
    transcript = []
    final = None
    max_turns = tool_budget + 5 if arm == "czip" else 2
    for _ in range(max_turns):
        input_chars += sum(len(m["content"]) for m in conversation)
        raw, usage = chat(conversation)
        if usage:
            usage_seen = True
            for key in usage_total:
                usage_total[key] += int(usage.get(key) or 0)
        transcript.append({"model": raw, "usage": usage})
        try:
            action = _json_object(raw)
        except (ValueError, json.JSONDecodeError) as exc:
            conversation.append({"role": "assistant", "content": raw})
            conversation.append({"role": "user", "content": f"Invalid JSON: {exc}. Return valid answer JSON."})
            continue
        if action.get("action") == "answer":
            if arm == "czip" and tool_calls < tool_budget:
                cited = action.get("evidence") if isinstance(action.get("evidence"), list) else []
                unread = [i for i in cited if isinstance(i, int) and i not in read_indices]
                if unread:
                    conversation.append({"role": "assistant", "content": raw})
                    conversation.append({"role": "user", "content":
                                         "Before finalizing, open the source messages you cited "
                                         f"with read actions: {unread}. Then answer again. "
                                         "For UNKNOWN, evidence may be an empty list."})
                    continue
            final = action
            break
        if arm != "czip":
            conversation.append({"role": "assistant", "content": raw})
            conversation.append({"role": "user", "content": "No tools are available. Answer or abstain now."})
            continue
        if tool_calls >= tool_budget:
            conversation.append({"role": "assistant", "content": raw})
            conversation.append({"role": "user", "content": "Tool budget exhausted. Answer or abstain now."})
            continue
        tool_calls += 1
        try:
            if action.get("action") == "search":
                query = str(action.get("query", ""))[:120]
                result = czip.paket_ara(pack_path, query, max_satir=8)
            elif action.get("action") == "read":
                index = int(action["index"])
                result = {"index": index,
                          "messages": czip.mesaj_araligi(pack_path, str(index))}
                read_indices.add(index)
            else:
                result = {"error": "unknown action; use search, read, or answer"}
        except (ValueError, KeyError, IndexError) as exc:
            result = {"error": str(exc)}
        transcript.append({"tool": action, "result": result})
        conversation.append({"role": "assistant", "content": raw})
        conversation.append({"role": "user", "content": "CZIP RESULT:\n" +
                             json.dumps(result, ensure_ascii=False) +
                             "\nContinue. Cite exact zero-based indices in the final answer."})
    final = final or {"action": "answer", "answer": "", "evidence": []}
    score = grade(probe, final.get("answer"), final.get("evidence"))
    cited = final.get("evidence") if isinstance(final.get("evidence"), list) else []
    cited = {x for x in cited if isinstance(x, int) and not isinstance(x, bool)}
    if arm == "czip":
        accessible = read_indices
    elif arm == "tail":
        accessible = set(range(max(0, len(messages) - tail_messages), len(messages)))
    elif arm == "full":
        accessible = set(range(len(messages)))
    else:
        accessible = {int(i) for i in re.findall(r"\[(\d+)\]", summary or "")}
    evidence_read = cited.issubset(accessible)
    score["grounded"] = score["grounded"] and evidence_read
    return {"id": probe["id"], "category": probe["category"], "arm": arm,
            "expected": probe["answer"], "answer": final.get("answer"),
            "gold_evidence": probe["evidence"], "cited_evidence": final.get("evidence"),
            **score, "evidence_read": evidence_read,
            "tool_calls": tool_calls, "input_chars": input_chars,
            "usage": usage_total if usage_seen else None,
            "latency_seconds": round(time.monotonic() - start_time, 3),
            "trace": transcript}


def summarize(results: list[dict], arms: list[str], total_probes: int) -> dict:
    out = {}
    for arm in arms:
        rows = [row for row in results if row["arm"] == arm]
        completed = [row for row in rows if "error" not in row]
        out[arm] = {
            "completed": len(completed), "total": total_probes,
            "accuracy": sum(x["correct"] for x in completed) / total_probes,
            "grounded_accuracy": sum(x["grounded"] for x in completed) / total_probes,
            "tool_calls": sum(x["tool_calls"] for x in completed),
            "input_chars": sum(x["input_chars"] for x in completed),
            "prompt_tokens": (sum(x["usage"]["prompt_tokens"] for x in completed)
                              if completed and all(x["usage"] is not None for x in completed)
                              else None),
            "median_latency_seconds": (round(statistics.median(x["latency_seconds"] for x in completed), 3)
                                       if completed else None),
        }
    return out


def markdown_report(record: dict) -> str:
    lines = ["# Czip Continuity Gauntlet — Run Report", "",
             f"- Dataset SHA-256: `{record['dataset_sha256']}`",
             f"- Czip engine SHA-256: `{record.get('czip_sha256') or 'not used'}`",
             f"- Model: `{record['model']}`", f"- Endpoint: `{record['endpoint']}`",
             f"- Generated: `{record['generated_at']}`", "",
             "| Arm | Completed | Correct / total | Grounded / total | Prompt tokens incl. setup | Input chars incl. setup | Median latency (s) |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for arm, item in record["summary"].items():
        total = item["total"]
        correct = round(item["accuracy"] * total)
        grounded = round(item["grounded_accuracy"] * total)
        tokens = item["prompt_tokens"] if item["prompt_tokens"] is not None else "unavailable"
        lines.append(f"| {arm} | {item['completed']}/{total} | {correct}/{total} | "
                     f"{grounded}/{total} | {tokens} | {item['input_chars']} | "
                     f"{item['median_latency_seconds']} |")
    if record.get("summary_setup"):
        setup = record["summary_setup"]
        lines += ["", "Rolling summary preparation: " +
                  (f"{setup['calls']} model calls, {setup['seconds']} seconds, "
                   f"{setup['input_chars']} input characters; "
                   f"prompt tokens: {setup['usage']['prompt_tokens'] if setup['usage'] else 'unavailable'}."
                   if "error" not in setup else f"failed: {setup['error']}"), ""]
    if record.get("pack_stats"):
        pack = record["pack_stats"]
        lines += [f"Czip full-pack preparation: {pack['paket_bayt']} bytes on disk, "
                  f"{record['pack_seconds']} seconds. This is outside model prompt tokens.", ""]
    lines += ["", "## Per-question results", "",
              "| Arm | Probe | Category | Answer | Expected | Correct | Grounded | Calls |",
              "|---|---|---|---|---|---|---|---:|"]
    for row in record["results"]:
        if "error" in row:
            lines.append(f"| {row['arm']} | {row['id']} | error | — | — | no | no | 0 |")
        else:
            answer = str(row["answer"]).replace("|", "\\|")
            lines.append(f"| {row['arm']} | {row['id']} | {row['category']} | {answer} | "
                         f"{row['expected']} | {'yes' if row['correct'] else 'no'} | "
                         f"{'yes' if row['grounded'] else 'no'} | {row['tool_calls']} |")
    lines += ["", "## Interpretation", "",
              "Grounded accuracy requires the exact short answer, every required source index, "
              "and proof that the cited source was exposed to the answering model. "
              "Missing or failed probes count against the total. Prompt tokens are reported only "
              "when the API supplies usage for every completed request.", "",
              "This is a synthetic, single logical conversation replay with per-question API calls. "
              "It measures retrieval-assisted continuity; it does not prove an infinite native "
              "context window, or that a competing memory system cannot match the result.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    generate = sub.add_parser("generate", help="create a deterministic synthetic conversation")
    generate.add_argument("--seed", type=int, default=20260930)
    generate.add_argument("--filler-per-gap", type=int, default=60)
    generate.add_argument("--output", type=Path, required=True)
    run = sub.add_parser("run", help="run Czip and baseline arms against a local chat API")
    run.add_argument("--dataset", type=Path, required=True)
    run.add_argument("--out-dir", type=Path, required=True)
    run.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    run.add_argument("--model", required=True)
    run.add_argument("--czip-source", type=Path)
    run.add_argument("--arms", nargs="+", choices=["czip", "summary", "tail", "full"],
                     default=["czip", "summary", "tail"])
    run.add_argument("--tail-messages", type=int, default=24)
    run.add_argument("--tool-budget", type=int, default=6)
    run.add_argument("--summary-chunk-messages", type=int, default=24)
    run.add_argument("--summary-budget-chars", type=int, default=4000)
    run.add_argument("--timeout", type=int, default=180)
    run.add_argument("--max-output-tokens", type=int, default=180)
    run.add_argument("--disable-thinking", action="store_true",
                     help="send chat_template_kwargs.enable_thinking=false to compatible servers")
    run.add_argument("--api-key-env", default="CZCG_API_KEY")
    args = parser.parse_args(argv)
    if args.command == "generate":
        dataset = make_dataset(args.seed, args.filler_per_gap)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({"dataset": str(args.output), "messages": len(dataset["messages"]),
                          "probes": len(dataset["probes"]), "sha256": _sha256(args.output)}))
        return 0
    if args.tail_messages < 1 or args.tool_budget < 0:
        parser.error("tail messages must be positive and tool budget nonnegative")
    data = json.loads(args.dataset.read_text(encoding="utf-8"))
    validate_dataset(data)
    if "czip" in args.arms and not args.czip_source:
        parser.error("--czip-source is required for the czip arm")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    engine_sha = _sha256(args.czip_source / "hkp.py") if "czip" in args.arms else None
    harness_sha = _sha256(Path(__file__))
    engine = load_czip(str(args.czip_source)) if "czip" in args.arms else None
    pack_path = None
    pack_stats = None
    pack_seconds = None
    if engine:
        pack_start = time.monotonic()
        pack_stats = engine.sikistir(data["messages"], str(args.out_dir / "conversation"),
                                     mod="eksiksiz", baslik="Continuity Gauntlet")
        pack_seconds = round(time.monotonic() - pack_start, 3)
        if not pack_stats.get("ok"):
            raise RuntimeError("Czip packing failed: " + json.dumps(pack_stats))
        pack_path = pack_stats["yol"]
    key = os.environ.get(args.api_key_env)

    def chat(conversation, tokens=None):
        return _post_chat(args.base_url, args.model, conversation, args.timeout,
                          key, tokens or args.max_output_tokens, args.disable_thinking)

    summary_text = None
    summary_setup = None
    if "summary" in args.arms:
        try:
            summary_text, summary_setup = build_rolling_summary(
                data["messages"], lambda convo: chat(convo, 1200), args.summary_chunk_messages,
                args.summary_budget_chars)
        except (RuntimeError, urllib.error.URLError, TimeoutError, KeyError, ValueError) as exc:
            summary_setup = {"error": str(exc)}
    results = []
    for arm in args.arms:
        for probe in data["probes"]:
            try:
                row = run_probe(probe, data["messages"], arm, chat, engine, pack_path,
                                args.tail_messages, args.tool_budget, summary_text)
            except (RuntimeError, urllib.error.URLError, TimeoutError, KeyError, ValueError) as exc:
                row = {"id": probe["id"], "arm": arm, "error": str(exc)}
            results.append(row)
            print(f"{arm:5s} {probe['id']:20s} " +
                  ("ERROR " + row["error"] if "error" in row else
                   f"correct={row['correct']} grounded={row['grounded']}"), flush=True)
    summary_metrics = summarize(results, args.arms, len(data["probes"]))
    if "summary" in args.arms and summary_setup and "error" not in summary_setup:
        summary_metrics["summary"]["input_chars"] += summary_setup["input_chars"]
        setup_usage = summary_setup.get("usage")
        if summary_metrics["summary"]["prompt_tokens"] is not None and setup_usage:
            summary_metrics["summary"]["prompt_tokens"] += setup_usage["prompt_tokens"]
        else:
            summary_metrics["summary"]["prompt_tokens"] = None
    record = {"schema": SCHEMA, "dataset_sha256": _sha256(args.dataset),
              "czip_sha256": engine_sha, "harness_sha256": harness_sha,
              "model": args.model, "endpoint": args.base_url,
              "generated_at": datetime.now(timezone.utc).isoformat(),
              "settings": {"arms": args.arms, "tail_messages": args.tail_messages,
                           "tool_budget": args.tool_budget, "max_output_tokens": args.max_output_tokens,
                           "pack_mode": "full" if engine else None,
                           "summary_chunk_messages": args.summary_chunk_messages,
                           "summary_budget_chars": args.summary_budget_chars,
                           "disable_thinking": args.disable_thinking},
              "pack_stats": {k: v for k, v in pack_stats.items() if k != "yol"} if pack_stats else None,
              "pack_seconds": pack_seconds, "summary_setup": summary_setup,
              "results": results, "summary": summary_metrics}
    (args.out_dir / "results.json").write_text(json.dumps(record, indent=2, ensure_ascii=False),
                                                  encoding="utf-8")
    (args.out_dir / "report.md").write_text(markdown_report(record), encoding="utf-8")
    print(f"Report: {args.out_dir / 'report.md'}")
    return 0 if all("error" not in row for row in results) else 2


if __name__ == "__main__":
    sys.exit(main())
