import subprocess
import sys
from pathlib import Path
from uuid import uuid4


def ensure_ffmpeg_available() -> None:
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "ffmpeg was not found on your PATH. "
            "Please install ffmpeg and make sure it is available in the terminal."
        ) from exc


def convert_all() -> None:
    root = Path(__file__).resolve().parents[1]
    src_root = root / "dataset" / "ssl-alphabet"
    dst_root = root / "dataset" / "ssl-alphabet-converted"

    if not src_root.exists():
        raise FileNotFoundError(f"Source folder not found: {src_root}")

    dst_root.mkdir(parents=True, exist_ok=True)

    video_exts = {".mov", ".mp4", ".avi", ".mkv", ".m4v"}
    total = 0
    skipped = 0

    print(f"Source root : {src_root}")
    print(f"Target root : {dst_root}")
    print("Starting conversion...\n")

    for letter_dir in sorted(src_root.iterdir()):
        if not letter_dir.is_dir():
            continue

        rel_label = letter_dir.name
        dst_letter_dir = dst_root / rel_label
        dst_letter_dir.mkdir(parents=True, exist_ok=True)

        for src_vid in sorted(letter_dir.iterdir()):
            if src_vid.suffix.lower() not in video_exts:
                continue

            # Generate random GUID-style name
            guid = uuid4().hex[:8]
            dst_vid = dst_letter_dir / f"ssl-{guid}.mp4"

            if dst_vid.exists():
                print(f"[skip] {src_vid} -> {dst_vid} (already exists)")
                skipped += 1
                continue

            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(src_vid),
                "-c:v",
                "libx264",
                "-crf",
                "23",
                "-preset",
                "veryfast",
                "-c:a",
                "aac",
                "-movflags",
                "+faststart",
                str(dst_vid),
            ]

            print(f"[convert] {src_vid} -> {dst_vid}")
            try:
                subprocess.run(cmd, check=True)
                total += 1
            except subprocess.CalledProcessError as exc:  # noqa: PERF203, BLE001
                print(f"  !! ffmpeg failed for {src_vid}: {exc}")
                if dst_vid.exists():
                    dst_vid.unlink(missing_ok=True)

    print("\nDone.")
    print(f"Converted: {total} file(s)")
    print(f"Skipped  : {skipped} file(s)")


def main() -> None:
    try:
        ensure_ffmpeg_available()
        convert_all()
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

