import argparse
import random
import shutil
from pathlib import Path
from collections import defaultdict

IMAGE_EXTS_DEFAULT = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".gif", ".webp"}

def find_images(src: Path, exts, recursive: bool):
    pattern = "**/*" if recursive else "*"
    files = [p for p in src.glob(pattern) if p.is_file() and p.suffix.lower() in exts]
    return files

def group_by_immediate_parent(paths):
    groups = defaultdict(list)
    for p in paths:
        groups[p.parent.name].append(p)
    return groups

def proportional_take(group_counts, total_needed, rnd):
    # Distribute "total_needed" proportionally across groups, rounding and fixing remainder
    total_available = sum(group_counts.values())
    if total_available == 0:
        return {g: 0 for g in group_counts}

    raw = {g: (group_counts[g] / total_available) * total_needed for g in group_counts}
    base = {g: int(v) for g, v in raw.items()}
    remainder = total_needed - sum(base.values())
    if remainder > 0:
        # assign remainder to the groups with largest fractional parts first (random tie break)
        fracs = [(g, raw[g] - base[g]) for g in group_counts]
        rnd.shuffle(fracs)  # randomize tie-breaking among equal fractions
        fracs.sort(key=lambda x: x[1], reverse=True)
        for i in range(remainder):
            base[fracs[i % len(fracs)][0]] += 1
    return base

def copy_with_pairs(src_file: Path, dst_file: Path, pair_exts, overwrite: bool):
    dst_file.parent.mkdir(parents=True, exist_ok=True)
    if not dst_file.exists() or overwrite:
        shutil.copy2(src_file, dst_file)

    # Copy annotation/sidecar files with same stem (if present)
    for ext in pair_exts:
        cand = src_file.with_suffix(ext)
        if cand.exists():
            target = dst_file.with_suffix(ext)
            if not target.exists() or overwrite:
                shutil.copy2(cand, target)

def main():
    parser = argparse.ArgumentParser(
        description="Randomly sample images into a training dataset folder."
    )
    parser.add_argument("--src", required=True, type=Path, help="Source dataset folder")
    parser.add_argument("--dst", required=True, type=Path, help="Destination folder")
    parser.add_argument("-n", "--num", required=True, type=int, help="Number of images to sample")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--recursive", action="store_true", help="Search recursively for images")
    parser.add_argument("--ext", nargs="*", help="Image extensions to include (e.g. .jpg .png). Defaults to common types.")
    parser.add_argument("--stratify", action="store_true",
                        help="Stratify by immediate subfolders of --src (e.g., class folders).")
    parser.add_argument("--keep-tree", action="store_true",
                        help="Keep original relative folder structure under --dst.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite if files exist at destination")
    parser.add_argument("--move", action="store_true", help="Move files instead of copying")
    parser.add_argument("--pair-exts", default="",
                        help="Comma-separated list of paired extensions to copy with same stem (e.g., .json,.txt,.xml).")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without copying/moving")
    args = parser.parse_args()

    rnd = random.Random(args.seed)
    exts = set(e.lower() if e.startswith(".") else f".{e.lower()}" for e in (args.ext or IMAGE_EXTS_DEFAULT))
    pair_exts = tuple([e if e.startswith(".") else f".{e}" for e in args.pair_exts.split(",") if e.strip()])

    if not args.src.exists() or not args.src.is_dir():
        raise SystemExit(f"Source folder not found: {args.src}")

    all_imgs = find_images(args.src, exts, args.recursive)
    if not all_imgs:
        raise SystemExit("No images found with the given extensions.")

    if args.stratify:
        groups = group_by_immediate_parent(all_imgs)
        counts = {g: len(groups[g]) for g in groups}
        to_take_per_group = proportional_take(counts, args.num, rnd)

        chosen = []
        for g, take_n in to_take_per_group.items():
            candidates = groups[g][:]
            rnd.shuffle(candidates)
            chosen.extend(candidates[:min(take_n, len(candidates))])

        # If proportional rounding left us short due to tiny groups, top up randomly
        if len(chosen) < args.num:
            remaining = [p for p in all_imgs if p not in set(chosen)]
            rnd.shuffle(remaining)
            needed = args.num - len(chosen)
            chosen.extend(remaining[:needed])
    else:
        candidates = all_imgs[:]
        rnd.shuffle(candidates)
        chosen = candidates[:min(args.num, len(candidates))]

    if len(chosen) < args.num:
        print(f"Warning: Requested {args.num} but only {len(chosen)} images available.")

    ops = []
    for src_path in chosen:
        if args.keep-tree:
            rel = src_path.relative_to(args.src)
            dst_path = args.dst / rel
        elif args.stratify:
            # preserve class folder (immediate parent) under dst
            dst_path = args.dst / src_path.parent.name / src_path.name
        else:
            dst_path = args.dst / src_path.name

        ops.append((src_path, dst_path))

    print(f"Selected {len(ops)} images.")
    if args.dry_run:
        for s, d in ops[:10]:
            print(f"[DRY-RUN] {'MOVE' if args.move else 'COPY'} {s} -> {d}")
        if len(ops) > 10:
            print(f"...and {len(ops) - 10} more")
        return

    for src_path, dst_path in ops:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        if args.move:
            if args.overwrite and dst_path.exists():
                dst_path.unlink()
            shutil.move(str(src_path), str(dst_path))
            # Move paired files if present
            for ext in pair_exts:
                cand = src_path.with_suffix(ext)
                if cand.exists():
                    target = dst_path.with_suffix(ext)
                    if args.overwrite and target.exists():
                        target.unlink()
                    shutil.move(str(cand), str(target))
        else:
            copy_with_pairs(src_path, dst_path, pair_exts, args.overwrite)

    print(f"Done. Files {'moved' if args.move else 'copied'} to: {args.dst}")

if __name__ == "__main__":
    main()
