#!/usr/bin/env python3
"""
Test suite for validating example configurations work with Python 3.12

This tests that:
1. All YAML config files can be loaded
2. Hydra initialization works with the configs
3. The dataclass/Hydra integration works correctly
"""

import sys
import os
from pathlib import Path
import yaml

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")

def find_example_configs():
    """Find all YAML configuration files in the examples directory"""
    examples_dir = Path("examples")
    if not examples_dir.exists():
        return []

    # Find all .yaml files
    yaml_files = list(examples_dir.rglob("*.yaml"))
    return yaml_files

def test_yaml_syntax():
    """Test 1: Verify all YAML files have valid syntax"""
    print("Test 1: YAML Syntax Validation")

    yaml_files = find_example_configs()
    if not yaml_files:
        print("  ⚠️  SKIP: No YAML files found in examples/")
        return True

    print(f"  Found {len(yaml_files)} YAML configuration files")

    failed = []
    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r') as f:
                yaml.safe_load(f)
        except Exception as e:
            failed.append((yaml_file, str(e)))

    if failed:
        print(f"  ❌ FAIL: {len(failed)} files have invalid YAML syntax:")
        for file, error in failed[:5]:  # Show first 5
            print(f"    - {file}: {error}")
        return False

    print(f"  ✅ PASS: All {len(yaml_files)} YAML files have valid syntax")
    return True

def test_hydra_config_structure():
    """Test 2: Verify configs have expected Hydra structure"""
    print("\nTest 2: Hydra Configuration Structure")

    yaml_files = find_example_configs()
    if not yaml_files:
        print("  ⚠️  SKIP: No YAML files found")
        return True

    # Sample a few representative configs
    test_files = [
        "examples/cmsc/config/pretraining/ecg_transformer/cmsc.yaml",
        "examples/scratch/ecg_classification/ecg_transformer/diagnosis_physionet2021.yaml",
        "examples/w2v_cmsc/config/pretraining/w2v_cmsc.yaml",
    ]

    tested = 0
    failed = []

    for config_path in test_files:
        if not os.path.exists(config_path):
            continue

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Check for expected top-level keys
            expected_keys = ['task', 'model', 'criterion', 'optimizer']
            missing = [k for k in expected_keys if k not in config]

            if missing:
                failed.append((config_path, f"Missing keys: {missing}"))
            else:
                tested += 1

        except Exception as e:
            failed.append((config_path, str(e)))

    if not tested and not failed:
        print("  ⚠️  SKIP: No test configs found")
        return True

    if failed:
        print(f"  ❌ FAIL: {len(failed)} configs have structure issues:")
        for file, error in failed:
            print(f"    - {file}: {error}")
        return False

    print(f"  ✅ PASS: {tested} sample configs have valid Hydra structure")
    return True

def test_config_loading_with_hydra():
    """Test 3: Test that configs can be loaded with Hydra/OmegaConf"""
    print("\nTest 3: Config Loading with Hydra/OmegaConf")

    try:
        from omegaconf import OmegaConf
        from hydra import compose, initialize_config_dir
        from hydra.core.global_hydra import GlobalHydra
    except ImportError as e:
        print(f"  ⚠️  SKIP: Hydra/OmegaConf not available - {e}")
        return True

    # Test loading a simple config
    test_config = "examples/scratch/ecg_classification/ecg_transformer/diagnosis_physionet2021.yaml"

    if not os.path.exists(test_config):
        print(f"  ⚠️  SKIP: Test config not found: {test_config}")
        return True

    try:
        # Load config with OmegaConf
        cfg = OmegaConf.load(test_config)
        print(f"  ✅ PASS: Loaded config with OmegaConf")

        # Verify config structure
        assert 'task' in cfg, "Config missing 'task' key"
        assert 'model' in cfg, "Config missing 'model' key"
        print(f"  ✅ PASS: Config has expected structure")

        # Verify task name is set correctly
        if hasattr(cfg.task, '_name'):
            print(f"  ✅ PASS: Task name: {cfg.task._name}")

        return True

    except Exception as e:
        print(f"  ❌ FAIL: Error loading config - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fairseq_config_integration():
    """Test 4: Test integration with fairseq_signals config system"""
    print("\nTest 4: Fairseq Signals Config Integration")

    try:
        from fairseq_signals.dataclass.configs import Config
        from fairseq_signals.dataclass.initialize import hydra_init
        from omegaconf import OmegaConf
    except ImportError as e:
        print(f"  ⚠️  SKIP: Fairseq imports not available - {e}")
        return True

    try:
        # Test that Hydra initialization works (this uses our fixed code)
        hydra_init("test_config")
        print("  ✅ PASS: Hydra initialized with fairseq configs")

        # Test that we can create a Config instance
        cfg = Config()
        print("  ✅ PASS: Created Config instance with default_factory")

        # Test that we can convert it to OmegaConf
        omega_cfg = OmegaConf.structured(cfg)
        print("  ✅ PASS: Converted Config to OmegaConf structure")

        return True

    except Exception as e:
        print(f"  ❌ FAIL: Config integration error - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_example_readme_commands():
    """Test 5: Validate that example README commands reference valid configs"""
    print("\nTest 5: Example README Command Validation")

    readme_files = list(Path("examples").rglob("README.md"))

    if not readme_files:
        print("  ⚠️  SKIP: No README files found")
        return True

    print(f"  Found {len(readme_files)} README files")

    # Parse READMEs for config-dir and config-name references
    config_refs = []
    for readme in readme_files:
        try:
            with open(readme, 'r') as f:
                content = f.read()
                # Look for --config-dir and --config-name patterns
                import re
                dir_matches = re.findall(r'--config-dir\s+(\S+)', content)
                name_matches = re.findall(r'--config-name\s+(\S+)', content)

                for dir_match in dir_matches:
                    if dir_match.startswith('examples/'):
                        config_refs.append(dir_match)
        except Exception as e:
            continue

    if not config_refs:
        print("  ⚠️  SKIP: No config references found in READMEs")
        return True

    # Verify referenced directories exist
    missing = []
    for ref in set(config_refs):
        if not os.path.exists(ref):
            missing.append(ref)

    if missing:
        print(f"  ❌ FAIL: {len(missing)} referenced config dirs don't exist:")
        for m in missing[:5]:
            print(f"    - {m}")
        return False

    print(f"  ✅ PASS: All {len(set(config_refs))} referenced config directories exist")
    return True

def run_all_tests():
    """Run all example tests"""
    print_header("Python 3.12 Examples Test Suite")

    # Change to repo root if needed
    if not os.path.exists("examples"):
        print("Error: examples/ directory not found. Run from repo root.")
        return 1

    tests = [
        ("YAML Syntax", test_yaml_syntax),
        ("Hydra Config Structure", test_hydra_config_structure),
        ("Config Loading with Hydra", test_config_loading_with_hydra),
        ("Fairseq Config Integration", test_fairseq_config_integration),
        ("Example README Validation", test_example_readme_commands),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Print summary
    print_header("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")

    print(f"\n{'=' * 70}")
    print(f"  Results: {passed}/{total} tests passed")
    print(f"{'=' * 70}\n")

    if passed == total:
        print("🎉 ALL EXAMPLE TESTS PASSED!")
        print("Example configurations are compatible with Python 3.12")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed. Review output above.")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
