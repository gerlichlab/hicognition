"""Writes the synthetic genome that the reference results are computed on.

The files are committed, so every later run reads the same bytes, whatever library versions
it has. Rerun this script only together with new reference results, from back_end/:

    python -m tests.reference.make_inputs tests/testfiles/reference

The genome has two chromosomes with two arms each. Contacts fall off with distance, are denser
inside TADs and form loops between anchor pairs. chr1 has a stretch without contacts, so its
balancing weights are NaN there, and regions on chr3 lie outside the genome.

- cooler_a.mcool has the resolutions 1, 2, 5, 10, 20 and 50 kb, the 1-2-5 steps the upload
  documentation asks for.
- cooler_b.mcool has 1, 5, 10, 25 and 50 kb, as 4D Nucleome coolers do, and no balancing
  weights at 50 kb.
- Three BigWigs: peaks at the anchors, levels per TAD, and dips at the anchors with two stretches
  without data.
- Region sets: anchors as points, TADs, larger overlapping domains and loops as BEDPE, plus two
  point sets for the region collection.
"""
import os
import subprocess
import sys

import cooler
import h5py
import numpy as np
import pandas as pd
import pyBigWig

SEED = 20261106
CHROMSIZES = {"chr1": 10_000_000, "chr2": 6_000_000}
ARMS = [
    ("chr1", 0, 4_000_000),
    ("chr1", 4_000_000, 10_000_000),
    ("chr2", 0, 2_500_000),
    ("chr2", 2_500_000, 6_000_000),
]
BASE_RESOLUTION = 1000
RESOLUTIONS_A = [1000, 2000, 5000, 10000, 20000, 50000]
RESOLUTIONS_B = [1000, 5000, 10000, 25000, 50000]
CIS_CONTACTS = 350_000
CONTACTS_PER_LOOP = 120
TRANS_CONTACTS = 4_000
# no contacts in this stretch, so its bins get NaN weights
CONTACT_GAP = ("chr1", 7_000_000, 7_060_000)
BIGWIG_STEP = 100
PEAK_WIDTH = 500


def make_tads(rng):
    """TADs of 150 to 700 kb that tile each chromosome."""
    tads = []
    for chrom, size in CHROMSIZES.items():
        start = 0
        while start < size:
            end = min(start + int(rng.integers(150, 701)) * 1000, size)
            tads.append((chrom, start, end))
            start = end
    return pd.DataFrame(tads, columns=["chrom", "start", "end"])


def make_anchors(rng, tads):
    """Loop anchors: most TAD boundaries and as many random positions."""
    anchors = []
    for chrom, group in tads.groupby("chrom", sort=False):
        for boundary in group["start"].to_numpy()[1:]:
            if rng.random() < 0.8:
                anchors.append((chrom, int(boundary + rng.integers(-10_000, 10_001))))
    for _ in range(len(anchors)):
        chrom = "chr1" if rng.random() < 0.6 else "chr2"
        anchors.append(
            (chrom, int(rng.integers(50_000, CHROMSIZES[chrom] - 50_000)))
        )
    anchors = pd.DataFrame(anchors, columns=["chrom", "pos"])
    order = anchors["chrom"].map({chrom: i for i, chrom in enumerate(CHROMSIZES)})
    return anchors.assign(order=order).sort_values(["order", "pos"]).drop(columns="order")


def make_loops(rng, anchors, number=40):
    """Pairs of anchors on one chromosome, 100 kb to 1.5 Mb apart."""
    candidates = []
    for chrom, group in anchors.groupby("chrom", sort=False):
        positions = group["pos"].to_numpy()
        for i, first in enumerate(positions):
            for second in positions[i + 1 :]:
                if 100_000 <= second - first <= 1_500_000:
                    candidates.append((chrom, first, second))
    picked = rng.choice(len(candidates), size=number, replace=False)
    return pd.DataFrame(
        [candidates[i] for i in sorted(picked)], columns=["chrom", "pos1", "pos2"]
    )


