import importlib.util
import tempfile
import unittest
from pathlib import Path

from cui.squoosh_cui import EncodeOptions, _compress_image, _validate_options


class TestSquooshCui(unittest.TestCase):
    def test_validate_options_normalizes(self):
        options = _validate_options(
            EncodeOptions(fmt="JPEG", quality=80, optimize=False)
        )
        self.assertEqual(options.fmt, "jpeg")
        self.assertEqual(options.quality, 80)

    def test_validate_options_rejects_quality(self):
        with self.assertRaises(ValueError):
            _validate_options(EncodeOptions(fmt="jpeg", quality=0, optimize=False))

    @unittest.skipUnless(
        importlib.util.find_spec("PIL") is not None, "Pillow not installed"
    )
    def test_compress_image_creates_output(self):
        from PIL import Image  # type: ignore

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "input.png"
            output_path = temp_path / "output.jpg"
            image = Image.new("RGB", (10, 10), color=(255, 0, 0))
            image.save(input_path)

            options = _validate_options(
                EncodeOptions(fmt="jpeg", quality=70, optimize=False)
            )
            _compress_image(input_path, output_path, options)

            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
