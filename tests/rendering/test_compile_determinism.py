import filecmp
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class CompileDeterminismTest(unittest.TestCase):
    def compile_to(self, out: Path):
        result = subprocess.run([sys.executable, "scripts/sgctl.py", "compile", "examples/brownfield-feature/CONTRACT.json", "--out", str(out)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_compile_outputs_required_files_and_single_launch_marker(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "sg"
            self.compile_to(out)
            for rel in ["CONTRACT.json", "MANIFEST.json", "THINKING.md", "LOOP_DESIGN.md", "ROADMAP.md", "STATE.md", "PROTOCOL.md", "LAUNCH_GOAL.md", "phases/phase-01.md"]:
                self.assertTrue((out / rel).is_file(), rel)
            hits = []
            for p in out.rglob("*.md"):
                for i, line in enumerate(p.read_text().splitlines(), 1):
                    if line.startswith("SUPERGOAL_GOAL_BODY:"):
                        hits.append(f"{p.relative_to(out)}:{i}")
            self.assertEqual(len(hits), 1)
            self.assertTrue(hits[0].startswith("LAUNCH_GOAL.md:"))

    def test_recompile_is_byte_stable_except_out_path_in_launch_goal(self):
        with tempfile.TemporaryDirectory() as td:
            out1 = Path(td) / "a"; out2 = Path(td) / "b"
            self.compile_to(out1); self.compile_to(out2)
            comparable = ["CONTRACT.json", "THINKING.md", "LOOP_DESIGN.md", "ROADMAP.md", "STATE.md", "PROTOCOL.md", "phases/phase-01.md"]
            for rel in comparable:
                self.assertTrue(filecmp.cmp(out1 / rel, out2 / rel, shallow=False), rel)

if __name__ == "__main__":
    unittest.main()