def cis_contacts(rng, tads, number):
    """Contacts within chromosomes: distances from a power law, fewer across TAD boundaries."""
    lengths = np.array(list(CHROMSIZES.values()), dtype=float)
    per_chrom = rng.multinomial(number, lengths / lengths.sum())
    exponent, shortest, longest = 1.1, 1e3, 3e6
    contacts = []
    for (chrom, size), count in zip(CHROMSIZES.items(), per_chrom):
        # draw twice as many, since contacts across TAD boundaries are thinned out
        u = rng.random(2 * count)
        distance = (
            shortest ** (1 - exponent)
            + u * (longest ** (1 - exponent) - shortest ** (1 - exponent))
        ) ** (1 / (1 - exponent))
        pos1 = rng.integers(0, size, 2 * count)
        pos2 = (pos1 + distance).astype(np.int64)
        inside = pos2 < size
        starts = tads.loc[tads["chrom"] == chrom, "start"].to_numpy()
        same_tad = np.searchsorted(starts, pos1, "right") == np.searchsorted(
            starts, pos2, "right"
        )
        keep = inside & (same_tad | (rng.random(2 * count) < 0.4))
        pos1, pos2 = pos1[keep][:count], pos2[keep][:count]
        contacts.append(pd.DataFrame({"chrom1": chrom, "pos1": pos1, "chrom2": chrom, "pos2": pos2}))
    return pd.concat(contacts, ignore_index=True)


def loop_contacts(rng, loops):
    """Contacts concentrated around each pair of loop anchors."""
    contacts = []
    for loop in loops.itertuples():
        size = CHROMSIZES[loop.chrom]
        pos1 = np.clip(loop.pos1 + rng.normal(0, 2_000, CONTACTS_PER_LOOP), 0, size - 1)
        pos2 = np.clip(loop.pos2 + rng.normal(0, 2_000, CONTACTS_PER_LOOP), 0, size - 1)
        contacts.append(
            pd.DataFrame(
                {"chrom1": loop.chrom, "pos1": pos1.astype(np.int64), "chrom2": loop.chrom, "pos2": pos2.astype(np.int64)}
            )
        )
    return pd.concat(contacts, ignore_index=True)


def trans_contacts(rng):
    """Uniform contacts between chr1 and chr2."""
    return pd.DataFrame(
        {
            "chrom1": "chr1",
            "pos1": rng.integers(0, CHROMSIZES["chr1"], TRANS_CONTACTS),
            "chrom2": "chr2",
            "pos2": rng.integers(0, CHROMSIZES["chr2"], TRANS_CONTACTS),
        }
    )


