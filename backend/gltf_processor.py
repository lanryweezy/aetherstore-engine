import subprocess
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class GLTFProcessor:
    def __init__(self, executable: str = "gltf-transform"):
        self.executable = executable

    def is_available(self) -> bool:
        """Check if gltf-transform is installed and accessible."""
        try:
            subprocess.run([self.executable, "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def optimize_model(self, input_file: str, output_file: str, texture_resolution: int = 1024) -> bool:
        """
        Optimize a 3D model using gltf-transform's optimize command.
        This applies Draco compression and WebP texture compression.
        """
        if not self.is_available():
            logger.error("gltf-transform is not available.")
            return False

        # Build the optimize command
        cmd = [
            self.executable,
            "optimize",
            input_file,
            output_file,
            "--compress", "draco",
            "--texture-compress", "webp",
            "--texture-size", str(texture_resolution)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"gltf-transform optimization successful: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"gltf-transform optimization failed. Exit code: {e.returncode}")
            logger.error(f"Stdout: {e.stdout}")
            logger.error(f"Stderr: {e.stderr}")
            return False

# Global instance
gltf_processor = GLTFProcessor()
