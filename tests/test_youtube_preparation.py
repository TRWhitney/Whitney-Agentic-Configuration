from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import cast

SCRIPT_PATH = (
    Path(__file__).parents[1]
    / "skills"
    / "note-system"
    / "scripts"
    / "prepare_youtube.py"
)
SPEC = importlib.util.spec_from_file_location("youtube_preparation", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load {SCRIPT_PATH}")
youtube_preparation = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = youtube_preparation
ORIGINAL_DONT_WRITE_BYTECODE = sys.dont_write_bytecode
try:
    sys.dont_write_bytecode = True
    SPEC.loader.exec_module(youtube_preparation)
finally:
    sys.dont_write_bytecode = ORIGINAL_DONT_WRITE_BYTECODE


class CaptionSelectionTests(unittest.TestCase):
    def test_authored_caption_wins_over_automatic_caption(self) -> None:
        metadata = {
            "language": "en",
            "subtitles": {"en": [{"ext": "vtt"}]},
            "automatic_captions": {"en-orig": [{"ext": "vtt"}]},
        }

        selected = youtube_preparation.select_caption(metadata, None)

        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(selected.origin, "authored-caption")
        self.assertEqual(selected.language, "en")
        self.assertFalse(selected.automatic)

    def test_original_automatic_caption_wins_over_translations(self) -> None:
        metadata = {
            "language": "ja",
            "subtitles": {},
            "automatic_captions": {
                "en": [{"ext": "vtt", "name": "English"}],
                "ja-orig": [{"ext": "vtt", "name": "Japanese (Original)"}],
            },
        }

        selected = youtube_preparation.select_caption(metadata, None)

        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(selected.origin, "platform-auto-caption")
        self.assertEqual(selected.language, "ja-orig")

    def test_ambiguous_automatic_languages_require_an_explicit_language(self) -> None:
        metadata = {
            "subtitles": {},
            "automatic_captions": {
                "en": [{"ext": "vtt"}],
                "es": [{"ext": "vtt"}],
            },
        }

        with self.assertRaisesRegex(youtube_preparation.PreparationError, "--language"):
            youtube_preparation.select_caption(metadata, None)


class TranscriptConversionTests(unittest.TestCase):
    def test_vtt_conversion_preserves_cue_order_lines_and_repetition(self) -> None:
        vtt = """WEBVTT

00:00:01.200 --> 00:00:03.400 align:start
First line
second line

00:00:03.400 --> 00:00:04.000
First line

"""

        markdown = youtube_preparation.vtt_to_markdown(
            vtt, "https://www.youtube.com/watch?v=abc"
        )

        self.assertEqual(markdown.count("First line"), 2)
        self.assertIn("First line\nsecond line", markdown)
        self.assertIn("[00:00:01.200]", markdown)
        self.assertIn("watch?v=abc&t=1s", markdown)
        self.assertLess(markdown.index("second line"), markdown.rindex("First line"))

    def test_scene_limit_keeps_chronological_coverage(self) -> None:
        scenes = [
            youtube_preparation.SceneFrame(float(index * 10), float(index) / 10)
            for index in range(10)
        ]

        selected = youtube_preparation.limit_scene_frames(scenes, 4)

        self.assertEqual(
            [scene.timestamp for scene in selected], [0.0, 30.0, 60.0, 90.0]
        )


class FakeRunner:
    def __init__(self, metadata: dict[str, object]) -> None:
        self.metadata = metadata
        self.calls: list[list[str]] = []

    def __call__(self, arguments: list[str]) -> subprocess.CompletedProcess[str]:
        self.calls.append(arguments)
        if "--dump-single-json" in arguments:
            return subprocess.CompletedProcess(
                arguments, 0, json.dumps(self.metadata), ""
            )

        output_template = youtube_preparation.option_value(arguments, "--output")
        if "--write-subs" in arguments or "--write-auto-subs" in arguments:
            assert output_template is not None
            transcript = Path(output_template.replace("%(ext)s", "en.vtt"))
            transcript.write_text(
                "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nFaithful words\n",
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(arguments, 0, "", "")

        if "after_move:filepath" in arguments:
            assert output_template is not None
            video = Path(output_template.replace("%(ext)s", "mp4"))
            video.write_bytes(b"video")
            return subprocess.CompletedProcess(arguments, 0, f"{video}\n", "")

        if "-show_entries" in arguments:
            return subprocess.CompletedProcess(
                arguments, 0, '{"format":{"duration":"121.0"}}', ""
            )

        output = Path(arguments[-1])
        if output.name == "audio.wav":
            output.write_bytes(b"audio")
            return subprocess.CompletedProcess(arguments, 0, "", "")
        if arguments[0].endswith("whisper-cli"):
            if "--version" in arguments:
                return subprocess.CompletedProcess(
                    arguments, 0, "whisper.cpp 1.9.2", ""
                )
            output_base = youtube_preparation.option_value(arguments, "-of")
            assert output_base is not None
            Path(f"{output_base}.vtt").write_text(
                "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nGenerated words\n",
                encoding="utf-8",
            )
            Path(f"{output_base}.json").write_text(
                '{"result":{"language":"en"}}\n', encoding="utf-8"
            )
            return subprocess.CompletedProcess(arguments, 0, "", "")
        if "interval-%04d.jpg" in str(output):
            for index in range(1, 4):
                Path(str(output).replace("%04d", f"{index:04d}")).write_bytes(b"jpg")
            return subprocess.CompletedProcess(arguments, 0, "", "")
        if arguments[-1] == "-" and "showinfo" in " ".join(arguments):
            stderr = "pts_time:12.5\npts_time:88.0\n"
            return subprocess.CompletedProcess(arguments, 0, "", stderr)
        if output.name.startswith("scene-"):
            output.write_bytes(b"jpg")
            return subprocess.CompletedProcess(arguments, 0, "", "")
        if "sheet-%03d.jpg" in str(output):
            Path(str(output).replace("%03d", "001")).write_bytes(b"sheet")
            return subprocess.CompletedProcess(arguments, 0, "", "")
        raise AssertionError(f"Unexpected command: {arguments}")


class PreparationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)

    def resolver(self, command: str) -> str | None:
        if command in {"ffmpeg", "ffprobe", "yt-dlp"}:
            return f"/tools/{command}"
        return None

    def test_missing_base_dependency_fails_before_creating_workspace(self) -> None:
        workspace = self.root / "workspace"
        configuration = youtube_preparation.Configuration(
            url="https://youtu.be/abc", workspace=workspace
        )

        with self.assertRaisesRegex(youtube_preparation.PreparationError, "yt-dlp"):
            youtube_preparation.prepare_youtube(
                configuration,
                runner=lambda arguments: subprocess.CompletedProcess(
                    arguments, 0, "", ""
                ),
                resolver=lambda command: None,
            )

        self.assertFalse(workspace.exists())

    def test_no_caption_or_asr_fails_before_downloading_video(self) -> None:
        workspace = self.root / "workspace"
        runner = FakeRunner(
            {
                "id": "abc",
                "title": "No captions",
                "webpage_url": "https://youtu.be/abc",
                "subtitles": {},
                "automatic_captions": {},
            }
        )

        with self.assertRaisesRegex(youtube_preparation.PreparationError, "whisper"):
            youtube_preparation.prepare_youtube(
                youtube_preparation.Configuration(
                    url="https://youtu.be/abc", workspace=workspace
                ),
                runner=runner,
                resolver=self.resolver,
            )

        self.assertTrue((workspace / "source.json").is_file())
        self.assertFalse(any("after_move:filepath" in call for call in runner.calls))

    def test_caption_path_prepares_transcript_storyboards_and_manifest(self) -> None:
        workspace = self.root / "workspace"
        runner = FakeRunner(
            {
                "id": "abc",
                "title": "A useful video",
                "language": "en",
                "webpage_url": "https://www.youtube.com/watch?v=abc",
                "subtitles": {"en": [{"ext": "vtt"}]},
                "automatic_captions": {},
            }
        )

        manifest_path = youtube_preparation.prepare_youtube(
            youtube_preparation.Configuration(
                url="https://youtu.be/abc", workspace=workspace
            ),
            runner=runner,
            resolver=self.resolver,
        )

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["transcript"]["origin"], "authored-caption")
        self.assertEqual(
            [frame["timestamp"] for frame in manifest["frames"]["interval"]],
            [0.0, 60.0, 120.0],
        )
        self.assertEqual(
            [frame["timestamp"] for frame in manifest["frames"]["scene"]],
            [12.5, 88.0],
        )
        self.assertIn(
            "Faithful words",
            (workspace / "transcript.md").read_text(encoding="utf-8"),
        )
        self.assertTrue((workspace / "interval" / "sheet-001.jpg").is_file())
        self.assertTrue((workspace / "scene" / "sheet-001.jpg").is_file())

    def test_local_asr_records_backend_model_and_generated_origin(self) -> None:
        workspace = self.root / "workspace"
        model = self.root / "ggml-small.bin"
        model.write_bytes(b"model")
        runner = FakeRunner(
            {
                "id": "abc",
                "title": "No captions",
                "language": "en",
                "webpage_url": "https://youtu.be/abc",
                "subtitles": {},
                "automatic_captions": {},
            }
        )

        manifest_path = youtube_preparation.prepare_youtube(
            youtube_preparation.Configuration(
                url="https://youtu.be/abc",
                workspace=workspace,
                whisper_model=model,
            ),
            runner=runner,
            resolver=lambda command: f"/tools/{command}",
        )

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        transcript = manifest["transcript"]
        self.assertEqual(transcript["origin"], "local-asr")
        self.assertEqual(transcript["backend"], "whisper.cpp")
        self.assertEqual(transcript["model"], "ggml-small.bin")
        self.assertEqual(len(transcript["model_sha256"]), 64)
        whisper_call = next(call for call in runner.calls if "-ovtt" in call)
        self.assertIn("-ojf", whisper_call)
        self.assertIn(
            "Generated words",
            (workspace / "transcript.md").read_text(encoding="utf-8"),
        )

    def test_explicit_asr_language_controls_decoder_and_manifest(self) -> None:
        workspace = self.root / "workspace"
        model = self.root / "ggml-small.bin"
        model.write_bytes(b"model")
        runner = FakeRunner(
            {
                "id": "abc",
                "title": "No captions",
                "webpage_url": "https://youtu.be/abc",
                "subtitles": {},
                "automatic_captions": {},
            }
        )

        manifest_path = youtube_preparation.prepare_youtube(
            youtube_preparation.Configuration(
                url="https://youtu.be/abc",
                workspace=workspace,
                language="ja",
                whisper_model=model,
            ),
            runner=runner,
            resolver=lambda command: f"/tools/{command}",
        )

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["transcript"]["language"], "ja")
        whisper_call = next(call for call in runner.calls if "-ovtt" in call)
        language_index = whisper_call.index("-l")
        self.assertEqual(whisper_call[language_index + 1], "ja")


