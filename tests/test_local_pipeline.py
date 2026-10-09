import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np

from background_remover import BackgroundRemover
from image_processor import ImageProcessor


class BackgroundTests(unittest.TestCase):
    def test_named_colors_remove_extreme_channel_values(self):
        remover = BackgroundRemover()
        for name, bgr in [('white', (255, 255, 255)), ('black', (0, 0, 0)),
                          ('green', (0, 255, 0)), ('blue', (255, 0, 0))]:
            with self.subTest(color=name):
                image = np.full((5, 5, 3), bgr, dtype=np.uint8)
                image[2, 2] = (100, 100, 100)
                result = remover.remove_color_background(image, color_name=name)
                self.assertEqual(result[0, 0, 3], 0)
                self.assertEqual(result[2, 2, 3], 255)

    def test_auto_detect_keeps_bgr_channel_order(self):
        image = np.full((5, 5, 3), (200, 80, 40), dtype=np.uint8)
        image[2, 2] = (40, 80, 200)
        result = BackgroundRemover().remove_color_background(image)
        self.assertEqual(result[0, 0, 3], 0)
        self.assertEqual(result[2, 2, 3], 255)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.processor = ImageProcessor()

    def image(self, path, alpha=False):
        path.parent.mkdir(parents=True, exist_ok=True)
        image = np.full((16, 16, 4 if alpha else 3), 255, dtype=np.uint8)
        image[4:12, 4:12, :3] = (40, 80, 200)
        if alpha:
            image[0:2, :, 3] = 0
            image[6:10, 6:10, 3] = 70
        self.assertTrue(cv2.imwrite(str(path), image))
        return image

    def test_process_creates_parent_and_preserves_source_alpha(self):
        source = self.root / 'source.png'
        original = self.image(source, alpha=True)
        original_bytes = source.read_bytes()
        output = self.root / 'nested' / 'result.png'
        self.assertTrue(self.processor.process_image(source, output, remove_watermark=False))
        actual = cv2.imread(str(output), cv2.IMREAD_UNCHANGED)
        np.testing.assert_array_equal(actual, original)
        self.assertEqual(source.read_bytes(), original_bytes)

    def test_background_forces_png_and_does_not_restore_transparent_pixels(self):
        source = self.root / 'source.png'
        original = self.image(source, alpha=True)
        original_bytes = source.read_bytes()
        requested = self.root / 'result.jpg'
        self.assertTrue(self.processor.process_image(
            source, requested, remove_watermark=False, remove_background=True, bg_color='white'))
        self.assertFalse(requested.exists())
        actual = cv2.imread(str(requested.with_suffix('.png')), cv2.IMREAD_UNCHANGED)
        self.assertEqual(actual[0, 0, 3], 0)
        np.testing.assert_array_equal(actual[6:10, 6:10, 3], original[6:10, 6:10, 3])
        self.assertEqual(source.read_bytes(), original_bytes)

    def test_writer_failure_is_reported(self):
        source = self.root / 'source.png'
        self.image(source)
        with patch('image_processor.cv2.imwrite', return_value=False):
            self.assertFalse(self.processor.process_image(
                source, self.root / 'result.png', remove_watermark=False))

    def test_source_cannot_be_overwritten(self):
        source = self.root / 'source.png'
        self.image(source)
        before = source.read_bytes()
        self.assertFalse(self.processor.process_image(
            source, source, remove_watermark=False, remove_background=True, bg_color='white'))
        self.assertEqual(source.read_bytes(), before)

    def test_recursive_rerun_excludes_output_tree(self):
        source = self.root / 'input' / 'sub' / 'source.png'
        self.image(source)
        before = source.read_bytes()
        for _ in range(2):
            self.assertEqual(self.processor.process_directory(
                self.root / 'input', recursive=True, remove_watermark=False), (1, 0))
        self.assertTrue((self.root / 'input' / 'output' / 'sub' / 'source.png').exists())
        self.assertFalse((self.root / 'input' / 'output' / 'output').exists())
        self.assertEqual(source.read_bytes(), before)

    def test_colliding_png_names_fail_without_overwriting(self):
        input_dir = self.root / 'input'
        self.image(input_dir / 'same.jpg')
        self.image(input_dir / 'same.png')
        self.assertEqual(self.processor.process_directory(
            input_dir, remove_watermark=False, remove_background=True, bg_color='white'), (0, 2))
        self.assertFalse((input_dir / 'output' / 'same.png').exists())

    def test_directory_rejects_in_place_output(self):
        input_dir = self.root / 'input'
        source = input_dir / 'source.png'
        self.image(source)
        before = source.read_bytes()
        self.assertEqual(self.processor.process_directory(
            input_dir, output_dir=input_dir, remove_watermark=False), (0, 1))
        self.assertEqual(source.read_bytes(), before)

    def test_cli_processes_local_fixture(self):
        source = self.root / 'source.png'
        self.image(source)
        output = self.root / 'cli.png'
        command = [sys.executable, str(Path(__file__).resolve().parents[1] / 'main.py'),
                   str(source), '-b', 'white', '-o', str(output)]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        actual = cv2.imread(str(output), cv2.IMREAD_UNCHANGED)
        self.assertEqual(actual[0, 0, 3], 0)
        self.assertEqual(actual[8, 8, 3], 255)

    def test_uppercase_png_uses_same_case_sensitive_target(self):
        input_dir = self.root / 'input'
        self.image(input_dir / 'photo.PNG')
        with patch('image_processor.os.path.normcase', side_effect=lambda value: value):
            result = self.processor.process_directory(
                input_dir, remove_watermark=False, remove_background=True, bg_color='white')
        self.assertEqual(result, (1, 0))
        output = input_dir / 'output' / 'photo.png'
        self.assertTrue(output.exists())
        actual = cv2.imread(str(output), cv2.IMREAD_UNCHANGED)
        self.assertEqual(actual[0, 0, 3], 0)
        self.assertEqual(actual[8, 8, 3], 255)

    def test_sixteen_bit_watermark_input_is_normalized(self):
        source = self.root / 'sixteen.png'
        image = np.full((16, 16, 3), 65535, dtype=np.uint16)
        self.assertTrue(cv2.imwrite(str(source), image))
        original_bytes = source.read_bytes()
        output = self.root / 'watermark.png'
        self.assertTrue(self.processor.process_image(source, output, remove_watermark=True))
        actual = cv2.imread(str(output), cv2.IMREAD_UNCHANGED)
        self.assertEqual(actual.dtype, np.uint8)
        np.testing.assert_array_equal(actual, np.full((16, 16, 3), 255, dtype=np.uint8))
        self.assertEqual(source.read_bytes(), original_bytes)

    def test_sixteen_bit_background_and_alpha_are_scaled_consistently(self):
        source = self.root / 'sixteen-alpha.png'
        image = np.full((16, 16, 4), 65535, dtype=np.uint16)
        image[4:12, 4:12, :3] = (40 * 257, 80 * 257, 200 * 257)
        image[0:2, :, 3] = 0
        image[6:10, 6:10, 3] = 70 * 257
        self.assertTrue(cv2.imwrite(str(source), image))
        original_bytes = source.read_bytes()
        output = self.root / 'background.png'
        self.assertTrue(self.processor.process_image(
            source, output, remove_watermark=True, remove_background=True, bg_color='white'))
        actual = cv2.imread(str(output), cv2.IMREAD_UNCHANGED)
        self.assertEqual(actual.dtype, np.uint8)
        self.assertEqual(actual[0, 0, 3], 0)
        self.assertEqual(actual[4, 8, 3], 255)
        self.assertEqual(actual[8, 8, 3], 70)
        self.assertEqual(source.read_bytes(), original_bytes)


if __name__ == '__main__':
    with contextlib.redirect_stdout(io.StringIO()):
        unittest.main()
