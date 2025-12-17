"""
Configuration management utilities
Loads and validates YAML config files
"""

from pathlib import Path
from typing import Any, Dict
import yaml


class ConfigManager:
    """Manages loading and accessing configuration files"""
    
    def __init__(self, config_dir: str = "configs"):
        """
        Initialize config manager
        
        Args:
            config_dir: Directory containing config files
        """
        self.config_dir = Path(config_dir)
        self._configs: Dict[str, Dict[str, Any]] = {}
    
    def load(self, config_name: str) -> Dict[str, Any]:
        """
        Load a configuration file
        
        Args:
            config_name: Name of config (without .yaml extension)
            
        Returns:
            Configuration dictionary
        """
        if config_name in self._configs:
            return self._configs[config_name]
        
        config_path = self.config_dir / f"{config_name}.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self._configs[config_name] = config
        return config
    
    def get(self, config_name: str, key: str, default: Any = None) -> Any:
        """
        Get a specific config value
        
        Args:
            config_name: Name of config file
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        config = self.load(config_name)
        
        # Support dot notation for nested keys
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def reload(self, config_name: str) -> Dict[str, Any]:
        """Force reload a configuration file"""
        if config_name in self._configs:
            del self._configs[config_name]
        return self.load(config_name)


# Global config manager instance
config_manager = ConfigManager()
