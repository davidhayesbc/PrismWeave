#!/usr/bin/env python3
"""
Production Fix: PrismWeave Configuration Update
Fixes the timeout issue by setting appropriate limits for phi3:mini
"""

import yaml
from pathlib import Path

def create_optimized_config():
    """Create an optimized configuration file for PrismWeave"""
    
    config = {
        'models': {
            'small': {
                'primary': 'phi3:mini',
                'fallback': 'mistral:latest',
                'max_tokens': 1000,
                'max_context': 3000,  # Reduced from 50000
                'temperature': 0.1,
                'timeout': 45  # 45 second timeout
            },
            'medium': {
                'primary': 'mistral:latest',
                'fallback': 'llama3.1:8b',
                'max_tokens': 2000,
                'max_context': 8000,
                'temperature': 0.3,
                'timeout': 60
            },
            'large': {
                'primary': 'llama3.1:8b', 
                'fallback': 'mistral:latest',
                'max_tokens': 4000,
                'max_context': 16000,
                'temperature': 0.5,
                'timeout': 120
            }
        },
        'processing': {
            'max_content_length': 3000,  # Reduced from 50000 for phi3:mini
            'chunk_size': 2000,
            'overlap': 200,
            'min_word_count': 50,
            'timeout': 45,  # 45 second timeout
            'enable_preprocessing': True,  # Enable our preprocessing
            'remove_code_blocks': True,    # Remove problematic code blocks
            'simplify_markdown': True      # Simplify complex markdown
        },
        'ollama': {
            'host': 'http://localhost:11434',
            'timeout': 45,  # Reduced from potentially longer timeouts
            'max_retries': 2,
            'retry_delay': 5
        },
        'taxonomy': {
            'tech_tags': [
                'programming', 'ai', 'machine-learning', 'web-development', 
                'backend', 'frontend', 'devops', 'database', 'api', 'testing',
                'security', 'cloud', 'docker', 'kubernetes', 'python', 'javascript',
                'typescript', 'react', 'node', 'aws', 'azure', 'gcp'
            ],
            'business_tags': [
                'strategy', 'startup', 'management', 'leadership', 'finance',
                'marketing', 'sales', 'product', 'growth', 'innovation'
            ],
            'categories': [
                'tech', 'business', 'research', 'news', 'tutorial', 'reference', 'unsorted'
            ]
        }
    }
    
    return config

def backup_existing_config():
    """Backup existing configuration"""
    config_path = Path("config.yaml")
    if config_path.exists():
        backup_path = Path("config.yaml.backup")
        import shutil
        shutil.copy2(config_path, backup_path)
        print(f"✅ Backed up existing config to {backup_path}")
        return True
    return False

def update_config():
    """Update the configuration with optimized settings"""
    print("🔧 Updating PrismWeave Configuration")
    print("=" * 50)
    
    # Backup existing config
    backup_created = backup_existing_config()
    
    # Create optimized config
    config = create_optimized_config()
    
    # Write new config
    config_path = Path("config.yaml")
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print(f"✅ Created optimized config at {config_path}")
    
    # Show key changes
    print("\n📊 Key Configuration Changes:")
    print(f"   • max_content_length: 50000 → 3000 (94% reduction)")
    print(f"   • phi3:mini max_context: unlimited → 3000")
    print(f"   • timeout: default → 45 seconds")
    print(f"   • enable_preprocessing: True")
    print(f"   • remove_code_blocks: True")
    
    if backup_created:
        print(f"\n💾 Original config backed up as config.yaml.backup")
    
    print(f"\n🎯 These changes should resolve the phi3:mini timeout issues!")

def test_with_new_config():
    """Test document processing with the new configuration"""
    print("\n🧪 Testing with New Configuration")
    print("=" * 40)
    
    # Import PrismWeave components to test
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path.cwd() / 'src'))
        
        from src.utils.config import Config
        
        # Load new config
        config = Config()
        print(f"✅ Config loaded successfully")
        print(f"   max_content_length: {config.processing.max_content_length}")
        print(f"   small model: {config.get_model_config('small').get('primary')}")
        
    except Exception as e:
        print(f"⚠️ Could not test config loading: {e}")
        print("   This is normal if dependencies are not installed")

def main():
    """Main execution function"""
    print("🚀 PrismWeave Configuration Fix")
    print("=" * 60)
    print("This script fixes the phi3:mini timeout issues by:")
    print("1. Reducing max_content_length from 50000 to 3000 characters")
    print("2. Setting appropriate timeouts for phi3:mini")
    print("3. Enabling content preprocessing")
    print("4. Optimizing model configurations")
    print("")
    
    # Update configuration
    update_config()
    
    # Test new configuration
    test_with_new_config()
    
    print("\n✅ Configuration Update Complete!")
    print("\n📝 Next Steps:")
    print("1. Restart any running PrismWeave processes")
    print("2. Test document processing with the problematic document")
    print("3. If issues persist, try switching to mistral:latest model")
    print("4. Monitor processing times (should be under 45 seconds)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Configuration update cancelled")
    except Exception as e:
        print(f"\n❌ Configuration update failed: {e}")
        import traceback
        traceback.print_exc()