def pixels_from_contacts(contacts):
    """Counts contacts per pair of base-resolution bins, upper triangle, sorted."""
    gap_chrom, gap_start, gap_end = CONTACT_GAP
    in_gap = np.zeros(len(contacts), dtype=bool)
    for side in ("1", "2"):
        in_gap |= (contacts["chrom" + side] == gap_chrom) & contacts["pos" + side].between(
            gap_start, gap_end - 1
        )
    contacts = contacts[~in_gap]
    offsets, total = {}, 0
    for chrom, size in CHROMSIZES.items():
        offsets[chrom] = total
        total += -(-size // BASE_RESOLUTION)
    bin1 = contacts["chrom1"].map(offsets).to_numpy() + contacts["pos1"].to_numpy() // BASE_RESOLUTION
    bin2 = contacts["chrom2"].map(offsets).to_numpy() + contacts["pos2"].to_numpy() // BASE_RESOLUTION
    low, high = np.minimum(bin1, bin2), np.maximum(bin1, bin2)
    keys, counts = np.unique(low * total + high, return_counts=True)
    return pd.DataFrame(
        {"bin1_id": keys // total, "bin2_id": keys % total, "count": counts.astype(np.int32)}
    )


def write_coolers(out_dir, pixels):
    """Writes the base cooler, zoomifies and balances it twice, and removes cooler_b's 50 kb weights."""
    bins = cooler.util.binnify(pd.Series(CHROMSIZES), BASE_RESOLUTION)
    base = os.path.join(out_dir, "base.cool")
    cooler.create_cooler(base, bins, pixels, ordered=True, dtypes={"count": np.int32})
    cooler_cli = os.path.join(os.path.dirname(sys.executable), "cooler")
    for name, resolutions in (("cooler_a.mcool", RESOLUTIONS_A), ("cooler_b.mcool", RESOLUTIONS_B)):
        subprocess.run(
            [
                cooler_cli,
                "zoomify",
                "--balance",
                "--resolutions",
                ",".join(str(r) for r in resolutions),
                "--out",
                os.path.join(out_dir, name),
                base,
            ],
            check=True,
        )
    with h5py.File(os.path.join(out_dir, "cooler_b.mcool"), "r+") as f:
        del f["resolutions/50000/bins/weight"]
    os.remove(base)


def peak_values(rng, anchors, baseline, amplitude):
    """Per chromosome, values in 100 bp steps: a baseline per 5 kb block plus a peak at each anchor."""
    tracks = {}
    offsets = np.arange(-20, 21)
    shape = amplitude * np.exp(-0.5 * (offsets / 3) ** 2)
    for chrom, size in CHROMSIZES.items():
        steps = size // BIGWIG_STEP
        values = np.repeat(baseline * (1 + 0.3 * rng.random(steps // 50 + 1)), 50)[:steps]
        for center in anchors.loc[anchors["chrom"] == chrom, "pos"].to_numpy() // BIGWIG_STEP:
            index = center + offsets
            inside = (index >= 0) & (index < steps)
            values[index[inside]] += shape[inside]
        tracks[chrom] = values
    return tracks


def domain_values(rng, tads):
    """Per chromosome, values in 100 bp steps: alternating levels per TAD, noise per 10 kb."""
    tracks = {}
    for chrom, size in CHROMSIZES.items():
        steps = size // BIGWIG_STEP
        starts = tads.loc[tads["chrom"] == chrom, "start"].to_numpy() // BIGWIG_STEP
        tad_index = np.searchsorted(starts, np.arange(steps), "right") - 1
        levels = np.where(tad_index % 2 == 0, 0.5, 3.0)
        noise = np.repeat(1 + 0.2 * rng.random(steps // 100 + 1), 100)[:steps]
        tracks[chrom] = levels * noise
    return tracks


def write_bigwig(path, tracks):
    """One entry per run of equal values; NaN stretches are left out, so readers see no data there."""
    bigwig = pyBigWig.open(path, "w")
    bigwig.addHeader(list(CHROMSIZES.items()))
    for chrom, values in tracks.items():
        values = np.round(values, 3)
        missing = np.isnan(values)
        same = (values[1:] == values[:-1]) | (missing[1:] & missing[:-1])
        starts = np.flatnonzero(np.r_[True, ~same])
        ends = np.r_[starts[1:], len(values)]
        keep = ~missing[starts]
        bigwig.addEntries(
            [chrom] * int(keep.sum()),
            (starts[keep] * BIGWIG_STEP).tolist(),
            ends=np.minimum(ends[keep] * BIGWIG_STEP, CHROMSIZES[chrom]).tolist(),
            values=values[starts[keep]].astype(float).tolist(),
        )
    bigwig.close()


def write_bigwigs(out_dir, rng, anchors, tads):
    write_bigwig(os.path.join(out_dir, "peaks.bw"), peak_values(rng, anchors, 1.0, 20.0))
    write_bigwig(os.path.join(out_dir, "domains.bw"), domain_values(rng, tads))
    dips = peak_values(rng, anchors, 5.0, -4.0)
    dips["chr1"][9_500_000 // BIGWIG_STEP :] = np.nan
    dips["chr2"][1_000_000 // BIGWIG_STEP : 1_200_000 // BIGWIG_STEP] = np.nan
    write_bigwig(os.path.join(out_dir, "dips.bw"), dips)


def peaks(frame, column="pos"):
    """500 bp intervals centred on the positions in column."""
    half = PEAK_WIDTH // 2
    return pd.DataFrame(
        {"chrom": frame["chrom"], "start": frame[column] - half, "end": frame[column] + half}
    )


def write_regions(out_dir, rng, anchors, tads, loops):
    def write(name, frame):
        frame.to_csv(os.path.join(out_dir, name), sep="\t", header=False, index=False)

    # points, with one near the start of chr1, one across chr1's arm boundary and two outside the genome
    edge_cases = pd.DataFrame(
        [("chr1", 500, 1000), ("chr1", 3_999_800, 4_000_300), ("chr3", 100_000, 100_500), ("chr3", 200_000, 200_500)],
        columns=["chrom", "start", "end"],
    )
    write("points.bed", pd.concat([peaks(anchors), edge_cases], ignore_index=True))
    write("tads.bed", tads)
    # overlapping domains of 650 to 900 kb: a median near 800 kb, where 25 kb bins win for 5% pileups
    domains = []
    for _ in range(45):
        chrom = "chr1" if rng.random() < 0.6 else "chr2"
        length = int(rng.integers(650, 901)) * 1000
        start = int(rng.integers(0, CHROMSIZES[chrom] - length) // 1000) * 1000
        domains.append((chrom, start, start + length))
    domains = pd.DataFrame(domains, columns=["chrom", "start", "end"])
    order = domains["chrom"].map({chrom: i for i, chrom in enumerate(CHROMSIZES)})
    write("domains.bed", domains.assign(order=order).sort_values(["order", "start"]).drop(columns="order"))
    first, second = peaks(loops, "pos1"), peaks(loops, "pos2")
    write(
        "loops.bedpe",
        pd.concat([first.add_suffix("1"), second.add_suffix("2")], axis=1),
    )
    shifted = anchors.assign(pos=np.minimum(anchors["pos"] + 50_000, anchors["chrom"].map(CHROMSIZES) - PEAK_WIDTH))
    write("shifted.bed", peaks(shifted))
    random_points = []
    for _ in range(80):
        chrom = "chr1" if rng.random() < 0.6 else "chr2"
        random_points.append((chrom, int(rng.integers(PEAK_WIDTH, CHROMSIZES[chrom] - PEAK_WIDTH))))
    random_points = pd.DataFrame(random_points, columns=["chrom", "pos"])
    order = random_points["chrom"].map({chrom: i for i, chrom in enumerate(CHROMSIZES)})
    write("random.bed", peaks(random_points.assign(order=order).sort_values(["order", "pos"])))


def write_assembly(out_dir):
    pd.Series(CHROMSIZES).to_csv(os.path.join(out_dir, "synthetic.chrom.sizes"), sep="\t", header=False)
    pd.DataFrame(ARMS, columns=["chrom", "start", "end"]).to_csv(
        os.path.join(out_dir, "arms.synthetic"), index=False
    )


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    rng = np.random.default_rng(SEED)
    tads = make_tads(rng)
    anchors = make_anchors(rng, tads)
    loops = make_loops(rng, anchors)
    contacts = pd.concat(
        [cis_contacts(rng, tads, CIS_CONTACTS), loop_contacts(rng, loops), trans_contacts(rng)],
        ignore_index=True,
    )
    write_coolers(out_dir, pixels_from_contacts(contacts))
    write_bigwigs(out_dir, rng, anchors, tads)
    write_regions(out_dir, rng, anchors, tads, loops)
    write_assembly(out_dir)


if __name__ == "__main__":
    main(sys.argv[1])
