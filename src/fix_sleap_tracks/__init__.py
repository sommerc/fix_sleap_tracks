from pathlib import Path

import argparse

from loguru import logger
from rich.prompt import Prompt
import sleap_io as sio


def find_unique_tracks_by_name(tracks):
    unique = {}
    for t in tracks:
        if t.name not in unique:
            unique[t.name] = t
    return unique


def get_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="A package to fix SLEAP tracks.")
    parser.add_argument("slp_file", help="Path to the SLEAP .slp file to be fixed.")

    return parser.parse_args()


def main() -> None:
    args = get_parser()
    logger.info(f"Loading SLEAP file: {args.slp_file}")

    slp_file = Path(args.slp_file)
    assert slp_file.exists(), f"SLEAP file {args.slp_file} does not exist."

    slp = sio.load_slp(args.slp_file)

    unqique_tracks = find_unique_tracks_by_name(slp.tracks)

    logger.info(
        f"Found {len(unqique_tracks)} unique tracks out of {len(slp.tracks)} total tracks."
    )
    for t in unqique_tracks.values():
        logger.info(f" - {t.name}")

    if len(unqique_tracks) == len(slp.tracks):
        logger.success("No duplicates found. SLP is okay. Done")
        return

    confirm = Prompt.ask(
        "Do you want to proceed with fixing the SLP by removing duplicate tracks?",
        choices=["yes", "no"],
        default="yes",
    )
    if confirm != "yes":
        logger.info("Aborting.")
        return

    for lf in slp.labeled_frames:
        for inst in lf.instances:
            if inst.track is not None:
                if inst.track not in unqique_tracks.values():
                    inst.track = unqique_tracks[inst.track.name]

    slp.tracks = list(unqique_tracks.values())

    out_slp = slp_file.with_stem(slp_file.stem + "_fixed")
    logger.info(f"Saving fixed SLP to: {out_slp}")
    sio.save_slp(slp, out_slp)

    logger.success("Done.")
