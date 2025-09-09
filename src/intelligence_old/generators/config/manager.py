# src/intelligence/generators/config/manager.py
"""
CONFIGURATION MANAGEMENT SYSTEM
🔧 Centralized configuration for all generators
⚡ Hot-reloading and validation
📊 Performance-based auto-tuning
🎯 Environment-specific settings
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, asdict, field
import os
import yaml

logger = logging.getLogger(__name__)

@dataclass
class ProviderConfig:
    """Configuration for AI providers"""
    name: str
    api_key_env: str
    base_url: Optional[str] = None
    models: Dict[str, str] = field(default_factory=dict)
    cost_per_1k_tokens: float = 0.001
    rate_limit_rpm: int = 60
    timeout_seconds: int = 30
    priority: int = 1  # Lower = higher priority
    enabled: bool = True

@dataclass
class ContentTypeConfig:
    """Configuration for content types"""
    name: str
    preferred_providers: List[str] = field(default_factory=list)
    quality_threshold: float = 0.7
    max_tokens: int = 2000
    temperature: float = 0.7
    cost_budget_per_generation: float = 0.01
    timeout_seconds: int = 45
    retry_count: int = 3

@dataclass
class GeneratorConfig:
    """Enhanced generator configuration"""
    name: str
    module_path: str
    class_name: str
    enabled: bool = True
    supported_content_types: List[str] = field(default_factory=list)
    cost_tier: str = "ultra_cheap"
    health_check_interval: int = 300
    max_concurrent_generations: int = 5
    cache_results: bool = False
    cache_ttl_seconds: int = 3600

@dataclass
class FactoryConfig:
    """Main factory configuration"""
    lazy_loading: bool = True
    health_monitoring: bool = True
    cost_optimization: bool = True
    auto_fallback: bool = True
    metrics_collection: bool = True
    log_level: str = "INFO"
    max_generation_time: int = 120  # seconds
    cleanup_interval: int = 1800  # 30 minutes

class ConfigurationManager:
    """Centralized configuration management with hot-reloading"""
    
    def __init__(self, config_dir: str = "config/generators"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration storage
        self.providers: Dict[str, ProviderConfig] = {}
        self.content_types: Dict[str, ContentTypeConfig] = {}
        self.generators: Dict[str, GeneratorConfig] = {}
        self.factory_config: FactoryConfig = FactoryConfig()
        
        # Hot-reload tracking
        self._file_watchers = {}
        self._last_reload = datetime.now(timezone.utc)
        self._reload_callbacks = []
        
        # Load configurations
        self._initialize_default_configs()
        self._load_configurations()
        
        logger.info(f"🔧 Configuration Manager initialized: {len(self.providers)} providers, {len(self.generators)} generators")
    
    def _initialize_default_configs(self):
        """Initialize default configurations"""
        
        # Default provider configurations
        self.providers = {
            "groq": ProviderConfig(
                name="groq",
                api_key_env="GROQ_API_KEY",
                models={
                    "text": "llama-3.3-70b-versatile",
                    "chat": "llama-3.3-70b-versatile"
                },
                cost_per_1k_tokens=0.00013,
                rate_limit_rpm=30,
                priority=1
            ),
            "deepseek": ProviderConfig(
                name="deepseek",
                api_key_env="DEEPSEEK_API_KEY",
                base_url="https://api.deepseek.com",
                models={
                    "text": "deepseek-chat",
                    "reasoning": "deepseek-reasoner"
                },
                cost_per_1k_tokens=0.00089,
                rate_limit_rpm=60,
                priority=2
            ),
            "together": ProviderConfig(
                name="together",
                api_key_env="TOGETHER_API_KEY",
                base_url="https://api.together.xyz/v1",
                models={
                    "text": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
                },
                cost_per_1k_tokens=0.0008,
                rate_limit_rpm=60,
                priority=3
            ),
            "anthropic": ProviderConfig(
                name="anthropic",
                api_key_env="ANTHROPIC_API_KEY",
                models={
                    "text": "claude-sonnet-4-20250514",
                    "reasoning": "claude-sonnet-4-20250514"
                },
                cost_per_1k_tokens=0.009,
                rate_limit_rpm=50,
                priority=4
            )
        }
        
        # Default content type configurations
        self.content_types = {
            "email_sequence": ContentTypeConfig(
                name="email_sequence",
                preferred_providers=["groq", "deepseek", "together"],
                quality_threshold=0.7,
                max_tokens=3000,
                temperature=0.8,
                cost_budget_per_generation=0.005
            ),
            "social_posts": ContentTypeConfig(
                name="social_posts",
                preferred_providers=["groq", "deepseek"],
                quality_threshold=0.75,
                max_tokens=1500,
                temperature=0.9,
                cost_budget_per_generation=0.003
            ),
            "ad_copy": ContentTypeConfig(
                name="ad_copy",
                preferred_providers=["anthropic", "deepseek", "groq"],
                quality_threshold=0.8,
                max_tokens=2000,
                temperature=0.7,
                cost_budget_per_generation=0.008
            ),
            "blog_post": ContentTypeConfig(
                name="blog_post",
                preferred_providers=["anthropic", "deepseek"],
                quality_threshold=0.85,
                max_tokens=4000,
                temperature=0.6,
                cost_budget_per_generation=0.015
            ),
            "landing_page": ContentTypeConfig(
                name="landing_page",
                preferred_providers=["anthropic", "together"],
                quality_threshold=0.9,
                max_tokens=5000,
                temperature=0.5,
                cost_budget_per_generation=0.025
            )
        }
        
        # Default generator configurations
        self.generators = {
            "email_sequence": GeneratorConfig(
                name="email_sequence",
                module_path="email_generator",
                class_name="EmailSequenceGenerator",
                supported_content_types=["email_sequence", "email_campaign"],
                max_concurrent_generations=3
            ),
            "social_posts": GeneratorConfig(
                name="social_posts",
                module_path="social_media_generator",
                class_name="SocialMediaGenerator",
                supported_content_types=["social_posts", "SOCIAL_POSTS", "social_media"],
                max_concurrent_generations=5
            ),
            "ad_copy": GeneratorConfig(
                name="ad_copy",
                module_path="ad_copy_generator",
                class_name="AdCopyGenerator",
                supported_content_types=["ad_copy", "ads", "advertising"],
                max_concurrent_generations=4
            ),
            "blog_post": GeneratorConfig(
                name="blog_post",
                module_path="blog_post_generator",
                class_name="BlogPostGenerator",
                supported_content_types=["blog_post", "article", "content"],
                max_concurrent_generations=2
            ),
            "landing_page": GeneratorConfig(
                name="landing_page",
                module_path="landing_page.core.generator",
                class_name="LandingPageGenerator",
                supported_content_types=["landing_page", "webpage", "page"],
                max_concurrent_generations=2
            )
        }
    
    def _load_configurations(self):
        """Load configurations from files"""
        
        config_files = {
            "providers.yaml": self._load_providers_config,
            "content_types.yaml": self._load_content_types_config,
            "generators.yaml": self._load_generators_config,
            "factory.yaml": self._load_factory_config
        }
        
        for filename, loader_func in config_files.items():
            file_path = self.config_dir / filename
            
            if file_path.exists():
                try:
                    loader_func(file_path)
                    logger.info(f"📋 Loaded configuration from {filename}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load {filename}: {e}")
            else:
                # Create default config file
                self._create_default_config_file(filename)
    
    def _load_providers_config(self, file_path: Path):
        """Load providers configuration"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        for provider_name, config_data in data.get("providers", {}).items():
            self.providers[provider_name] = ProviderConfig(**config_data)
    
    def _load_content_types_config(self, file_path: Path):
        """Load content types configuration"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        for content_type, config_data in data.get("content_types", {}).items():
            self.content_types[content_type] = ContentTypeConfig(**config_data)
    
    def _load_generators_config(self, file_path: Path):
        """Load generators configuration"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        for generator_name, config_data in data.get("generators", {}).items():
            self.generators[generator_name] = GeneratorConfig(**config_data)
    
    def _load_factory_config(self, file_path: Path):
        """Load factory configuration"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        factory_data = data.get("factory", {})
        if factory_data:
            self.factory_config = FactoryConfig(**factory_data)
    
    def _create_default_config_file(self, filename: str):
        """Create default configuration files"""
        file_path = self.config_dir / filename
        
        try:
            if filename == "providers.yaml":
                config_data = {
                    "providers": {name: asdict(config) for name, config in self.providers.items()}
                }
            elif filename == "content_types.yaml":
                config_data = {
                    "content_types": {name: asdict(config) for name, config in self.content_types.items()}
                }
            elif filename == "generators.yaml":
                config_data = {
                    "generators": {name: asdict(config) for name, config in self.generators.items()}
                }
            elif filename == "factory.yaml":
                config_data = {
                    "factory": asdict(self.factory_config)
                }
            else:
                return
            
            with open(file_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            logger.info(f"📄 Created default config file: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create {filename}: {e}")
    
    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """Get provider configuration"""
        return self.providers.get(provider_name)
    
    def get_content_type_config(self, content_type: str) -> Optional[ContentTypeConfig]:
        """Get content type configuration"""
        return self.content_types.get(content_type)
    
    def get_generator_config(self, generator_name: str) -> Optional[GeneratorConfig]:
        """Get generator configuration"""
        return self.generators.get(generator_name)
    
    def get_optimal_providers_for_content_type(self, content_type: str) -> List[str]:
        """Get optimal providers for content type based on configuration and performance"""
        
        content_config = self.get_content_type_config(content_type)
        if not content_config:
            # Return all available providers sorted by priority
            return self._get_available_providers_by_priority()
        
        # Filter preferred providers by availability
        available_providers = []
        for provider_name in content_config.preferred_providers:
            provider_config = self.get_provider_config(provider_name)
            if provider_config and provider_config.enabled and self._is_provider_available(provider_name):
                available_providers.append(provider_name)
        
        # Add other available providers as fallbacks
        for provider_name in self._get_available_providers_by_priority():
            if provider_name not in available_providers:
                available_providers.append(provider_name)
        
        return available_providers
    
    def _get_available_providers_by_priority(self) -> List[str]:
        """Get available providers sorted by priority"""
        available = [
            (name, config) for name, config in self.providers.items()
            if config.enabled and self._is_provider_available(name)
        ]
        
        # Sort by priority (lower number = higher priority)
        available.sort(key=lambda x: x[1].priority)
        
        return [name for name, _ in available]
    
    def _is_provider_available(self, provider_name: str) -> bool:
        """Check if provider is available (has API key)"""
        provider_config = self.get_provider_config(provider_name)
        if not provider_config:
            return False
        
        api_key = os.getenv(provider_config.api_key_env)
        return api_key is not None and len(api_key.strip()) > 0
    
    def update_provider_performance(self, provider_name: str, metrics: Dict[str, Any]):
        """Update provider performance metrics for optimization"""
        
        provider_config = self.get_provider_config(provider_name)
        if not provider_config:
            return
        
        # Auto-adjust priority based on performance
        success_rate = metrics.get("success_rate", 1.0)
        avg_response_time = metrics.get("avg_response_time", 1.0)
        cost_efficiency = metrics.get("cost_efficiency", 1.0)
        
        # Calculate performance score (0-1, higher is better)
        performance_score = (success_rate * 0.5) + (cost_efficiency * 0.3) + (min(1.0, 2.0 / avg_response_time) * 0.2)
        
        # Adjust priority based on performance (lower number = higher priority)
        if performance_score > 0.8:
            provider_config.priority = max(1, provider_config.priority - 1)
        elif performance_score < 0.5:
            provider_config.priority = min(10, provider_config.priority + 1)
        
        logger.debug(f"🎯 Updated {provider_name} priority to {provider_config.priority} (score: {performance_score:.2f})")
    
    def auto_tune_content_type_config(self, content_type: str, performance_data: Dict[str, Any]):
        """Auto-tune content type configuration based on performance"""
        
        content_config = self.get_content_type_config(content_type)
        if not content_config:
            return
        
        # Adjust quality threshold based on actual results
        actual_quality = performance_data.get("avg_quality_score", content_config.quality_threshold)
        if actual_quality > content_config.quality_threshold + 0.1:
            content_config.quality_threshold = min(0.95, content_config.quality_threshold + 0.05)
        elif actual_quality < content_config.quality_threshold - 0.1:
            content_config.quality_threshold = max(0.5, content_config.quality_threshold - 0.05)
        
        # Adjust cost budget based on actual costs
        actual_cost = performance_data.get("avg_cost", content_config.cost_budget_per_generation)
        if actual_cost < content_config.cost_budget_per_generation * 0.5:
            content_config.cost_budget_per_generation = max(0.001, content_config.cost_budget_per_generation * 0.8)
        elif actual_cost > content_config.cost_budget_per_generation * 1.2:
            content_config.cost_budget_per_generation = min(0.1, content_config.cost_budget_per_generation * 1.2)
        
        logger.debug(f"🔧 Auto-tuned {content_type}: quality_threshold={content_config.quality_threshold:.2f}, cost_budget=${content_config.cost_budget_per_generation:.4f}")
    
    def validate_configuration(self) -> Dict[str, List[str]]:
        """Validate all configurations and return issues"""
        
        issues = {
            "providers": [],
            "content_types": [],
            "generators": [],
            "factory": []
        }
        
        # Validate providers
        for provider_name, config in self.providers.items():
            if not config.api_key_env:
                issues["providers"].append(f"{provider_name}: Missing api_key_env")
            
            if config.cost_per_1k_tokens <= 0:
                issues["providers"].append(f"{provider_name}: Invalid cost_per_1k_tokens")
            
            if not config.models:
                issues["providers"].append(f"{provider_name}: No models configured")
        
        # Validate content types
        for content_type, config in self.content_types.items():
            if not config.preferred_providers:
                issues["content_types"].append(f"{content_type}: No preferred providers")
            
            if config.quality_threshold < 0 or config.quality_threshold > 1:
                issues["content_types"].append(f"{content_type}: Invalid quality_threshold")
            
            if config.max_tokens <= 0:
                issues["content_types"].append(f"{content_type}: Invalid max_tokens")
        
        # Validate generators
        for generator_name, config in self.generators.items():
            if not config.module_path or not config.class_name:
                issues["generators"].append(f"{generator_name}: Missing module_path or class_name")
            
            if not config.supported_content_types:
                issues["generators"].append(f"{generator_name}: No supported content types")
        
        # Validate factory config
        if self.factory_config.max_generation_time <= 0:
            issues["factory"].append("Invalid max_generation_time")
        
        return issues
    
    def reload_configuration(self):
        """Reload all configurations from files"""
        
        logger.info("🔄 Reloading configurations...")
        
        try:
            self._load_configurations()
            self._last_reload = datetime.now(timezone.utc)
            
            # Notify callbacks
            for callback in self._reload_callbacks:
                try:
                    callback()
                except Exception as e:
                    logger.warning(f"⚠️ Reload callback failed: {e}")
            
            logger.info("✅ Configuration reload completed")
            
        except Exception as e:
            logger.error(f"❌ Configuration reload failed: {e}")
    
    def add_reload_callback(self, callback: callable):
        """Add callback to be called on configuration reload"""
        self._reload_callbacks.append(callback)
    
    def export_configuration(self, export_dir: str):
        """Export all configurations to specified directory"""
        
        export_path = Path(export_dir)
        export_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Export providers
            providers_data = {"providers": {name: asdict(config) for name, config in self.providers.items()}}
            with open(export_path / "providers.yaml", 'w') as f:
                yaml.dump(providers_data, f, default_flow_style=False, indent=2)
            
            # Export content types
            content_types_data = {"content_types": {name: asdict(config) for name, config in self.content_types.items()}}
            with open(export_path / "content_types.yaml", 'w') as f:
                yaml.dump(content_types_data, f, default_flow_style=False, indent=2)
            
            # Export generators
            generators_data = {"generators": {name: asdict(config) for name, config in self.generators.items()}}
            with open(export_path / "generators.yaml", 'w') as f:
                yaml.dump(generators_data, f, default_flow_style=False, indent=2)
            
            # Export factory config
            factory_data = {"factory": asdict(self.factory_config)}
            with open(export_path / "factory.yaml", 'w') as f:
                yaml.dump(factory_data, f, default_flow_style=False, indent=2)
            
            logger.info(f"📤 Configuration exported to {export_dir}")
            
        except Exception as e:
            logger.error(f"❌ Configuration export failed: {e}")
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration"""
        
        available_providers = [name for name in self.providers.keys() if self._is_provider_available(name)]
        enabled_generators = [name for name, config in self.generators.items() if config.enabled]
        
        return {
            "providers": {
                "total": len(self.providers),
                "available": len(available_providers),
                "enabled": len([c for c in self.providers.values() if c.enabled]),
                "available_list": available_providers
            },
            "content_types": {
                "total": len(self.content_types),
                "configured": list(self.content_types.keys())
            },
            "generators": {
                "total": len(self.generators),
                "enabled": len(enabled_generators),
                "enabled_list": enabled_generators
            },
            "factory": {
                "lazy_loading": self.factory_config.lazy_loading,
                "health_monitoring": self.factory_config.health_monitoring,
                "cost_optimization": self.factory_config.cost_optimization,
                "auto_fallback": self.factory_config.auto_fallback
            },
            "last_reload": self._last_reload.isoformat(),
            "validation_issues": self.validate_configuration()
        }


