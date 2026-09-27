"""
Automated tests for organizer.py

Run from the 01-Smart-File-Organizer folder:
    python scripts/test_organizer.py

Every test works in its own temporary folder inside the project
(test_tmp_...), which is deleted afterwards. The real input/ and
output/ folders are never touched.
"""

import io
import re
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import organizer

PROJECT_DIR = Path(__file__).resolve().parent.parent


class OrganizerTestCase(unittest.TestCase):
    """Shared set-up: a fresh, empty sandbox for every test."""

    def setUp(self):
        # A temporary folder inside the project, removed in tearDown()
        self.sandbox = Path(tempfile.mkdtemp(prefix="test_tmp_", dir=PROJECT_DIR))
        self.input_dir = self.sandbox / "input"
        self.output_dir = self.sandbox / "output"
        self.input_dir.mkdir()
        self.output_dir.mkdir()

        # Point the organizer at the sandbox instead of the real folders
        patches = [
            mock.patch.object(organizer, "INPUT_DIR", self.input_dir),
            mock.patch.object(organizer, "OUTPUT_DIR", self.output_dir),
            mock.patch.object(organizer, "LOG_FILE",
                              self.output_dir / "organization_log.txt"),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def tearDown(self):
        shutil.rmtree(self.sandbox)

    # ---- helpers -------------------------------------------------------

    def make_file(self, name, content=None):
        """Create a file in the sandbox input folder. Content defaults to its name."""
        path = self.input_dir / name
        path.write_text(content if content is not None else f"content of {name}")
        return path

    def run_organizer(self, *options):
        """Run organizer.main() with options; return (exit_code, printed_text)."""
        printed = io.StringIO()
        with mock.patch.object(sys, "argv", ["organizer.py", *options]):
            with redirect_stdout(printed):
                exit_code = organizer.main()
        return exit_code, printed.getvalue()

    def snapshot(self):
        """Every file/folder in the sandbox with its content, for before/after checks."""
        result = {}
        for path in sorted(self.sandbox.rglob("*")):
            relative = str(path.relative_to(self.sandbox))
            result[relative] = path.read_text() if path.is_file() else "<folder>"
        return result

    def log_lines(self):
        log = self.output_dir / "organization_log.txt"
        return log.read_text().splitlines() if log.exists() else []


class TestClassification(OrganizerTestCase):
    """The rules that pick a folder for each extension."""

    def test_known_extensions(self):
        expected = {
            "a.pdf": "PDFs", "a.jpg": "Images", "a.jpeg": "Images",
            "a.png": "Images", "a.xls": "Excel", "a.xlsx": "Excel",
            "a.doc": "Word", "a.docx": "Word", "a.ppt": "PowerPoint",
            "a.pptx": "PowerPoint", "a.txt": "Text",
        }
        for name, folder in expected.items():
            with self.subTest(name=name):
                self.assertEqual(organizer.classify(Path(name)), folder)

    def test_extension_is_case_insensitive(self):
        self.assertEqual(organizer.classify(Path("SCAN.PDF")), "PDFs")
        self.assertEqual(organizer.classify(Path("Photo.JpG")), "Images")

    def test_unknown_and_missing_extensions_go_to_other(self):
        for name in ["song.mp3", "data.xyz", "LICENSE", "archive.tar.gz"]:
            with self.subTest(name=name):
                self.assertEqual(organizer.classify(Path(name)), "Other")


class TestNormalFiles(OrganizerTestCase):
    """Test 1: the nine sample files from the project brief."""

    SAMPLES = {
        "report.pdf": "PDFs", "invoice.pdf": "PDFs", "photo.jpg": "Images",
        "hospital.png": "Images", "equipment.xlsx": "Excel",
        "employees.xlsx": "Excel", "notes.txt": "Text",
        "proposal.docx": "Word", "presentation.pptx": "PowerPoint",
    }

    def test_files_move_to_correct_folders(self):
        for name in self.SAMPLES:
            self.make_file(name)

        exit_code, output = self.run_organizer()

        self.assertEqual(exit_code, 0)
        self.assertIn("Done: 9 moved", output)
        self.assertEqual(list(self.input_dir.iterdir()), [], "input should be empty")
        for name, folder in self.SAMPLES.items():
            moved = self.output_dir / folder / name
            self.assertTrue(moved.exists(), f"{name} missing from {folder}/")
            # The content must survive the move unchanged
            self.assertEqual(moved.read_text(), f"content of {name}")

    def test_all_category_folders_are_created(self):
        self.make_file("report.pdf")
        self.run_organizer()
        for folder in ["PDFs", "Images", "Excel", "Word", "PowerPoint", "Text", "Other"]:
            self.assertTrue((self.output_dir / folder).is_dir(), f"{folder}/ missing")

    def test_log_records_every_file(self):
        for name in self.SAMPLES:
            self.make_file(name)
        self.run_organizer()

        lines = self.log_lines()
        self.assertEqual(len(lines), 9)
        # Format: 2026-09-27 14:30:05 | report.pdf | PDFs/ | MOVED
        pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| report\.pdf \| PDFs/ \| MOVED$"
        self.assertTrue(any(re.match(pattern, line) for line in lines), lines)

    def test_log_is_appended_not_replaced(self):
        self.make_file("report.pdf")
        self.run_organizer()
        self.make_file("notes.txt")
        self.run_organizer()
        self.assertEqual(len(self.log_lines()), 2)


class TestDuplicates(OrganizerTestCase):
    """Test 2: same filename arriving more than once."""

    def test_duplicates_are_renamed_and_nothing_is_overwritten(self):
        pdfs = self.output_dir / "PDFs"
        for version in ["first", "second", "third"]:
            self.make_file("report.pdf", version)
            exit_code, _ = self.run_organizer()
            self.assertEqual(exit_code, 0)

        self.assertEqual((pdfs / "report.pdf").read_text(), "first")
        self.assertEqual((pdfs / "report_1.pdf").read_text(), "second")
        self.assertEqual((pdfs / "report_2.pdf").read_text(), "third")
        self.assertIn("renamed to report_2.pdf", self.log_lines()[-1])

    def test_duplicate_without_extension(self):
        self.make_file("LICENSE", "one")
        self.run_organizer()
        self.make_file("LICENSE", "two")
        self.run_organizer()
        self.assertEqual((self.output_dir / "Other" / "LICENSE_1").read_text(), "two")

    def test_incoming_name_that_looks_like_a_renamed_file(self):
        # report_1.pdf is already taken by a renamed file; a *real*
        # report_1.pdf arriving must not overwrite it
        for version in ["a", "b"]:
            self.make_file("report.pdf", version)
            self.run_organizer()
        self.make_file("report_1.pdf", "c")
        self.run_organizer()

        pdfs = self.output_dir / "PDFs"
        self.assertEqual((pdfs / "report_1.pdf").read_text(), "b")
        self.assertEqual((pdfs / "report_1_1.pdf").read_text(), "c")


class TestUnknownExtensions(OrganizerTestCase):
    """Test 3: unsupported types go to Other/ and are reported."""

    def test_unknown_files_go_to_other_and_are_listed(self):
        for name in ["song.mp3", "data.xyz", "LICENSE"]:
            self.make_file(name)

        exit_code, output = self.run_organizer()

        self.assertEqual(exit_code, 0)
        for name in ["song.mp3", "data.xyz", "LICENSE"]:
            self.assertTrue((self.output_dir / "Other" / name).exists())
            self.assertIn(f"  - {name}", output)
        self.assertIn("[unknown type: .mp3]", output)
        self.assertIn("[unknown type: no extension]", output)
        self.assertTrue(any("[unknown type: .xyz]" in l for l in self.log_lines()))


class TestEmptyInput(OrganizerTestCase):
    """Test 4: nothing to do."""

    def test_empty_input_folder(self):
        exit_code, output = self.run_organizer()
        self.assertEqual(exit_code, 0)
        self.assertIn("Nothing to organize", output)
        self.assertEqual(list(self.output_dir.iterdir()), [], "output should stay empty")

    def test_hidden_files_are_ignored(self):
        self.make_file(".gitkeep", "")
        exit_code, output = self.run_organizer()
        self.assertEqual(exit_code, 0)
        self.assertIn("Nothing to organize", output)
        self.assertTrue((self.input_dir / ".gitkeep").exists())

    def test_subfolders_are_reported_not_silently_ignored(self):
        (self.input_dir / "Holiday Photos").mkdir()
        self.make_file("report.pdf")

        exit_code, output = self.run_organizer()

        self.assertEqual(exit_code, 0)
        self.assertIn("Holiday Photos", output)
        self.assertTrue((self.input_dir / "Holiday Photos").is_dir(), "subfolder must stay put")
        self.assertTrue((self.output_dir / "PDFs" / "report.pdf").exists())

    def test_only_subfolders_are_reported(self):
        (self.input_dir / "Holiday Photos").mkdir()
        exit_code, output = self.run_organizer()
        self.assertEqual(exit_code, 0)
        self.assertIn("Holiday Photos", output)


class TestMissingInput(OrganizerTestCase):
    """Test 5: the input folder is not there (or is not a folder)."""

    def test_missing_input_folder(self):
        self.input_dir.rmdir()
        exit_code, output = self.run_organizer()
        self.assertEqual(exit_code, 1)
        self.assertIn("ERROR: the input folder does not exist", output)
        self.assertEqual(list(self.output_dir.iterdir()), [], "nothing should be created")

    def test_input_is_a_file(self):
        self.input_dir.rmdir()
        self.input_dir.write_text("oops")
        exit_code, output = self.run_organizer()
        self.assertEqual(exit_code, 1)
        self.assertIn("is a file, not a folder", output)


class TestDryRun(OrganizerTestCase):
    """Test 6: --dry-run must preview accurately and change nothing."""

    def test_dry_run_changes_nothing(self):
        for name in ["report.pdf", "photo.jpg", "song.mp3"]:
            self.make_file(name)
        before = self.snapshot()

        exit_code, output = self.run_organizer("--dry-run")

        self.assertEqual(exit_code, 0)
        self.assertEqual(self.snapshot(), before, "dry run changed something")
        self.assertIn("DRY RUN", output)
        self.assertIn("WOULD MOVE", output)
        self.assertNotIn("MOVED", output.replace("WOULD MOVE", ""))

    def test_dry_run_predicts_renames_correctly(self):
        self.make_file("report.pdf", "first")
        self.run_organizer()
        self.make_file("report.pdf", "second")

        _, preview = self.run_organizer("--dry-run")
        _, real = self.run_organizer()

        self.assertIn("WOULD MOVE (renamed to report_1.pdf)", preview)
        self.assertIn("MOVED (renamed to report_1.pdf)", real)


class TestManyFiles(OrganizerTestCase):
    """Test 7: a large batch of mixed files."""

    def test_one_thousand_files(self):
        extensions = ["pdf", "jpg", "png", "xlsx", "docx", "pptx", "txt", "zip"]
        for i in range(1000):
            self.make_file(f"file_{i:04d}.{extensions[i % len(extensions)]}")

        exit_code, output = self.run_organizer()

        self.assertEqual(exit_code, 0)
        self.assertIn("Done: 1000 moved", output)
        self.assertEqual(list(self.input_dir.iterdir()), [])
        moved = [p for p in self.output_dir.rglob("*") if p.is_file()
                 and p.name != "organization_log.txt"]
        self.assertEqual(len(moved), 1000)
        self.assertEqual(len(list((self.output_dir / "Other").iterdir())), 125)  # .zip
        self.assertEqual(len(self.log_lines()), 1000)


class TestErrors(OrganizerTestCase):
    """Error handling: one bad file must not stop the others."""

    def test_locked_file_is_reported_and_others_still_move(self):
        for name in ["report.pdf", "photo.jpg", "notes.txt"]:
            self.make_file(name)

        real_move = shutil.move

        def fake_move(src, dst):
            # Pretend photo.jpg is open in another program
            if src.endswith("photo.jpg"):
                raise PermissionError(13, "Permission denied", src)
            return real_move(src, dst)

        with mock.patch.object(organizer.shutil, "move", fake_move):
            exit_code, output = self.run_organizer()

        self.assertEqual(exit_code, 1)
        self.assertIn("photo.jpg", output)
        self.assertIn("permission denied", output)
        self.assertTrue((self.input_dir / "photo.jpg").exists(), "photo.jpg must stay in input")
        self.assertTrue((self.output_dir / "PDFs" / "report.pdf").exists())
        self.assertTrue((self.output_dir / "Text" / "notes.txt").exists())
        self.assertTrue(any("ERROR" in l and "photo.jpg" in l for l in self.log_lines()))

    def test_output_folder_blocked(self):
        self.make_file("report.pdf")
        (self.output_dir / "PDFs").write_text("a file where a folder should be")

        exit_code, output = self.run_organizer()

        self.assertEqual(exit_code, 1)
        self.assertIn("No files were moved", output)
        self.assertTrue((self.input_dir / "report.pdf").exists())

    def test_log_unavailable_still_organizes(self):
        self.make_file("report.pdf")
        (self.output_dir / "organization_log.txt").mkdir()  # can't write to a folder

        exit_code, output = self.run_organizer()

        self.assertEqual(exit_code, 1)
        self.assertIn("could not write to the log file", output)
        self.assertTrue((self.output_dir / "PDFs" / "report.pdf").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
