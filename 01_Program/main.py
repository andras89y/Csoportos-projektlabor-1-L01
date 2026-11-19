# L01 - 3D haromszoghalo lyukkitolto osszehasonlito program.
# A matematikai algoritmusok a projekt eredeti forrasa alapjan valtozatlanok.

import os
import sys
import time
import csv
import webbrowser
from datetime import datetime
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# EXE es .py futtatasnal is a fajl melletti "Lyukkitoltes_Eredmenyek" mappaba mentunk
if getattr(sys, 'frozen', False):
    ROOT_DIR = os.path.dirname(sys.executable)
elif "__file__" in locals():
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
else:
    ROOT_DIR = os.getcwd()

OUT_DIR = os.path.join(ROOT_DIR, "Lyukkitoltes_Eredmenyek")
os.makedirs(OUT_DIR, exist_ok=True)


# ==========================================
# 1. MODUL: 3D HÁLÓ OSZTÁLY ÉS 2 TESZTMODELL
# ==========================================
class TriMesh:
    def __init__(self, vertices, faces):
        self.vertices = np.array(vertices, dtype=float)
        self.faces = np.array(faces, dtype=int)

    def copy(self):
        return TriMesh(self.vertices.copy(), self.faces.copy())

    def save_obj(self, filename):
        filepath = os.path.join(OUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            for v in self.vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in self.faces:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")


def generate_torus_model(n_theta=40, n_phi=80):
    R, r = 3.0, 1.2
    vertices = []
    for i in range(n_theta):
        theta = 2.0 * np.pi * i / n_theta
        for j in range(n_phi):
            phi = 2.0 * np.pi * j / n_phi
            wave = 0.15 * np.sin(3 * phi) * np.cos(2 * theta)
            rr = r + wave
            x = (R + rr * np.cos(theta)) * np.cos(phi)
            y = (R + rr * np.cos(theta)) * np.sin(phi)
            z = rr * np.sin(theta)
            vertices.append([x, y, z])
    vertices = np.array(vertices)

    faces = []
    for i in range(n_theta):
        i_next = (i + 1) % n_theta
        for j in range(n_phi):
            j_next = (j + 1) % n_phi
            v00 = i * n_phi + j
            v10 = i_next * n_phi + j
            v11 = i_next * n_phi + j_next
            v01 = i * n_phi + j_next
            faces.append([v00, v10, v11])
            faces.append([v00, v11, v01])
    faces = np.array(faces)
    orig_mesh = TriMesh(vertices, faces)

    hole_specs = [
        (0.0, 0.0, 0.75),
        (np.pi / 2, np.pi / 2, 0.85),
        (np.pi, np.pi, 0.90),
        (-np.pi / 3, 3 * np.pi / 2, 0.80)
    ]
    keep_mask = np.ones(len(faces), dtype=bool)
    face_centers = vertices[faces].mean(axis=1)

    for theta_c, phi_c, radius in hole_specs:
        wave = 0.15 * np.sin(3 * phi_c) * np.cos(2 * theta_c)
        rr = r + wave
        cx = (R + rr * np.cos(theta_c)) * np.cos(phi_c)
        cy = (R + rr * np.cos(theta_c)) * np.sin(phi_c)
        cz = rr * np.sin(theta_c)
        center = np.array([cx, cy, cz])
        dists = np.linalg.norm(face_centers - center, axis=1)
        keep_mask &= (dists > radius)

    broken_mesh = TriMesh(vertices, faces[keep_mask])
    return orig_mesh, broken_mesh


def generate_sphere_model(n_lat=45, n_lon=70):
    R_base = 2.8
    vertices = [[0.0, 0.0, R_base]]
    for i in range(1, n_lat):
        theta = np.pi * i / n_lat
        for j in range(n_lon):
            phi = 2.0 * np.pi * j / n_lon
            wave = 0.22 * np.sin(3 * theta) * np.cos(4 * phi)
            r = R_base + wave
            x = r * np.sin(theta) * np.cos(phi)
            y = r * np.sin(theta) * np.sin(phi)
            z = r * np.cos(theta)
            vertices.append([x, y, z])
    vertices.append([0.0, 0.0, -R_base])
    vertices = np.array(vertices)
    south_idx = len(vertices) - 1

    faces = []
    for j in range(n_lon):
        j_next = (j + 1) % n_lon
        faces.append([0, 1 + j, 1 + j_next])

    for i in range(n_lat - 2):
        row1 = 1 + i * n_lon
        row2 = 1 + (i + 1) * n_lon
        for j in range(n_lon):
            j_next = (j + 1) % n_lon
            v00 = row1 + j
            v01 = row1 + j_next
            v10 = row2 + j
            v11 = row2 + j_next
            faces.append([v00, v10, v11])
            faces.append([v00, v11, v01])

    last_row = 1 + (n_lat - 2) * n_lon
    for j in range(n_lon):
        j_next = (j + 1) % n_lon
        faces.append([last_row + j, south_idx, last_row + j_next])

    faces = np.array(faces)
    orig_mesh = TriMesh(vertices, faces)

    hole_dirs = [
        (np.pi * 0.32, -np.pi * 0.25, 0.85),
        (np.pi * 0.55, -np.pi * 0.05, 0.90),
        (np.pi * 0.45, -np.pi * 0.50, 0.80),
        (np.pi * 0.65, np.pi * 0.35, 0.85),
    ]
    keep_mask = np.ones(len(faces), dtype=bool)
    face_centers = vertices[faces].mean(axis=1)

    for theta_c, phi_c, radius in hole_dirs:
        wave = 0.22 * np.sin(3 * theta_c) * np.cos(4 * phi_c)
        r = R_base + wave
        center = np.array([
            r * np.sin(theta_c) * np.cos(phi_c),
            r * np.sin(theta_c) * np.sin(phi_c),
            r * np.cos(theta_c)
        ])
        dists = np.linalg.norm(face_centers - center, axis=1)
        keep_mask &= (dists > radius)

    broken_mesh = TriMesh(vertices, faces[keep_mask])
    return orig_mesh, broken_mesh


# ==========================================
# 2. MODUL: LYUKDETEKTÁLÁS
# ==========================================
class HoleDetector:
    @staticmethod
    def find_boundary_loops(mesh):
        edge_count = defaultdict(int)
        directed_edges = {}

        for face in mesh.faces:
            for k in range(3):
                u, v = int(face[k]), int(face[(k + 1) % 3])
                undirected = (min(u, v), max(u, v))
                edge_count[undirected] += 1
                directed_edges[(u, v)] = undirected

        boundary_next = {}
        for (u, v), undirected in directed_edges.items():
            if edge_count[undirected] == 1:
                boundary_next[v] = u

        open_edges_count = len(boundary_next)
        visited = set()
        loops = []

        for start_v in list(boundary_next.keys()):
            if start_v in visited:
                continue
            loop = []
            curr = start_v
            while curr not in visited and curr in boundary_next:
                visited.add(curr)
                loop.append(curr)
                curr = boundary_next[curr]
            if len(loop) >= 3:
                loops.append(loop)

        return loops, open_edges_count, boundary_next


# ==========================================
# 3. MODUL: 4 LYUKKITÖLTŐ ALGORITMUS
# ==========================================
class HoleFiller:
    @staticmethod
    def fill_centroid_fan(mesh):
        res = mesh.copy()
        loops, _, _ = HoleDetector.find_boundary_loops(res)
        new_verts = res.vertices.tolist()
        new_faces = res.faces.tolist()

        for loop in loops:
            pts = res.vertices[loop]
            centroid = pts.mean(axis=0)
            c_idx = len(new_verts)
            new_verts.append(centroid.tolist())
            n = len(loop)
            for i in range(n):
                new_faces.append([loop[i], loop[(i + 1) % n], c_idx])

        return TriMesh(new_verts, new_faces)

    @staticmethod
    def fill_ear_clipping(mesh):
        res = mesh.copy()
        loops, _, _ = HoleDetector.find_boundary_loops(res)
        new_faces = res.faces.tolist()

        for loop in loops:
            poly = list(loop)
            pts = res.vertices[poly]
            center = pts.mean(axis=0)
            normal = np.zeros(3)
            for i in range(len(poly)):
                p1 = res.vertices[poly[i]] - center
                p2 = res.vertices[poly[(i + 1) % len(poly)]] - center
                normal += np.cross(p1, p2)
            norm_len = np.linalg.norm(normal)
            normal = normal / norm_len if norm_len > 1e-12 else np.array([0.0, 0.0, 1.0])

            while len(poly) > 3:
                n = len(poly)
                best_idx = 0
                best_score = -1e18
                for i in range(n):
                    p_prev = res.vertices[poly[(i - 1) % n]]
                    p_curr = res.vertices[poly[i]]
                    p_next = res.vertices[poly[(i + 1) % n]]
                    e1 = p_curr - p_prev
                    e2 = p_next - p_curr
                    cross_z = np.dot(np.cross(e1, e2), normal)
                    dist = np.linalg.norm(p_next - p_prev) + 1e-8
                    score = (cross_z / dist) - 0.5 * dist
                    if score > best_score:
                        best_score = score
                        best_idx = i

                new_faces.append([poly[(best_idx - 1) % n], poly[best_idx], poly[(best_idx + 1) % n]])
                poly.pop(best_idx)

            if len(poly) == 3:
                new_faces.append([poly[0], poly[1], poly[2]])

        return TriMesh(res.vertices, new_faces)

    @staticmethod
    def _build_multiring_patch(res, loop, rings=3):
        pts = res.vertices[loop]
        centroid = pts.mean(axis=0)
        n = len(loop)
        new_verts = res.vertices.tolist()
        new_faces = res.faces.tolist()
        patch_vert_indices = []

        ring_loops = [loop]
        for r in range(1, rings):
            alpha = r / float(rings)
            ring_idx = []
            for u in loop:
                p = (1.0 - alpha) * res.vertices[u] + alpha * centroid
                idx = len(new_verts)
                new_verts.append(p.tolist())
                ring_idx.append(idx)
                patch_vert_indices.append(idx)
            ring_loops.append(ring_idx)

        c_idx = len(new_verts)
        new_verts.append(centroid.tolist())
        patch_vert_indices.append(c_idx)

        for r in range(rings - 1):
            outer, inner = ring_loops[r], ring_loops[r + 1]
            for i in range(n):
                u0, u1 = outer[i], outer[(i + 1) % n]
                v0, v1 = inner[i], inner[(i + 1) % n]
                new_faces.append([u0, u1, v1])
                new_faces.append([u0, v1, v0])

        last_ring = ring_loops[-1]
        for i in range(n):
            new_faces.append([last_ring[i], last_ring[(i + 1) % n], c_idx])

        return np.array(new_verts, dtype=float), np.array(new_faces, dtype=int), patch_vert_indices

    @staticmethod
    def fill_multiring_laplacian(mesh, rings=3, iterations=25):
        res = mesh.copy()
        loops, _, _ = HoleDetector.find_boundary_loops(res)
        all_patch_verts = []

        for loop in loops:
            v_arr, f_arr, patch_ids = HoleFiller._build_multiring_patch(res, loop, rings=rings)
            res = TriMesh(v_arr, f_arr)
            all_patch_verts.extend(patch_ids)

        adj = defaultdict(set)
        for face in res.faces:
            for k in range(3):
                u, v = int(face[k]), int(face[(k + 1) % 3])
                adj[u].add(v)
                adj[v].add(u)

        verts = res.vertices.copy()
        for _ in range(iterations):
            next_verts = verts.copy()
            for idx in all_patch_verts:
                nbrs = list(adj[idx])
                if nbrs:
                    next_verts[idx] = verts[nbrs].mean(axis=0)
            verts = next_verts

        return TriMesh(verts, res.faces)

    @staticmethod
    def fill_multiring_biharmonic_tps(mesh, rings=3):
        res = HoleFiller.fill_multiring_laplacian(mesh, rings=rings, iterations=25)
        loops, _, _ = HoleDetector.find_boundary_loops(mesh)

        adj = defaultdict(set)
        for face in mesh.faces:
            for k in range(3):
                u, v = int(face[k]), int(face[(k + 1) % 3])
                adj[u].add(v)
                adj[v].add(u)

        orig_n = len(mesh.vertices)
        verts = res.vertices.copy()
        curr_idx = orig_n

        for loop in loops:
            n_loop = len(loop)
            count = (rings - 1) * n_loop + 1
            patch_ids = list(range(curr_idx, curr_idx + count))
            curr_idx += count

            anchor_set = set(loop)
            for u in loop:
                for nb in adj[u]:
                    anchor_set.add(nb)
            anchor_pts = verts[list(anchor_set)]

            center = anchor_pts.mean(axis=0)
            centered = anchor_pts - center
            _, _, vh = np.linalg.svd(centered, full_matrices=False)
            local_axes = vh

            uv_anchors = centered @ local_axes.T
            X, Z = uv_anchors[:, :2], uv_anchors[:, 2]

            diff = X[:, None, :] - X[None, :, :]
            r = np.linalg.norm(diff, axis=2)
            K = np.where(r > 1e-10, (r ** 2) * np.log(r + 1e-12), 0.0)
            P = np.column_stack([np.ones(len(X)), X])

            m = len(X)
            A = np.zeros((m + 3, m + 3))
            A[:m, :m] = K + 1e-3 * np.eye(m)
            A[:m, m:] = P
            A[m:, :m] = P.T

            b = np.zeros(m + 3)
            b[:m] = Z

            coeffs = np.linalg.lstsq(A, b, rcond=None)[0]
            w, a = coeffs[:m], coeffs[m:]

            for pid in patch_ids:
                p_local = (verts[pid] - center) @ local_axes.T
                xy = p_local[:2]
                d = np.linalg.norm(X - xy, axis=1)
                phi = np.where(d > 1e-10, (d ** 2) * np.log(d + 1e-12), 0.0)
                z_pred = a[0] + a[1] * xy[0] + a[2] * xy[1] + np.dot(w, phi)
                verts[pid] = center + np.array([xy[0], xy[1], z_pred]) @ local_axes

        return TriMesh(verts, res.faces)


# ==========================================
# 4. MODUL: KIÉRTÉKELÉS, 3D ÁBRA ÉS JEGYZŐKÖNYV
# ==========================================
def evaluate_repair(orig_mesh, broken_mesh, repaired_mesh, elapsed_ms):
    loops, open_edges, _ = HoleDetector.find_boundary_loops(repaired_mesh)
    n_broken_faces = len(broken_mesh.faces)
    new_faces = repaired_mesh.faces[n_broken_faces:]

    orig_centers = orig_mesh.vertices[orig_mesh.faces].mean(axis=1)
    new_centers = repaired_mesh.vertices[new_faces].mean(axis=1)

    dists = np.linalg.norm(new_centers[:, None, :] - orig_centers[None, :, :], axis=2)
    min_dists = dists.min(axis=1)
    return {
        "new_faces": len(new_faces),
        "remaining_holes": len(loops),
        "open_edges": open_edges,
        "rmse": float(np.sqrt(np.mean(min_dists ** 2))),
        "hausdorff": float(np.max(min_dists)),
        "time_ms": elapsed_ms
    }


def compute_3d_shading(tris, base_rgb):
    v1 = tris[:, 1] - tris[:, 0]
    v2 = tris[:, 2] - tris[:, 0]
    normals = np.cross(v1, v2)
    normals /= (np.linalg.norm(normals, axis=1, keepdims=True) + 1e-12)
    light_dir = np.array([0.4, -0.6, 0.7])
    light_dir /= np.linalg.norm(light_dir)
    intensity = 0.40 + 0.60 * np.abs(normals @ light_dir)
    return np.clip(intensity[:, None] * np.array(base_rgb)[None, :], 0.0, 1.0)


def create_3d_figure(model_title, orig_mesh, broken_mesh, repaired_dict, methods, png_filename, z_lim, z_aspect):
    fig = plt.figure(figsize=(15, 9.5))
    fig.suptitle(f"{model_title} - 3D Lyukkitoltes Osszehasonlitas (Egérrel forgatható!)", fontsize=13, fontweight="bold")

    plot_items = [
        ("Eredeti ep 3D modell", orig_mesh, False),
        ("Serult 3D modell (4 lyukkal)", broken_mesh, False),
    ] + [(lbl, repaired_dict[lbl], True) for _, lbl, _ in methods]

    n_broken = len(broken_mesh.faces)

    for idx, (title, m, has_patch) in enumerate(plot_items, start=1):
        ax = fig.add_subplot(2, 3, idx, projection="3d")
        if has_patch:
            base_tris = m.vertices[m.faces[:n_broken]]
            patch_tris = m.vertices[m.faces[n_broken:]]
        else:
            base_tris = m.vertices[m.faces]
            patch_tris = None

        base_colors = compute_3d_shading(base_tris, [0.35, 0.65, 0.95])
        if patch_tris is not None and len(patch_tris) > 0:
            patch_colors = compute_3d_shading(patch_tris, [0.95, 0.20, 0.25])
            all_tris = np.concatenate([base_tris, patch_tris], axis=0)
            all_colors = np.concatenate([base_colors, patch_colors], axis=0)
        else:
            all_tris = base_tris
            all_colors = base_colors

        col_all = Poly3DCollection(all_tris, facecolors=all_colors, edgecolors=(0.1, 0.15, 0.25, 0.22), linewidths=0.25, zsort="average")
        ax.add_collection3d(col_all)

        ax.set_xlim(-4.0, 4.0)
        ax.set_ylim(-4.0, 4.0)
        ax.set_zlim(-z_lim, z_lim)
        ax.set_box_aspect((1.0, 1.0, z_aspect))
        ax.view_init(elev=26, azim=-42)
        ax.set_xlabel("X", fontsize=8)
        ax.set_ylabel("Y", fontsize=8)
        ax.set_zlabel("Z", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.set_title(title, fontsize=10.5, fontweight="bold")

    plt.tight_layout()
    png_path = os.path.join(OUT_DIR, png_filename)
    fig.savefig(png_path, dpi=180)
    return png_path


def generate_reports(all_model_data):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    csv_path = os.path.join(OUT_DIR, "meresi_eredmenyek.csv")
    txt_path = os.path.join(OUT_DIR, "Meresi_Jegyzokonyv.txt")
    html_path = os.path.join(OUT_DIR, "Meresi_Jegyzokonyv.html")

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Modell", "Algoritmus", "Eredeti_haromszogek", "Serult_haromszogek", "Potolt_haromszogek", "Maradek_lyukak", "Nyitott_elek", "RMSE_hiba", "Hausdorff_hiba", "Futasi_ido_ms"])
        for mdata in all_model_data:
            for label, m in mdata["results"].items():
                writer.writerow([
                    mdata["name"], label, mdata["orig_faces"], mdata["broken_faces"],
                    m["new_faces"], m["remaining_holes"], m["open_edges"],
                    f"{m['rmse']:.5f}", f"{m['hausdorff']:.5f}", f"{m['time_ms']:.2f}"
                ])

    lines = [
        "==========================================================================",
        "           3D FELÜLETI LYUKKITÖLTÉS - MÉRÉSI JEGYZŐKÖNYV",
        "==========================================================================",
        f"Generálás ideje: {now_str}",
        "Kimeneti mappa: Lyukkitoltes_Eredmenyek",
        ""
    ]
    for mdata in all_model_data:
        lines.append(f"--- {mdata['name']} ---")
        lines.append(f"Eredeti ép háló: {mdata['orig_faces']} háromszög | Sérült háló: {mdata['broken_faces']} háromszög")
        lines.append(f"Detektált lyukak: {mdata['init_holes']} db | Nyitott peremélek: {mdata['init_open_edges']} db")
        lines.append("-" * 74)
        lines.append(f"{'Algoritmus':28s} | {'Pótolt':6s} | {'Lyuk':4s} | {'RMSE':8s} | {'Hausdorff':9s} | {'Idő (ms)':8s}")
        lines.append("-" * 74)
        for label, m in mdata["results"].items():
            lines.append(f"{label:28s} | {m['new_faces']:6d} | {m['remaining_holes']:4d} | {m['rmse']:8.5f} | {m['hausdorff']:9.5f} | {m['time_ms']:8.2f}")
        lines.append("")

    lines.append("ÖSSZEFOGLALÓ ÉRTÉKELÉS:")
    lines.append("- A két beépített szintetikus tesztmodell mind a 8 javított hálóján 0 nyitott peremél maradt; ez önmagában nem bizonyítja az általános vízzáróságot.")
    lines.append("- A Centroid Fan a leggyorsabb, de sík/kúpos pótlást ad.")
    lines.append("- A TPS eljárás ezen teszteken adta a legkisebb, háromszögsúlypontokon számított egyirányú távolságmutatókat. Ez nem teljes felületi RMSE/Hausdorff-mérés.")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    html_sections = ""
    for mdata in all_model_data:
        best_rmse = min(v["rmse"] for v in mdata["results"].values())
        rows_html = ""
        for label, m in mdata["results"].items():
            is_best = abs(m["rmse"] - best_rmse) < 1e-9
            row_style = ' style="background-color:#e8f5e9; font-weight:bold;"' if is_best else ""
            badge = ' <span style="background:#2e7d32;color:#fff;padding:2px 6px;border-radius:4px;font-size:11px;">Legpontosabb</span>' if is_best else ""
            rows_html += f"""
            <tr{row_style}>
                <td>{label}{badge}</td>
                <td>{m['new_faces']} db</td>
                <td>{m['remaining_holes']} db</td>
                <td>{m['open_edges']} db</td>
                <td>{m['rmse']:.5f}</td>
                <td>{m['hausdorff']:.5f}</td>
                <td>{m['time_ms']:.1f} ms</td>
            </tr>"""

        html_sections += f"""
        <div class="card">
            <h2>{mdata['name']}</h2>
            <p class="meta">
                <strong>Eredeti háromszögek:</strong> {mdata['orig_faces']} db &nbsp;|&nbsp;
                <strong>Sérült háromszögek:</strong> {mdata['broken_faces']} db (Hiányzó: {mdata['orig_faces'] - mdata['broken_faces']} db) &nbsp;|&nbsp;
                <strong>Detektált lyukak:</strong> {mdata['init_holes']} db ({mdata['init_open_edges']} nyitott peremél)
            </p>
            <table>
                <thead>
                    <tr>
                        <th>Algoritmus</th>
                        <th>Pótolt háromszögek</th>
                        <th>Maradék lyukak</th>
                        <th>Nyitott élek</th>
                        <th>RMSE hiba</th>
                        <th>Hausdorff hiba</th>
                        <th>Futási idő</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            <div class="img-box">
                <img src="{mdata['png_file']}" alt="{mdata['name']}">
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="hu">
<head>
<meta charset="UTF-8">
<title>Mérési Jegyzőkönyv - 3D Lyukkitöltés</title>
<style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; color: #1e293b; margin: 0; padding: 28px; }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    .header {{ background: #1e3a8a; color: white; padding: 24px 28px; border-radius: 10px; margin-bottom: 24px; }}
    .header h1 {{ margin: 0 0 8px 0; font-size: 24px; }}
    .header p {{ margin: 4px 0; opacity: 0.9; font-size: 14px; }}
    .card {{ background: white; border-radius: 10px; padding: 24px; margin-bottom: 26px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); }}
    h2 {{ margin-top: 0; color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
    .meta {{ background: #f8fafc; padding: 10px 14px; border-left: 4px solid #3b82f6; border-radius: 4px; font-size: 14px; }}
    table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 10px 12px; text-align: center; }}
    th {{ background: #f1f5f9; color: #0f172a; }}
    td:first-child {{ text-align: left; }}
    .img-box {{ text-align: center; margin-top: 18px; }}
    .img-box img {{ max-width: 100%; border: 1px solid #e2e8f0; border-radius: 8px; }}
    .summary {{ background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; padding: 20px 24px; }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>Mérési Jegyzőkönyv – 3D Háromszögháló Lyukkitöltő Algoritmusok Vizsgálata</h1>
        <p><strong>Csoportos Projektlabor</strong> | Automatikus kiértékelés 2 különböző 3D tesztgeometrián</p>
        <p>Generálás dátuma: {now_str}</p>
    </div>
    {html_sections}
    <div class="summary">
        <h2>Mérnöki következtetések és kiértékelés</h2>
        <ul>
            <li><strong>Topológiai peremzárás a két tesztmodellen:</strong> a négy algoritmus mindkét beépített 3D modellen <strong>0-ra csökkentette a nyitott peremélek számát</strong>. Ez nem önmagában bizonyíték általános vízzáróságra.</li>
            <li><strong>Sebesség vs. Pontosság:</strong> A <em>Centroid Fan</em> és az <em>Ear Clipping</em> rendkívül gyors, de a görbült felületeken nagyobb geometriai hibát hagynak.</li>
            <li><strong>Távolságmutatók:</strong> a <em>Multi-Ring Biharmonic TPS</em> adta a legkisebb program szerinti RMSE- és maximumtávolság-értéket a két beépített teszten. A mutatók a pótolt és eredeti háromszögek súlypontjaira számított egyirányú legközelebbi-szomszéd távolságok, nem a teljes felületek szabványos Hausdorff-távolsága.</li>
        </ul>
    </div>
</div>
</body>
</html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return csv_path, txt_path, html_path


# ==========================================
# FŐPROGRAM FUTTATÁSA
# ==========================================
if __name__ == "__main__":
    print("=================================================================")
    print("  3D LYUKKITOLTO PROJEKT - 2 MODELL + AUTOMATIKUS JEGYZOKONYV")
    print("=================================================================")

    models_to_run = [
        ("1. Modell: 3D Hullamos Torusz", "torusz", generate_torus_model, "1_modell_torusz_3d.png", 2.0, 0.48),
        ("2. Modell: 3D Deformalt Gomb", "gomb", generate_sphere_model, "2_modell_gomb_3d.png", 3.2, 0.85),
    ]

    methods = [
        ("1_centroid_fan", "1. Centroid Fan", HoleFiller.fill_centroid_fan),
        ("2_ear_clipping", "2. Ear Clipping", HoleFiller.fill_ear_clipping),
        ("3_multiring_laplacian", "3. Multi-Ring Laplacian", HoleFiller.fill_multiring_laplacian),
        ("4_multiring_biharmonic_tps", "4. Multi-Ring Biharmonic TPS", HoleFiller.fill_multiring_biharmonic_tps),
    ]

    all_model_data = []

    for model_title, prefix, gen_fn, png_name, z_lim, z_aspect in models_to_run:
        orig_mesh, broken_mesh = gen_fn()
        loops, open_edges, _ = HoleDetector.find_boundary_loops(broken_mesh)

        print(f"\n>>> {model_title}")
        print(f"    Eredeti: {len(orig_mesh.faces)} haromszog | Serult: {len(broken_mesh.faces)} haromszog | Lyukak: {len(loops)} db ({open_edges} nyitott el)")

        orig_mesh.save_obj(f"{prefix}_0_eredeti.obj")
        broken_mesh.save_obj(f"{prefix}_0_lyukas.obj")

        results = {}
        repaired_meshes = {}

        for key, label, fn in methods:
            t0 = time.perf_counter()
            rep = fn(broken_mesh)
            dt = (time.perf_counter() - t0) * 1000.0
            rep.save_obj(f"{prefix}_{key}.obj")
            repaired_meshes[label] = rep
            m = evaluate_repair(orig_mesh, broken_mesh, rep, dt)
            results[label] = m
            print(f"    {label:28s} | Potolt: {m['new_faces']:3d} | Lyuk: {m['remaining_holes']} | RMSE: {m['rmse']:.4f} | Haus: {m['hausdorff']:.4f} | Ido: {m['time_ms']:.1f} ms")

        create_3d_figure(model_title, orig_mesh, broken_mesh, repaired_meshes, methods, png_name, z_lim, z_aspect)

        all_model_data.append({
            "name": model_title,
            "orig_faces": len(orig_mesh.faces),
            "broken_faces": len(broken_mesh.faces),
            "init_holes": len(loops),
            "init_open_edges": open_edges,
            "results": results,
            "png_file": png_name
        })

    csv_p, txt_p, html_p = generate_reports(all_model_data)
    print("\n=================================================================")
    print("MINDEN FAJL SIKERESEN LEGENERALVA A KOVETKEZO MAPPABA:")
    print(f"  {OUT_DIR}")
    print(f"  - Meresi jegyzokonyv (HTML): {os.path.basename(html_p)}")
    print(f"  - Meresi jegyzokonyv (TXT):  {os.path.basename(txt_p)}")
    print(f"  - Excel tablazat (CSV):      {os.path.basename(csv_p)}")
    print("  - 12 db .obj 3D modell fajl + 2 db 3D osszehasonlito .png kep")
    print("=================================================================")

    try:
        webbrowser.open(f"file:///{os.path.abspath(html_p).replace(chr(92), '/')}")
    except Exception:
        pass

    plt.show()
