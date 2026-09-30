import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("continuity_bench", ROOT / "bench.py")
bench = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bench)


def czip_checkout():
    candidates = ([Path(os.environ["CZCG_CZIP_SOURCE"])]
                  if os.environ.get("CZCG_CZIP_SOURCE") else [])
    candidates += [ROOT.parent / "Czip", ROOT.parent.parent / "work" / "Czip"]
    return next((path for path in candidates if (path / "hkp.py").is_file()), None)


class DatasetTests(unittest.TestCase):
    def test_determinism_and_gold_evidence(self):
        first = bench.make_dataset(44, 4)
        second = bench.make_dataset(44, 4)
        self.assertEqual(first["messages"], second["messages"])
        self.assertEqual(first["probes"], second["probes"])
        self.assertEqual(len(first["probes"]), 8)
        self.assertGreater(len(first["messages"]), 40)
        for probe in first["probes"]:
            for index in probe["evidence"]:
                self.assertGreaterEqual(index, 0)
                self.assertLess(index, len(first["messages"]))

    def test_answer_and_provenance_scored_separately(self):
        probe = {"answer": "X-123", "evidence": [3, 9], "category": "two_hop"}
        self.assertEqual(bench.grade(probe, "X-123", [3])["correct"], True)
        self.assertEqual(bench.grade(probe, "X-123", [3])["grounded"], False)
        self.assertEqual(bench.grade(probe, "X-123", [3, 9])["grounded"], True)
        unknown = {"answer": "UNKNOWN", "evidence": [], "category": "abstention"}
        self.assertTrue(bench.grade(unknown, "UNKNOWN", [])["grounded"])
        self.assertTrue(bench.grade(unknown, "UNKNOWN", [1])["grounded"])

    def test_short_answer_accepts_explanation_after_value(self):
        self.assertTrue(bench._answer_matches("ap-southeast-2 (supersedes draft)",
                                              "ap-southeast-2"))
        self.assertTrue(bench._answer_matches("UNKNOWN — no PIN was given", "UNKNOWN"))
        self.assertFalse(bench._answer_matches("NOPE", "NO"))

    def test_tail_cannot_cite_unseen_evidence(self):
        data = bench.make_dataset(44, 4)
        probe = next(p for p in data["probes"] if p["id"] == "early_exact")

        def fake_chat(_):
            return json.dumps({"action": "answer", "answer": "UNKNOWN", "evidence": []}), {}

        result = bench.run_probe(probe, data["messages"], "tail", fake_chat,
                                 tail_messages=4)
        self.assertFalse(result["correct"])
        self.assertEqual(result["tool_calls"], 0)

    def test_czip_full_pack_search_and_read(self):
        czip_source = czip_checkout()
        if czip_source is None:
            self.skipTest("provide the Czip checkout for integration testing")
        engine = bench.load_czip(str(czip_source))
        data = bench.make_dataset(44, 4)
        with tempfile.TemporaryDirectory() as temporary:
            stats = engine.sikistir(data["messages"], str(Path(temporary) / "case"),
                                    mod="eksiksiz")
            self.assertTrue(stats["ok"])
            probe = next(p for p in data["probes"] if p["id"] == "early_exact")
            matches = engine.paket_ara(stats["yol"], "verified rollback code")
            self.assertIn(probe["evidence"][0], [m["i"] for m in matches])
            message = engine.mesaj_araligi(stats["yol"], str(probe["evidence"][0]))[0]
            self.assertIn(probe["answer"], message["icerik"])

            replies = iter([
                {"action": "search", "query": "verified rollback code"},
                {"action": "read", "index": probe["evidence"][0]},
                {"action": "answer", "answer": probe["answer"],
                 "evidence": probe["evidence"]},
            ])

            def fake_chat(_):
                return json.dumps(next(replies)), {"prompt_tokens": 10,
                                                   "completion_tokens": 5}

            result = bench.run_probe(probe, data["messages"], "czip", fake_chat,
                                     engine, stats["yol"])
            self.assertTrue(result["grounded"])
            self.assertTrue(result["evidence_read"])
            self.assertEqual(result["tool_calls"], 2)

            forged = iter([{"action": "answer", "answer": probe["answer"],
                            "evidence": probe["evidence"]}])
            ungrounded = bench.run_probe(probe, data["messages"], "czip",
                                         lambda _: (json.dumps(next(forged)), {}),
                                         engine, stats["yol"], tool_budget=0)
            self.assertTrue(ungrounded["correct"])
            self.assertFalse(ungrounded["grounded"])

    def test_cli_writes_auditable_report_without_claiming_success(self):
        czip_source = czip_checkout()
        if czip_source is None:
            self.skipTest("provide the Czip checkout for integration testing")
        with tempfile.TemporaryDirectory() as temporary:
            dataset_path = Path(temporary) / "case.json"
            output_dir = Path(temporary) / "run"
            dataset_path.write_text(json.dumps(bench.make_dataset(44, 4)), encoding="utf-8")

            def fake_endpoint(*_):
                return json.dumps({"action": "answer", "answer": "UNKNOWN",
                                   "evidence": []}), {"prompt_tokens": 10,
                                                    "completion_tokens": 5}

            with patch.object(bench, "_post_chat", side_effect=fake_endpoint):
                code = bench.main(["run", "--dataset", str(dataset_path),
                                   "--out-dir", str(output_dir), "--model", "mock",
                                   "--czip-source", str(czip_source),
                                   "--arms", "czip", "tail"])
            self.assertEqual(code, 0)
            report = (output_dir / "report.md").read_text(encoding="utf-8")
            record = json.loads((output_dir / "results.json").read_text(encoding="utf-8"))
            self.assertIn("Czip full-pack preparation", report)
            self.assertEqual(record["summary"]["czip"]["completed"], 8)
            self.assertLess(record["summary"]["czip"]["accuracy"], 1)
            self.assertNotIn("yol", record["pack_stats"])


if __name__ == "__main__":
    unittest.main()
