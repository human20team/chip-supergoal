import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class SgctlSemanticValidationTest(unittest.TestCase):
    def run_sgctl(self, *args):
        return subprocess.run([sys.executable, "scripts/sgctl.py", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_validate_contract_accepts_example(self):
        result = self.run_sgctl("validate-contract", "examples/brownfield-feature/CONTRACT.json", "--strict")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validate_phase_rejects_known_bad_fixture_with_stable_codes(self):
        result = self.run_sgctl("validate-phase-markdown", "tests/fixtures/v2-invalid/phase-99-of-1-rpd-mismatch.md", "--format", "json")
        self.assertNotEqual(result.returncode, 0)
        codes = {d["code"] for d in json.loads(result.stdout)}
        self.assertIn("SGV-PHASE-ORDINAL-OUT-OF-RANGE", codes)
        self.assertIn("SGV-PHASE-COUNT-MISMATCH", codes)
        self.assertIn("SGV-PHASE-RPD-MISMATCH", codes)

    def test_validate_loop_rejects_known_bad_fixture_with_stable_code(self):
        result = self.run_sgctl("validate-loop-design", "--instantiated", "tests/fixtures/v2-invalid/loop-one-word.md", "--format", "json")
        self.assertNotEqual(result.returncode, 0)
        codes = {d["code"] for d in json.loads(result.stdout)}
        self.assertIn("SGV-LOOP-WEAK-SECTION", codes)

    def test_validate_package_catches_launch_marker_drift(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            package = Path(td) / "package-drift"
            package.mkdir(parents=True, exist_ok=True)
            for name in ["THINKING.md", "LOOP_DESIGN.md", "ROADMAP.md", "STATE.md", "PROTOCOL.md", "LAUNCH_GOAL.md"]:
                (package / name).write_text(f"# {name}\n", encoding="utf-8")
            (package / "ROADMAP.md").write_text("SUPERGOAL_GOAL_BODY: wrong\n", encoding="utf-8")
            result = self.run_sgctl("validate-package", str(package), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SGV-PACKAGE-LAUNCH-MARKER", {d["code"] for d in json.loads(result.stdout)})

if __name__ == "__main__":
    unittest.main()
