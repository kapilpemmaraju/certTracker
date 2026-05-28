"""
Configuration Loader for Certification Workflow
================================================

This module provides configuration management with support for:
- YAML configuration files
- Environment variable substitution
- Configuration validation
- Default values
- Multiple configuration profiles

Author: IBM BOB
Date: 2026-05-21
"""

import yaml
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and manage workflow configuration."""
    
    def __init__(self, config_path: str = "config.yaml", profile: str = "default"):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to configuration file
            profile: Configuration profile to use
        """
        self.config_path = Path(config_path)
        self.profile = profile
        self.config = {}
        self._load_config()
    
    def _substitute_env_vars(self, value: Any) -> Any:
        """
        Recursively substitute environment variables in configuration values.
        
        Supports ${VAR_NAME} and ${VAR_NAME:default_value} syntax.
        
        Args:
            value: Configuration value (can be string, dict, list, etc.)
            
        Returns:
            Value with environment variables substituted
        """
        if isinstance(value, str):
            # Pattern: ${VAR_NAME} or ${VAR_NAME:default}
            pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
            
            def replace_env_var(match):
                var_name = match.group(1)
                default_value = match.group(2) if match.group(2) is not None else ""
                return os.getenv(var_name, default_value)
            
            return re.sub(pattern, replace_env_var, value)
        
        elif isinstance(value, dict):
            return {k: self._substitute_env_vars(v) for k, v in value.items()}
        
        elif isinstance(value, list):
            return [self._substitute_env_vars(item) for item in value]
        
        return value
    
    def _load_config(self):
        """Load configuration from YAML file."""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                raw_config = yaml.safe_load(f)
            
            # Substitute environment variables
            self.config = self._substitute_env_vars(raw_config)
            
            logger.info(f"Configuration loaded from: {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to configuration value (e.g., 'files.file_a.path')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to configuration value
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def get_file_path(self, file_key: str, base_dir: Optional[Path] = None) -> Path:
        """
        Get file path from configuration.
        
        Args:
            file_key: Configuration key for file (e.g., 'files.file_a.path')
            base_dir: Base directory for relative paths
            
        Returns:
            Absolute Path object
        """
        file_path = self.get(file_key)
        if not file_path:
            raise ValueError(f"File path not found in configuration: {file_key}")
        
        path = Path(file_path)
        
        # If relative path and base_dir provided, make it absolute
        if not path.is_absolute() and base_dir:
            path = base_dir / path
        
    
    def find_file_by_pattern(self, file_key: str, base_dir: Optional[Path] = None) -> Path:
        """
        Find file matching pattern from configuration.
        
        Args:
            file_key: Configuration key for file (e.g., 'files.file_a')
            base_dir: Base directory to search for files
            
        Returns:
            Path to the first matching file
            
        Raises:
            FileNotFoundError: If no matching file is found
        """
        import glob
        
        # Get pattern from config
        pattern_key = f"{file_key}.path_pattern"
        pattern = self.get(pattern_key)
        
        # If no pattern, fall back to exact path
        if not pattern:
            path_key = f"{file_key}.path"
            return self.get_file_path(path_key, base_dir)
        
        # Set base directory
        if base_dir is None:
            base_dir = Path.cwd()
        else:
            base_dir = Path(base_dir)
        
        # Search for matching files
        search_pattern = str(base_dir / pattern)
        matching_files = glob.glob(search_pattern)
        
        if not matching_files:
            # Try without base_dir (pattern might be absolute)
            matching_files = glob.glob(pattern)
        
        if not matching_files:
            raise FileNotFoundError(
                f"No files found matching pattern '{pattern}' in directory '{base_dir}'"
            )
        
        # Return the first (most recent if sorted) matching file
        matching_files.sort(reverse=True)  # Sort to get most recent first
        found_file = Path(matching_files[0])
        
        logger.info(f"Found file matching pattern '{pattern}': {found_file.name}")
        return found_file
    
    def get_worksheet_name(self, file_key: str, excel_file: Path) -> str:
        """
        Get worksheet name from configuration, supporting patterns.
        
        Args:
            file_key: Configuration key for file (e.g., 'files.file_b')
            excel_file: Path to Excel file to check worksheets
            
        Returns:
            Worksheet name
        """
        import openpyxl
        import fnmatch
        
        # Get pattern from config
        pattern_key = f"{file_key}.worksheet_pattern"
        pattern = self.get(pattern_key)
        
        # If no pattern, use exact worksheet name
        if not pattern:
            worksheet_key = f"{file_key}.worksheet"
            worksheet_name = self.get(worksheet_key)
            if not worksheet_name:
                raise ValueError(f"Worksheet name not found in configuration: {worksheet_key}")
            return worksheet_name
        
        # Load workbook and find matching worksheet
        try:
            wb = openpyxl.load_workbook(excel_file, read_only=True)
            sheet_names = wb.sheetnames
            wb.close()
            
            # Find matching worksheet
            for sheet_name in sheet_names:
                if fnmatch.fnmatch(sheet_name, pattern):
                    logger.info(f"Found worksheet matching pattern '{pattern}': {sheet_name}")
                    return sheet_name
            
            raise ValueError(
                f"No worksheet found matching pattern '{pattern}' in file '{excel_file.name}'. "
                f"Available worksheets: {sheet_names}"
            )
        except Exception as e:
            logger.error(f"Error finding worksheet: {e}")
            raise
        return path
    
    def validate(self) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if configuration is valid
        """
        required_keys = [
            'files.file_a.path',
            'files.file_a.email_column',
            'files.file_b.path',
            'files.file_b.email_column',
            'files.file_b.client_column',
            'processing.target_client'
        ]
        
        missing_keys = []
        for key in required_keys:
            if self.get(key) is None:
                missing_keys.append(key)
        
        if missing_keys:
            logger.error(f"Missing required configuration keys: {missing_keys}")
            return False
        
        logger.info("Configuration validation passed")
        return True
    
    def save(self, output_path: Optional[str] = None):
        """
        Save current configuration to file.
        
        Args:
            output_path: Path to save configuration (default: original path)
        """
        save_path = Path(output_path) if output_path else self.config_path
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Configuration saved to: {save_path}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise
    
    def get_all(self) -> Dict:
        """Get entire configuration dictionary."""
        return self.config.copy()
    
    def reload(self):
        """Reload configuration from file."""
        self._load_config()
        logger.info("Configuration reloaded")
    
    def __repr__(self) -> str:
        return f"ConfigLoader(config_path='{self.config_path}', profile='{self.profile}')"


class ConfigValidator:
    """Validate configuration values."""
    
    @staticmethod
    def validate_file_exists(path: Path) -> bool:
        """Check if file exists."""
        return path.exists() and path.is_file()
    
    @staticmethod
    def validate_directory_exists(path: Path) -> bool:
        """Check if directory exists."""
        return path.exists() and path.is_dir()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_port(port: int) -> bool:
        """Validate port number."""
        return 1 <= port <= 65535
    
    @staticmethod
    def validate_positive_int(value: int) -> bool:
        """Validate positive integer."""
        return isinstance(value, int) and value > 0


def load_config(config_path: str = "config.yaml", profile: str = "default") -> ConfigLoader:
    """
    Convenience function to load configuration.
    
    Args:
        config_path: Path to configuration file
        profile: Configuration profile to use
        
    Returns:
        ConfigLoader instance
    """
    return ConfigLoader(config_path, profile)


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Load configuration
    config = load_config("config.yaml")
    
    # Validate configuration
    if config.validate():
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration validation failed")
    
    # Access configuration values
    print(f"\nFile A path: {config.get('files.file_a.path')}")
    print(f"File B path: {config.get('files.file_b.path')}")
    print(f"Target client: {config.get('processing.target_client')}")
    print(f"Output directory: {config.get('files.output.directory')}")
    
    # Get file paths
    base_dir = Path.cwd()
    file_a_path = config.get_file_path('files.file_a.path', base_dir)
    print(f"\nFile A absolute path: {file_a_path}")

# Made with Bob