# Global configuration manager instance
_global_config_manager = None

def get_configuration_manager(config_dir: str = None) -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _global_config_manager
    
    if _global_config_manager is None:
        config_dir = config_dir or os.getenv("GENERATOR_CONFIG_DIR", "config/generators")
        _global_config_manager = ConfigurationManager(config_dir)
    
    return _global_config_manager

def reload_global_configuration():
    """Reload global configuration"""
    global _global_config_manager
    if _global_config_manager:
        _global_config_manager.reload_configuration()

# Convenience functions
def get_provider_config(provider_name: str) -> Optional[ProviderConfig]:
    """Get provider configuration"""
    manager = get_configuration_manager()
    return manager.get_provider_config(provider_name)

def get_content_type_config(content_type: str) -> Optional[ContentTypeConfig]:
    """Get content type configuration"""
    manager = get_configuration_manager()
    return manager.get_content_type_config(content_type)

def get_generator_config(generator_name: str) -> Optional[GeneratorConfig]:
    """Get generator configuration"""
    manager = get_configuration_manager()
    return manager.get_generator_config(generator_name)

def get_optimal_providers(content_type: str) -> List[str]:
    """Get optimal providers for content type"""
    manager = get_configuration_manager()
    return manager.get_optimal_providers_for_content_type(content_type)

# CLI interface for configuration management
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generator Configuration Manager")
    parser.add_argument("--summary", action="store_true", help="Show configuration summary")
    parser.add_argument("--validate", action="store_true", help="Validate configurations")
    parser.add_argument("--export", help="Export configurations to directory")
    parser.add_argument("--reload", action="store_true", help="Reload configurations")
    parser.add_argument("--config-dir", help="Configuration directory", default="config/generators")
    args = parser.parse_args()
    
    manager = ConfigurationManager(args.config_dir)
    
    if args.summary:
        summary = manager.get_configuration_summary()
        print(json.dumps(summary, indent=2, default=str))
    
    elif args.validate:
        issues = manager.validate_configuration()
        if any(issues.values()):
            print("❌ Configuration issues found:")
            for category, issue_list in issues.items():
                if issue_list:
                    print(f"\n{category.upper()}:")
                    for issue in issue_list:
                        print(f"  - {issue}")
        else:
            print("✅ All configurations are valid")
    
    elif args.export:
        manager.export_configuration(args.export)
        print(f"📤 Configurations exported to {args.export}")
    
    elif args.reload:
        manager.reload_configuration()
        print("🔄 Configurations reloaded")
    
    else:
        parser.print_help()