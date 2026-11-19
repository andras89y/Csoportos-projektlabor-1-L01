"""Alapellenőrzés az L01 demo programjához; külső tesztkeretrendszer nélkül."""

import csv
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_Program"))
import main  # noqa: E402


class MeshChecks(unittest.TestCase):
    def test_built_in_models_have_four_detected_holes(self):
        for generator in (main.generate_torus_model, main.generate_sphere_model):
            with self.subTest(model=generator.__name__):
                intact, damaged = generator()
                loops, open_edges, _ = main.HoleDetector.find_boundary_loops(damaged)
                self.assertEqual(len(loops), 4)
                self.assertGreater(open_edges, 0)
                self.assertGreater(len(intact.faces), len(damaged.faces))

    def test_all_methods_close_test_boundaries(self):
        methods = (main.HoleFiller.fill_centroid_fan,
                   main.HoleFiller.fill_ear_clipping,
                   main.HoleFiller.fill_multiring_laplacian,
                   main.HoleFiller.fill_multiring_biharmonic_tps)
        for generator in (main.generate_torus_model, main.generate_sphere_model):
            original, damaged = generator()
            for method in methods:
                with self.subTest(model=generator.__name__, method=method.__name__):
                    repaired = method(damaged)
                    met = main.evaluate_repair(original, damaged, repaired, 0.0)
                    self.assertEqual(met['remaining_holes'], 0)
                    self.assertEqual(met['open_edges'], 0)
                    self.assertEqual(met['new_faces'], len(repaired.faces)-len(damaged.faces))
                    self.assertTrue(math.isfinite(met['rmse']))
                    self.assertTrue(math.isfinite(met['hausdorff']))

    def test_metrics_are_centroid_nearest_neighbor_measurements(self):
        original, damaged = main.generate_torus_model()
        repaired = main.HoleFiller.fill_centroid_fan(damaged)
        metrics = main.evaluate_repair(original, damaged, repaired, 0.0)
        added_faces = repaired.faces[len(damaged.faces):]
        added_centers = repaired.vertices[added_faces].mean(axis=1)
        original_centers = original.vertices[original.faces].mean(axis=1)
        from numpy.linalg import norm
        near = norm(added_centers[:, None, :] - original_centers[None, :, :], axis=2).min(axis=1)
        self.assertAlmostEqual(metrics['rmse'], math.sqrt(float((near ** 2).mean())), places=10)
        self.assertAlmostEqual(metrics['hausdorff'], float(near.max()), places=10)


class EndToEndChecks(unittest.TestCase):
    def test_full_run_exports_portable_results(self):
        # A saját projektet nem írjuk tele a teszthez: izolált munkakönyvtárban fut.
        with tempfile.TemporaryDirectory(prefix='l01_3d_test_') as tmp:
            copied = Path(tmp)/'main.py'
            shutil.copyfile(ROOT/'01_Program'/'main.py', copied)
            env = os.environ.copy()
            env['MPLBACKEND'] = 'Agg'
            result = subprocess.run([sys.executable, str(copied)], capture_output=True,
                                    text=True, encoding='utf-8', errors='replace',
                                    env=env, timeout=180)
            self.assertEqual(result.returncode, 0, msg=result.stdout[-2500:]+'\n'+result.stderr[-2500:])
            out = Path(tmp)/'Lyukkitoltes_Eredmenyek'
            self.assertTrue(out.is_dir())
            self.assertEqual(len(list(out.glob('*.obj'))), 12)
            self.assertEqual(len(list(out.glob('*.png'))), 2)
            self.assertEqual(len(list(out.glob('*.csv'))), 1)
            self.assertEqual(len(list(out.glob('*.html'))), 1)
            self.assertEqual(len(list(out.glob('*.txt'))), 1)

            html=(out/'Meresi_Jegyzokonyv.html').read_text(encoding='utf-8')
            images=re.findall(r'<img src="([^"]+)"', html)
            self.assertEqual(len(images), 2)
            for name in images:
                self.assertEqual(Path(name).name, name)
                self.assertTrue((out/name).is_file())
            with (out/'meresi_eredmenyek.csv').open(encoding='utf-8-sig', newline='') as f:
                rows=list(csv.DictReader(f, delimiter=';'))
            self.assertEqual(len(rows), 8)
            self.assertTrue(all(row['Maradek_lyukak']=='0' and row['Nyitott_elek']=='0' for row in rows))
            self.assertTrue(all(float(row['RMSE_hiba']) > 0 for row in rows))
            txt=(out/'Meresi_Jegyzokonyv.txt').read_text(encoding='utf-8')
            self.assertNotIn(tmp, txt)


if __name__ == '__main__':
    unittest.main()