class BoundedSceneRunner:
    def __init__(self, scene_count: int) -> None:
        self.scene_count = scene_count
        self.calls: list[list[str]] = []

    def __call__(self, arguments: list[str]) -> subprocess.CompletedProcess[str]:
        self.calls.append(arguments)
        if arguments[-1] == "-":
            stderr = "\n".join(
                f"pts_time:{index * 10}.0" for index in range(self.scene_count)
            )
            return subprocess.CompletedProcess(arguments, 0, "", stderr)
        output = Path(arguments[-1])
        output.write_bytes(b"jpg")
        return subprocess.CompletedProcess(arguments, 0, "", "")


class SceneExtractionBoundaryTests(unittest.TestCase):
    def test_scene_limit_bounds_image_writes_before_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            video = root / "video.mp4"
            video.write_bytes(b"video")
            runner = BoundedSceneRunner(scene_count=1000)

            frames = youtube_preparation.extract_scene_frames(
                "/tools/ffmpeg",
                video,
                root / "scene",
                0.35,
                4,
                runner,
            )

            image_calls = [call for call in runner.calls if call[-1].endswith(".jpg")]
            self.assertEqual(len(image_calls), 4)
            self.assertTrue(all("%" not in call[-1] for call in image_calls))
            self.assertEqual(
                [frame.timestamp for frame in frames], [0.0, 3330.0, 6660.0, 9990.0]
            )

    def test_missing_extracted_scene_frame_is_a_fidelity_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            video = root / "video.mp4"
            video.write_bytes(b"video")

            def runner(arguments: list[str]) -> subprocess.CompletedProcess[str]:
                if arguments[-1] == "-":
                    return subprocess.CompletedProcess(arguments, 0, "", "pts_time:5.0")
                return subprocess.CompletedProcess(arguments, 0, "", "")

            with self.assertRaisesRegex(
                youtube_preparation.PreparationError, "scene frame"
            ):
                youtube_preparation.extract_scene_frames(
                    "/tools/ffmpeg",
                    video,
                    root / "scene",
                    0.35,
                    4,
                    runner,
                )


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg is not installed")
class RealFfmpegSmokeTests(unittest.TestCase):
    def test_frame_extractors_and_contact_sheets_process_synthetic_video(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            video = root / "video.mp4"
            generated = subprocess.run(
                [
                    cast(str, shutil.which("ffmpeg")),
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=red:d=1:s=320x240:r=10",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=blue:d=1:s=320x240:r=10",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=green:d=1:s=320x240:r=10",
                    "-filter_complex",
                    "[0:v][1:v][2:v]concat=n=3:v=1:a=0",
                    "-pix_fmt",
                    "yuv420p",
                    str(video),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            ffmpeg = cast(str, shutil.which("ffmpeg"))
            interval_directory = root / "interval"
            scene_directory = root / "scene"

            intervals = youtube_preparation.extract_interval_frames(
                ffmpeg,
                video,
                interval_directory,
                1.0,
                youtube_preparation.run_command,
            )
            scenes = youtube_preparation.extract_scene_frames(
                ffmpeg,
                video,
                scene_directory,
                0.1,
                12,
                youtube_preparation.run_command,
            )
            sheets = youtube_preparation.create_contact_sheets(
                ffmpeg,
                interval_directory,
                "interval",
                len(intervals),
                2,
                2,
                youtube_preparation.run_command,
            )

            self.assertGreaterEqual(len(intervals), 3)
            self.assertGreaterEqual(len(scenes), 2)
            self.assertEqual(sheets, ["sheet-001.jpg"])


if __name__ == "__main__":
    unittest.main()
