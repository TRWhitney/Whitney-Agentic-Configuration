#!/usr/bin/env python3
"""Prepare transcript and visual evidence for one YouTube source."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import cast
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

CommandRunner = Callable[[list[str]], subprocess.CompletedProcess[str]]
CommandResolver = Callable[[str], str | None]
TIMING_PATTERN = re.compile(
    r"^(?P<start>(?:\d{2}:)?\d{2}:\d{2}\.\d{3})\s+-->\s+"
    r"(?P<end>(?:\d{2}:)?\d{2}:\d{2}\.\d{3})(?:\s+.*)?$"
)
INLINE_TAG_PATTERN = re.compile(r"<[^>]+>")
SCENE_TIME_PATTERN = re.compile(r"pts_time:(?P<time>\d+(?:\.\d+)?)")


class PreparationError(Exception):
    """Describe a recoverable preparation failure without a traceback."""


@dataclass(frozen=True)
class Configuration:
    url: str
    workspace: Path
    language: str | None = None
    interval_seconds: float = 60.0
    scene_threshold: float = 0.35
    max_scene_frames: int = 96
    sheet_columns: int = 4
    sheet_rows: int = 4
    whisper_command: str = "whisper-cli"
    whisper_model: Path | None = None


@dataclass(frozen=True)
class CaptionSelection:
    origin: str
    language: str
    automatic: bool


@dataclass(frozen=True)
class SceneFrame:
    timestamp: float
    score: float = 0.0


@dataclass(frozen=True)
class PreparedFrame:
    path: str
    timestamp: float


def option_value(arguments: Sequence[str], option: str) -> str | None:
    """Return the value following an option in an argument vector."""
    try:
        index = arguments.index(option)
    except ValueError:
        return None
    if index + 1 >= len(arguments):
        return None
    return arguments[index + 1]


def run_command(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    """Run one external boundary and retain output for diagnostics."""
    return subprocess.run(
        arguments,
        check=False,
        capture_output=True,
        text=True,
    )


def execute(runner: CommandRunner, arguments: list[str], label: str) -> str:
    result = runner(arguments)
    if result.returncode != 0:
        detail = (
            result.stderr.strip() or result.stdout.strip() or "no diagnostic output"
        )
        raise PreparationError(f"{label} failed: {detail}")
    return result.stdout


def resolve_tool(name: str, resolver: CommandResolver) -> str:
    resolved = resolver(name)
    if resolved is None:
        raise PreparationError(
            f"Required command '{name}' was not found. Install it separately and "
            "make it available on PATH."
        )
    return resolved


def ensure_empty_workspace(workspace: Path) -> None:
    if workspace.exists() and not workspace.is_dir():
        raise PreparationError(f"Workspace is not a directory: {workspace}")
    if workspace.exists() and next(workspace.iterdir(), None) is not None:
        raise PreparationError(f"Workspace must be empty: {workspace}")
    workspace.mkdir(parents=True, exist_ok=True)


def object_mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    return {str(key): item for key, item in value.items()}


def available_languages(value: object) -> tuple[str, ...]:
    tracks = object_mapping(value)
    return tuple(
        language
        for language, formats in tracks.items()
        if isinstance(formats, list) and formats
    )


def base_language(language: str) -> str:
    return language.lower().split("-", maxsplit=1)[0]


def choose_language(
    languages: Sequence[str], desired: str | None, *, prefer_original: bool
) -> str | None:
    if not languages:
        return None
    if desired is None:
        return languages[0] if len(languages) == 1 else None

    desired_lower = desired.lower()
    by_lower = {language.lower(): language for language in languages}
    candidates = (
        (f"{desired_lower}-orig", desired_lower)
        if prefer_original
        else (desired_lower, f"{desired_lower}-orig")
    )
    for candidate in candidates:
        if candidate in by_lower:
            return by_lower[candidate]

    desired_base = base_language(desired_lower)
    base_matches = [
        language for language in languages if base_language(language) == desired_base
    ]
    if prefer_original:
        original_matches = [
            language for language in base_matches if language.lower().endswith("-orig")
        ]
        if len(original_matches) == 1:
            return original_matches[0]
    return base_matches[0] if len(base_matches) == 1 else None


def select_caption(
    metadata: Mapping[str, object], requested_language: str | None
) -> CaptionSelection | None:
    """Select original-language transcript evidence without choosing a translation."""
    metadata_language = metadata.get("language")
    known_language = requested_language or (
        metadata_language if isinstance(metadata_language, str) else None
    )
    authored_languages = available_languages(metadata.get("subtitles"))
    authored = choose_language(
        authored_languages, known_language, prefer_original=False
    )
    if authored is not None:
        return CaptionSelection("authored-caption", authored, False)

    automatic_languages = available_languages(metadata.get("automatic_captions"))
    automatic = choose_language(
        automatic_languages, known_language, prefer_original=True
    )
    if automatic is not None:
        return CaptionSelection("platform-auto-caption", automatic, True)

    if authored_languages or automatic_languages:
        available = ", ".join((*authored_languages, *automatic_languages))
        raise PreparationError(
            "Caption language is ambiguous or the original language could not be "
            f"identified ({available}). Supply --language explicitly."
        )
    return None


def fetch_metadata(yt_dlp: str, url: str, runner: CommandRunner) -> dict[str, object]:
    output = execute(
        runner,
        [
            yt_dlp,
            "--dump-single-json",
            "--skip-download",
            "--no-playlist",
            "--no-warnings",
            "--",
            url,
        ],
        "yt-dlp metadata inspection",
    )
    try:
        parsed: object = json.loads(output)
    except json.JSONDecodeError as error:
        raise PreparationError("yt-dlp returned invalid metadata JSON.") from error
    if not isinstance(parsed, dict):
        raise PreparationError("yt-dlp metadata was not an object.")
    return {str(key): value for key, value in parsed.items()}


def new_file(previous: set[Path], current: Sequence[Path], label: str) -> Path:
    candidates = [path for path in current if path not in previous]
    if len(candidates) != 1:
        raise PreparationError(
            f"Expected one {label}, found {len(candidates)}. Workspace was preserved."
        )
    return candidates[0]


def download_caption(
    yt_dlp: str,
    url: str,
    workspace: Path,
    selection: CaptionSelection,
    runner: CommandRunner,
) -> Path:
    previous = set(workspace.glob("transcript*.vtt"))
    write_option = "--write-auto-subs" if selection.automatic else "--write-subs"
    execute(
        runner,
        [
            yt_dlp,
            "--skip-download",
            "--no-playlist",
            "--no-progress",
            write_option,
            "--sub-langs",
            selection.language,
            "--sub-format",
            "vtt",
            "--convert-subs",
            "vtt",
            "--output",
            str(workspace / "transcript.%(ext)s"),
            "--",
            url,
        ],
        "caption download",
    )
    return new_file(
        previous, sorted(workspace.glob("transcript*.vtt")), "VTT transcript"
    )


def download_video(
    yt_dlp: str, url: str, workspace: Path, runner: CommandRunner
) -> Path:
    output = execute(
        runner,
        [
            yt_dlp,
            "--no-playlist",
            "--no-progress",
            "--format",
            "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "--merge-output-format",
            "mp4",
            "--output",
            str(workspace / "video.%(ext)s"),
            "--print",
            "after_move:filepath",
            "--",
            url,
        ],
        "video download",
    )
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if not lines:
        raise PreparationError("yt-dlp did not report the downloaded video path.")
    video = Path(lines[-1]).resolve()
    workspace_root = workspace.resolve()
    if not video.is_relative_to(workspace_root) or not video.is_file():
        raise PreparationError("yt-dlp reported an invalid video path.")
    return video


def timestamp_seconds(value: str) -> float:
    parts = value.split(":")
    try:
        seconds = float(parts[-1])
        minutes = int(parts[-2])
        hours = int(parts[-3]) if len(parts) == 3 else 0
    except (ValueError, IndexError) as error:
        raise PreparationError(f"Invalid VTT timestamp: {value}") from error
    return hours * 3600 + minutes * 60 + seconds


def timestamp_label(value: str) -> str:
    return value if value.count(":") == 2 else f"00:{value}"


def timestamp_url(url: str, seconds: float) -> str:
    split = urlsplit(url)
    query = dict(parse_qsl(split.query, keep_blank_values=True))
    query["t"] = f"{math.floor(seconds)}s"
    return urlunsplit(
        (split.scheme, split.netloc, split.path, urlencode(query), split.fragment)
    )


def strip_vtt_markup(line: str) -> str:
    return html.unescape(INLINE_TAG_PATTERN.sub("", line))


def vtt_to_markdown(vtt: str, source_url: str) -> str:
    """Convert VTT control structure while retaining every cue and payload line."""
    normalized = vtt.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n{2,}", normalized.strip())
    rendered: list[str] = []
    for block in blocks:
        lines = block.splitlines()
        timing_index = next(
            (index for index, line in enumerate(lines) if TIMING_PATTERN.match(line)),
            None,
        )
        if timing_index is None:
            continue
        match = TIMING_PATTERN.match(lines[timing_index])
        assert match is not None
        payload = [strip_vtt_markup(line) for line in lines[timing_index + 1 :]]
        start = match.group("start")
        link = timestamp_url(source_url, timestamp_seconds(start))
        rendered.append(f"[{timestamp_label(start)}]({link})\n" + "\n".join(payload))
    if not rendered:
        raise PreparationError("The selected VTT contained no transcript cues.")
    return "\n\n".join(rendered) + "\n"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def transcribe_locally(
    ffmpeg: str,
    whisper: str,
    model: Path,
    language: str | None,
    video: Path,
    workspace: Path,
    runner: CommandRunner,
) -> tuple[Path, str, dict[str, object]]:
    audio = workspace / "audio.wav"
    execute(
        runner,
        [
            ffmpeg,
            "-y",
            "-i",
            str(video),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(audio),
        ],
        "audio extraction",
    )
    version = execute(runner, [whisper, "--version"], "whisper.cpp version").strip()
    output_base = workspace / "transcript"
    execute(
        runner,
        [
            whisper,
            "-m",
            str(model),
            "-f",
            str(audio),
            "-l",
            language or "auto",
            "-ovtt",
            "-ojf",
            "-of",
            str(output_base),
        ],
        "local transcription",
    )
    vtt_path = output_base.with_suffix(".vtt")
    json_path = output_base.with_suffix(".json")
    if not vtt_path.is_file() or not json_path.is_file():
        raise PreparationError(
            "whisper.cpp did not produce both VTT and full JSON outputs."
        )
    transcript_language = language or detected_transcript_language(json_path)
    provenance: dict[str, object] = {
        "backend": "whisper.cpp",
        "version": version,
        "model": model.name,
        "model_sha256": file_sha256(model),
        "language_mode": "specified" if language else "auto-detected",
        "full_json": json_path.relative_to(workspace).as_posix(),
    }
    return vtt_path, transcript_language, provenance


def detected_transcript_language(json_path: Path) -> str:
    try:
        parsed = object_mapping(json.loads(json_path.read_text(encoding="utf-8")))
    except json.JSONDecodeError as error:
        raise PreparationError("whisper.cpp returned invalid full JSON.") from error
    result = object_mapping(parsed.get("result"))
    language = result.get("language")
    if not isinstance(language, str) or not language or language == "auto":
        raise PreparationError(
            "whisper.cpp did not report the auto-detected transcript language."
        )
    return language


def video_duration(ffprobe: str, video: Path, runner: CommandRunner) -> float:
    output = execute(
        runner,
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(video),
        ],
        "video duration inspection",
    )
    try:
        parsed = object_mapping(json.loads(output))
        raw_duration = object_mapping(parsed.get("format")).get("duration", 0.0)
        if not isinstance(raw_duration, (int, float, str)):
            raise TypeError
        duration = float(raw_duration)
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        raise PreparationError("ffprobe returned an invalid video duration.") from error
    if duration <= 0:
        raise PreparationError("The downloaded video has no positive duration.")
    return duration


def limit_scene_frames(scenes: Sequence[SceneFrame], maximum: int) -> list[SceneFrame]:
    if maximum <= 0:
        raise PreparationError("Maximum scene frames must be positive.")
    if len(scenes) <= maximum:
        return list(scenes)
    if maximum == 1:
        return [scenes[0]]
    indices = [
        round(index * (len(scenes) - 1) / (maximum - 1)) for index in range(maximum)
    ]
    return [scenes[index] for index in indices]


def extract_interval_frames(
    ffmpeg: str,
    video: Path,
    directory: Path,
    interval: float,
    runner: CommandRunner,
) -> list[PreparedFrame]:
    if interval <= 0:
        raise PreparationError("Frame interval must be positive.")
    directory.mkdir()
    pattern = directory / "interval-%04d.jpg"
    execute(
        runner,
        [
            ffmpeg,
            "-y",
            "-i",
            str(video),
            "-vf",
            f"fps=1/{interval}:start_time=0,scale=min(1280\\,iw):-2",
            "-q:v",
            "2",
            str(pattern),
        ],
        "regular frame extraction",
    )
    paths = sorted(directory.glob("interval-*.jpg"))
    return [
        PreparedFrame(path.name, (index - 1) * interval)
        for index, path in enumerate(paths, start=1)
    ]


def extract_scene_frames(
    ffmpeg: str,
    video: Path,
    directory: Path,
    threshold: float,
    maximum: int,
    runner: CommandRunner,
) -> list[PreparedFrame]:
    if not 0 < threshold < 1:
        raise PreparationError("Scene threshold must be between zero and one.")
    directory.mkdir()
    result = runner(
        [
            ffmpeg,
            "-y",
            "-i",
            str(video),
            "-vf",
            f"scale=320:-2,select=gt(scene\\,{threshold}),showinfo",
            "-an",
            "-f",
            "null",
            "-",
        ]
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "no diagnostic output"
        raise PreparationError(f"scene frame extraction failed: {detail}")
    timestamps = [
        float(match.group("time"))
        for match in SCENE_TIME_PATTERN.finditer(result.stderr)
    ]
    selected_scenes = limit_scene_frames(
        [SceneFrame(timestamp) for timestamp in timestamps], maximum
    )
    prepared: list[PreparedFrame] = []
    for index, scene in enumerate(selected_scenes, start=1):
        destination = directory / f"scene-{index:04d}.jpg"
        execute(
            runner,
            [
                ffmpeg,
                "-y",
                "-ss",
                f"{scene.timestamp:.3f}",
                "-i",
                str(video),
                "-frames:v",
                "1",
                "-vf",
                "scale=min(1280\\,iw):-2",
                "-q:v",
                "2",
                str(destination),
            ],
            f"scene frame extraction at {scene.timestamp:.3f}s",
        )
        if not destination.is_file():
            raise PreparationError(
                f"FFmpeg did not create the scene frame at {scene.timestamp:.3f}s."
            )
        prepared.append(PreparedFrame(destination.name, scene.timestamp))
    return prepared


def create_contact_sheets(
    ffmpeg: str,
    directory: Path,
    prefix: str,
    frame_count: int,
    columns: int,
    rows: int,
    runner: CommandRunner,
) -> list[str]:
    if frame_count == 0:
        return []
    if columns <= 0 or rows <= 0:
        raise PreparationError("Contact-sheet dimensions must be positive.")
    pages = math.ceil(frame_count / (columns * rows))
    execute(
        runner,
        [
            ffmpeg,
            "-y",
            "-framerate",
            "1",
            "-i",
            str(directory / f"{prefix}-%04d.jpg"),
            "-vf",
            f"tile={columns}x{rows}:padding=4:margin=4",
            "-frames:v",
            str(pages),
            "-vsync",
            "vfr",
            str(directory / "sheet-%03d.jpg"),
        ],
        f"{prefix} contact-sheet creation",
    )
    sheets = sorted(directory.glob("sheet-*.jpg"))
    if len(sheets) != pages:
        raise PreparationError(
            f"Expected {pages} {prefix} contact sheet(s), found {len(sheets)}."
        )
    return [path.name for path in sheets]


def relative_frames(
    workspace: Path, directory: Path, frames: Sequence[PreparedFrame]
) -> list[dict[str, object]]:
    return [
        {
            "path": (directory / frame.path).relative_to(workspace).as_posix(),
            "timestamp": frame.timestamp,
        }
        for frame in frames
    ]


def canonical_source_url(metadata: Mapping[str, object], fallback: str) -> str:
    webpage_url = metadata.get("webpage_url")
    return webpage_url if isinstance(webpage_url, str) and webpage_url else fallback


def prepare_youtube(
    configuration: Configuration,
    *,
    runner: CommandRunner = run_command,
    resolver: CommandResolver = shutil.which,
) -> Path:
    """Prepare one source and return its manifest path."""
    yt_dlp = resolve_tool("yt-dlp", resolver)
    ffmpeg = resolve_tool("ffmpeg", resolver)
    ffprobe = resolve_tool("ffprobe", resolver)
    ensure_empty_workspace(configuration.workspace)

    metadata = fetch_metadata(yt_dlp, configuration.url, runner)
    source_json = configuration.workspace / "source.json"
    source_json.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    selection = select_caption(metadata, configuration.language)

    whisper: str | None = None
    if selection is None:
        if configuration.whisper_model is None:
            raise PreparationError(
                "No authored or original-language automatic captions were found. "
                "Configure local whisper.cpp with --whisper-model, or provide captions."
            )
        if not configuration.whisper_model.is_file():
            raise PreparationError(
                f"Whisper model does not exist: {configuration.whisper_model}"
            )
        whisper = resolve_tool(configuration.whisper_command, resolver)

    transcript_path: Path | None = None
    transcript_provenance: dict[str, object] = {}
    if selection is not None:
        transcript_path = download_caption(
            yt_dlp,
            configuration.url,
            configuration.workspace,
            selection,
            runner,
        )

    video = download_video(yt_dlp, configuration.url, configuration.workspace, runner)
    if selection is None:
        assert whisper is not None
        assert configuration.whisper_model is not None
        (
            transcript_path,
            transcript_language,
            transcript_provenance,
        ) = transcribe_locally(
            ffmpeg,
            whisper,
            configuration.whisper_model,
            configuration.language,
            video,
            configuration.workspace,
            runner,
        )
        selection = CaptionSelection("local-asr", transcript_language, True)
    assert transcript_path is not None

    source_url = canonical_source_url(metadata, configuration.url)
    transcript_markdown = configuration.workspace / "transcript.md"
    transcript_markdown.write_text(
        vtt_to_markdown(transcript_path.read_text(encoding="utf-8"), source_url),
        encoding="utf-8",
    )

    duration = video_duration(ffprobe, video, runner)
    interval_directory = configuration.workspace / "interval"
    scene_directory = configuration.workspace / "scene"
    interval_frames = extract_interval_frames(
        ffmpeg,
        video,
        interval_directory,
        configuration.interval_seconds,
        runner,
    )
    scene_frames = extract_scene_frames(
        ffmpeg,
        video,
        scene_directory,
        configuration.scene_threshold,
        configuration.max_scene_frames,
        runner,
    )
    interval_sheets = create_contact_sheets(
        ffmpeg,
        interval_directory,
        "interval",
        len(interval_frames),
        configuration.sheet_columns,
        configuration.sheet_rows,
        runner,
    )
    scene_sheets = create_contact_sheets(
        ffmpeg,
        scene_directory,
        "scene",
        len(scene_frames),
        configuration.sheet_columns,
        configuration.sheet_rows,
        runner,
    )

    manifest: dict[str, object] = {
        "source": {
            "id": metadata.get("id"),
            "title": metadata.get("title"),
            "url": source_url,
            "duration": duration,
            "metadata": source_json.name,
        },
        "transcript": {
            "origin": selection.origin,
            "language": selection.language,
            "evidence": transcript_path.relative_to(configuration.workspace).as_posix(),
            "markdown": transcript_markdown.name,
            **transcript_provenance,
        },
        "video": video.relative_to(configuration.workspace).as_posix(),
        "frames": {
            "interval": relative_frames(
                configuration.workspace, interval_directory, interval_frames
            ),
            "scene": relative_frames(
                configuration.workspace, scene_directory, scene_frames
            ),
            "interval_sheets": [
                (interval_directory / sheet)
                .relative_to(configuration.workspace)
                .as_posix()
                for sheet in interval_sheets
            ],
            "scene_sheets": [
                (scene_directory / sheet)
                .relative_to(configuration.workspace)
                .as_posix()
                for sheet in scene_sheets
            ],
        },
        "settings": {
            key: str(value) if isinstance(value, Path) else value
            for key, value in asdict(configuration).items()
            if key not in {"url", "workspace"}
        },
    }
    manifest_path = configuration.workspace / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare transcript and visual evidence for one YouTube video."
    )
    parser.add_argument("url")
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--language")
    parser.add_argument("--interval-seconds", type=float, default=60.0)
    parser.add_argument("--scene-threshold", type=float, default=0.35)
    parser.add_argument("--max-scene-frames", type=int, default=96)
    parser.add_argument("--sheet-columns", type=int, default=4)
    parser.add_argument("--sheet-rows", type=int, default=4)
    parser.add_argument("--whisper-command", default="whisper-cli")
    parser.add_argument("--whisper-model", type=Path)
    return parser


def configuration_from(arguments: argparse.Namespace) -> Configuration:
    return Configuration(
        url=cast(str, arguments.url),
        workspace=cast(Path, arguments.workspace),
        language=cast(str | None, arguments.language),
        interval_seconds=cast(float, arguments.interval_seconds),
        scene_threshold=cast(float, arguments.scene_threshold),
        max_scene_frames=cast(int, arguments.max_scene_frames),
        sheet_columns=cast(int, arguments.sheet_columns),
        sheet_rows=cast(int, arguments.sheet_rows),
        whisper_command=cast(str, arguments.whisper_command),
        whisper_model=cast(Path | None, arguments.whisper_model),
    )


def main() -> int:
    configuration = configuration_from(build_parser().parse_args())
    try:
        manifest = prepare_youtube(configuration)
    except PreparationError as error:
        print(f"Preparation failed: {error}", file=sys.stderr)
        if configuration.workspace.exists():
            print(f"Workspace preserved: {configuration.workspace}", file=sys.stderr)
        return 2
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
