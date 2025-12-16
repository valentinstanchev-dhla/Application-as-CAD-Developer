#!/usr/bin/env python3
"""
Render scaffold geometry from JSON using 3D wireframe boxes.

CLI example:
python render.py -f scaffold-1.json -h1 "ScaffoldingBox" -tx 15.5 -tz -1.2 -rz 90 -vo -vz

PyCharm:
Just click Run ▶ and you will be prompted for the file.
"""

import argparse
import json
import math
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa

# ---------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------

CUBE_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
]


def local_box_vertices(w, d, h):
    hw, hd = w * 0.5, d * 0.5
    return [
        (-hw, -hd, 0), (hw, -hd, 0),
        (hw, hd, 0), (-hw, hd, 0),
        (-hw, -hd, h), (hw, -hd, h),
        (hw, hd, h), (-hw, hd, h),
    ]


def mat4_mul_vec3(m, v):
    x, y, z = v
    return (
        m[0] * x + m[1] * y + m[2] * z + m[3],
        m[4] * x + m[5] * y + m[6] * z + m[7],
        m[8] * x + m[9] * y + m[10] * z + m[11],
    )


def rotate_z(v, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    x, y, z = v
    return c * x - s * y, s * x + c * y, z


def transform(v, tx, ty, tz, rz):
    return rotate_z((v[0] + tx, v[1] + ty, v[2] + tz), rz)


# ---------------------------------------------------------
# Rendering
# ---------------------------------------------------------

def render(parts, tx, ty, tz, rz, highlight, ortho, view):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.set_box_aspect([1, 1, 1])

    if ortho:
        ax.set_proj_type("ortho")

    if view == "x":
        ax.view_init(0, 0)
    elif view == "y":
        ax.view_init(0, 90)
    elif view == "z":
        ax.view_init(90, -90)

    for p in parts:
        ecs = p["ecsBox"]
        verts = local_box_vertices(p["width"], p["depth"], p["height"])
        verts = [mat4_mul_vec3(ecs, v) for v in verts]
        verts = [transform(v, tx, ty, tz, rz) for v in verts]

        color = "red" if p["name"] == highlight else "black"
        lw = 3 if p["name"] == highlight else 1

        for i0, i1 in CUBE_EDGES:
            xs, ys, zs = zip(verts[i0], verts[i1])
            ax.plot(xs, ys, zs, color=color, linewidth=lw)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    plt.show()


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("-f", "--input", help="Input JSON file")
    parser.add_argument("-tx", type=float, default=0.0)
    parser.add_argument("-ty", type=float, default=0.0)
    parser.add_argument("-tz", type=float, default=0.0)
    parser.add_argument("-rz", type=float, default=0.0)
    parser.add_argument("-h1", dest="highlight", help="Highlight part name")
    parser.add_argument("-vo", action="store_true", help="Orthographic view")
    parser.add_argument("-vx", action="store_true")
    parser.add_argument("-vy", action="store_true")
    parser.add_argument("-vz", action="store_true")

    args = parser.parse_args()

    # ---- FIX: interactive fallback ----
    if not args.input:
        args.input = input("Enter path to input JSON file: ").strip()

    if not args.input:
        print("ERROR: Input file is required.", file=sys.stderr)
        sys.exit(2)

    view = "x" if args.vx else "y" if args.vy else "z" if args.vz else None

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "parts" not in data:
        raise ValueError("Invalid JSON: missing 'parts'")

    render(
        data["parts"],
        args.tx, args.ty, args.tz, args.rz,
        args.highlight,
        args.vo,
        view,
    )


if __name__ == "__main__":
    main()