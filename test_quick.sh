#!/bin/bash
# Quick test to verify Python 3.12 migration works

echo "========================================"
echo "  Quick Python 3.12 Migration Test"
echo "========================================"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Quick import test
python3 -c "
import sys
print(f'Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')

# Test imports
print('Testing imports...')
import fairseq_signals
print(f'✅ fairseq_signals v{fairseq_signals.__version__}')

from fairseq_signals.dataclass.configs import Config
cfg = Config()
print(f'✅ Config with default_factory works')

from fairseq_signals.models.m3ae.bert_model import apply_chunking_to_forward
print(f'✅ Transformers compatibility fixed')

import fairseq_signals.models
print(f'✅ Models import successfully')

print('')
print('🎉 All quick tests passed!')
" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS: Python 3.12 migration working correctly"
    echo ""
    echo "To run comprehensive tests:"
    echo "  python3 test_python312_migration.py"
    exit 0
else
    echo ""
    echo "❌ FAILED: Please check error messages above"
    exit 1
fi
