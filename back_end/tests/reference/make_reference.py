"""Computes the reference results and writes them to tests/testfiles/reference/expected/.

Run in the image whose results are the reference, from back_end/:

    python -m tests.reference.make_reference

The arrays go into arrays.npz, except those compared only by their shape, whose shapes go into
shapes.json. The cleaned region files and the errors steps raised go into text.json, and the
versions of the libraries that computed them into versions.txt.
"""

import json
import os
import sys
import tempfile

EXPECTED_DIR = os.path.join(
    os.path.dirname(__file__), "..", "testfiles", "reference", "expected"
)
LIBRARIES = [
    "numpy",
    "pandas",
    "scipy",
    "cooler",
    "cooltools",
    "bioframe",
    "ngs",
    "pylola",
    "sklearn",
    "skimage",
    "umap",
    "numba",
    "bbi",
    "cv2",
    "flask",
    "sqlalchemy",
]


def library_versions():
    import importlib

    lines = ["python " + sys.version.split()[0]]
    for name in LIBRARIES:
        try:
            module = importlib.import_module(name)
            lines.append(name + " " + str(getattr(module, "__version__", "unknown")))
        except ImportError:
            lines.append(name + " not installed")
    return lines


def main():
    work_dir = tempfile.mkdtemp(prefix="hicognition-reference-")
    # the configuration reads the log paths when app is first imported
    os.environ.setdefault("LOG_FILE_NAME", os.path.join(work_dir, "application.logs"))
    os.environ.setdefault("ERROR_LOG_FILE_NAME", os.path.join(work_dir, "error.logs"))
    from .harness import compute
    from .test_reference import kind

    import numpy as np

    results = compute(os.path.join(work_dir, "upload"))
    arrays = {
        key: value
        for key, value in results.items()
        if isinstance(value, np.ndarray) and kind(key) != "shape"
    }
    shapes = {
        key: list(value.shape)
        for key, value in results.items()
        if isinstance(value, np.ndarray) and kind(key) == "shape"
    }
    text = {key: value for key, value in results.items() if isinstance(value, str)}
    os.makedirs(EXPECTED_DIR, exist_ok=True)
    np.savez_compressed(os.path.join(EXPECTED_DIR, "arrays.npz"), **arrays)
    with open(os.path.join(EXPECTED_DIR, "shapes.json"), "w", encoding="utf-8") as f:
        json.dump(shapes, f, indent=1, sort_keys=True)
    with open(os.path.join(EXPECTED_DIR, "text.json"), "w", encoding="utf-8") as f:
        json.dump(text, f, indent=1, sort_keys=True)
    with open(os.path.join(EXPECTED_DIR, "versions.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(library_versions()) + "\n")
    print(
        f"{len(arrays)} arrays, {len(shapes)} shapes and {len(text)} texts written to {os.path.abspath(EXPECTED_DIR)}"
    )


if __name__ == "__main__":
    main()
