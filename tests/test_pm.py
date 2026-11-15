"""The project-management calculators shipped in the library: critical path and earned value."""
import importlib.util
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

LIBRARY = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "..", "skills", "team", "library"))


def load(entry, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(LIBRARY, entry, "scripts", name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cpm = load("pm-schedule", "cpm")
evm = load("pm-control", "evm")


def network(*rows):
    return cpm.load([dict(zip(("id", "duration", "predecessors"), r)) for r in rows])


class CriticalPathTest(unittest.TestCase):
    def test_finish_to_start_network(self):
        acts = network(("A", "3", ""), ("B", "2", "A"), ("C", "4", "A"), ("D", "2", "B;C"))
        result = cpm.schedule(acts)
        self.assertEqual(result["end"], 9)
        self.assertEqual(result["path"], ["A", "C", "D"])
        self.assertEqual((acts["B"]["es"], acts["B"]["ls"], acts["B"]["total_float"]), (3, 5, 2))
        self.assertEqual(acts["B"]["free_float"], 2)
        self.assertFalse(acts["B"]["critical"])

    def test_free_float_differs_from_total_float(self):
        # B -> C chain beside A: B has total float 3 but no free float (C starts right after it)
        acts = network(("A", "6", ""), ("B", "1", ""), ("C", "2", "B"), ("D", "1", "A;C"))
        cpm.schedule(acts)
        self.assertEqual((acts["B"]["total_float"], acts["B"]["free_float"]), (3, 0))
        self.assertEqual((acts["C"]["total_float"], acts["C"]["free_float"]), (3, 3))

    def test_relation_types_and_lags(self):
        acts = network(("A", "4", ""), ("B", "3", "a:ss+1".replace("a", "A")), ("C", "2", "A:FF+2"),
                       ("D", "1", "A-1"), ("E", "2", "A:sf+3"))
        cpm.schedule(acts)
        self.assertEqual(acts["B"]["es"], 1)   # starts 1 after A starts
        self.assertEqual(acts["C"]["ef"], 6)   # finishes 2 after A finishes
        self.assertEqual(acts["D"]["es"], 3)   # 1-day lead on A's finish
        self.assertEqual(acts["E"]["ef"], 3)   # finishes 3 after A starts

    def test_three_point_estimates_and_probability(self):
        acts = cpm.load([{"id": "A", "optimistic": "2", "most_likely": "4", "pessimistic": "12"},
                         {"id": "B", "optimistic": "1", "most_likely": "2", "pessimistic": "3",
                          "predecessors": "A"}])
        result = cpm.schedule(acts)
        self.assertAlmostEqual(result["end"], 5 + 2)
        info = cpm.summary(acts, result, target=7)
        self.assertAlmostEqual(info["sigma"], ((10 / 6) ** 2 + (2 / 6) ** 2) ** 0.5)
        self.assertAlmostEqual(info["probability"], 0.5)

    def test_bad_networks_are_refused(self):
        with self.assertRaisesRegex(cpm.ScheduleError, "loop"):
            cpm.schedule(network(("A", "1", "B"), ("B", "1", "A")))
        with self.assertRaisesRegex(cpm.ScheduleError, "unknown predecessor"):
            network(("A", "1", "Z"))
        with self.assertRaisesRegex(cpm.ScheduleError, "duplicate"):
            network(("A", "1", ""), ("A", "2", ""))
        with self.assertRaisesRegex(cpm.ScheduleError, "bad predecessor"):
            network(("A", "1", ""), ("B", "1", "A:XX"))

    def test_cli_prints_table_and_gantt(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "plan.csv")
            with open(path, "w", encoding="utf-8") as f:
                f.write("id,name,duration,predecessors\nA,Design,3,\nB,Build,5,A\nM,Release,0,B\n")
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(cpm.main([path, "--gantt", "--start", "2026-01-05"]), 0)
        text = out.getvalue()
        self.assertIn("Critical path: A -> B -> M", text)
        self.assertIn("Build :crit, t2, 2026-01-08, 5d", text)
        self.assertIn("Release :crit, milestone, t3, 2026-01-13, 0d", text)


class EarnedValueTest(unittest.TestCase):
    def test_metrics_and_forecasts(self):
        m = evm.metrics(bac=10000, pv=5000, ev=4000, ac=5000)
        self.assertEqual((m["cv"], m["sv"]), (-1000, -1000))
        self.assertAlmostEqual(m["cpi"], 0.8)
        self.assertAlmostEqual(m["spi"], 0.8)
        self.assertAlmostEqual(m["eac_atypical"], 11000)
        self.assertAlmostEqual(m["eac_cpi"], 12500)
        self.assertAlmostEqual(m["eac_cpi_spi"], 5000 + 6000 / 0.64)
        self.assertAlmostEqual(m["etc_cpi"], 7500)
        self.assertAlmostEqual(m["vac"], -2500)
        self.assertAlmostEqual(m["tcpi_bac"], 1.2)
        self.assertAlmostEqual(m["tcpi_eac"], 0.8)
        self.assertIn("over budget by 1,000.00", evm.verdict(m)[0])
        self.assertTrue(any("rarely achievable" in v for v in evm.verdict(m)))

    def test_zero_actuals_give_no_index_instead_of_crashing(self):
        m = evm.metrics(bac=100, pv=0, ev=0, ac=0)
        self.assertIsNone(m["cpi"])
        self.assertIsNone(m["spi"])
        self.assertIsNone(m["eac_cpi"])
        self.assertIn("n/a", evm.report(m))

    def test_overspent_budget_has_no_tcpi(self):
        m = evm.metrics(bac=100, pv=100, ev=60, ac=120)
        self.assertIsNone(m["tcpi_bac"])
        self.assertTrue(any("already spent" in v for v in evm.verdict(m)))

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            evm.metrics(bac=0, pv=1, ev=1, ac=1)
        with self.assertRaises(ValueError):
            evm.metrics(bac=10, pv=-1, ev=1, ac=1)

    def test_cli_series(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "evm.csv")
            with open(path, "w", encoding="utf-8") as f:
                f.write("period,pv,ev,ac\nM1,1000,900,1000\nM2,2500,2000,2600\n")
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(evm.main(["--bac", "8000", path]), 0)
        self.assertIn("| M2 | 2,500.00 | 2,000.00 | 2,600.00 |", out.getvalue())
        self.assertIn("Latest period (M2)", out.getvalue())


if __name__ == "__main__":
    unittest.main()
