import subprocess
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class BlenderProcessor:
    def __init__(self, blender_executable: str = "blender"):
        self.blender_executable = blender_executable
        self.scripts_dir = Path(__file__).parent / "blender_scripts"

    def is_blender_available(self) -> bool:
        """Check if Blender is installed and accessible."""
        try:
            subprocess.run([self.blender_executable, "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def optimize_model(self, input_file: str, output_file: str, decimation_ratio: float) -> bool:
        """
        Optimize a 3D model using Blender's Decimate modifier.

        Args:
            input_file: Path to the input 3D model.
            output_file: Path to save the optimized 3D model.
            decimation_ratio: The ratio of faces to keep (0.0 to 1.0).

        Returns:
            True if optimization was successful, False otherwise.
        """
        if not self.is_blender_available():
            logger.error("Blender is not available.")
            return False

        script_path = self.scripts_dir / "optimize.py"
        if not script_path.exists():
            logger.error(f"Blender script not found: {script_path}")
            return False

        cmd = [
            self.blender_executable,
            "--background",
            "--python", str(script_path),
            "--",
            input_file,
            output_file,
            str(decimation_ratio)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Blender optimization successful: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Blender optimization failed. Exit code: {e.returncode}")
            logger.error(f"Stdout: {e.stdout}")
            logger.error(f"Stderr: {e.stderr}")
            return False

    def render_thumbnails(self, input_file: str, output_dir: str) -> bool:
        """
        Render thumbnails using Blender's rendering engine.
        """
        if not self.is_blender_available():
            logger.error("Blender is not available.")
            return False

        script_path = self.scripts_dir / "render_thumbnails.py"
        if not script_path.exists():
            logger.error(f"Blender script not found: {script_path}")
            return False

        os.makedirs(output_dir, exist_ok=True)

        cmd = [
            self.blender_executable,
            "--background",
            "--python", str(script_path),
            "--",
            input_file,
            output_dir
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Blender thumbnail rendering successful: {output_dir}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Blender thumbnail rendering failed. Exit code: {e.returncode}")
            logger.error(f"Stdout: {e.stdout}")
            logger.error(f"Stderr: {e.stderr}")
            return False

# Global instance
blender_processor = BlenderProcessor()
