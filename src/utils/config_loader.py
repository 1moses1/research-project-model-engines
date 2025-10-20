"""
Configuration loader utility for loading YAML config files.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Utility class for loading and managing configuration files."""

    def __init__(self, config_dir: str = "config"):
        """
        Initialize ConfigLoader.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Configuration directory not found: {config_dir}")

    def load_config(self, config_file: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file.

        Args:
            config_file: Name of the configuration file (e.g., 'data_config.yaml')

        Returns:
            Dictionary containing configuration parameters
        """
        config_path = self.config_dir / config_file

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        return config

    def load_data_config(self) -> Dict[str, Any]:
        """Load data pipeline configuration."""
        return self.load_config('data_config.yaml')

    def load_model_config(self) -> Dict[str, Any]:
        """Load model training configuration."""
        return self.load_config('model_config.yaml')

    def get_nist_controls(self) -> list:
        """Get list of NIST SP 800-53 controls from config."""
        config = self.load_data_config()
        return config.get('controls', {}).get('nist_controls', [])

    def get_rwanda_controls(self) -> list:
        """Get list of Rwanda NCSA controls from config."""
        config = self.load_data_config()
        return config.get('controls', {}).get('rwanda_controls', [])

    def get_all_controls(self) -> Dict[str, list]:
        """Get all controls (NIST + Rwanda)."""
        config = self.load_data_config()
        return {
            'nist': self.get_nist_controls(),
            'rwanda': self.get_rwanda_controls()
        }


if __name__ == "__main__":
    # Test the config loader
    loader = ConfigLoader()

    # Load data config
    data_config = loader.load_data_config()
    print("Data Config Keys:", data_config.keys())

    # Load model config
    model_config = loader.load_model_config()
    print("Model Config Keys:", model_config.keys())

    # Get controls
    nist_controls = loader.get_nist_controls()
    rwanda_controls = loader.get_rwanda_controls()

    print(f"\nTotal NIST Controls: {len(nist_controls)}")
    print(f"Total Rwanda Controls: {len(rwanda_controls)}")
    print(f"Sample NIST: {nist_controls[:5]}")
    print(f"Sample Rwanda: {rwanda_controls[:5]}")
