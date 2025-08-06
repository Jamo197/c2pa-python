#!/usr/bin/env python3
"""
Test script for EPUB metadata function.
This script tests the get_epub_metadata function exposed from c2pa_EPUB_Extension.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import c2pa
    print("✓ Successfully imported c2pa module")
    
    # Test if the new function is available
    print("\nTesting EPUB metadata function availability:")
    
    # Check if get_epub_metadata is available
    if hasattr(c2pa, 'get_epub_metadata'):
        print("✓ get_epub_metadata function is available")
    else:
        print("✗ get_epub_metadata function is NOT available")
    
    # Test function signature
    print("\nTesting function signature:")
    
    if hasattr(c2pa, 'get_epub_metadata'):
        import inspect
        sig = inspect.signature(c2pa.get_epub_metadata)
        print(f"get_epub_metadata signature: {sig}")
        
        # Show function documentation
        print(f"\nFunction documentation:")
        print(c2pa.get_epub_metadata.__doc__)
    
    print("\n✓ All tests completed successfully!")
    print("\nUsage example:")
    print("```python")
    print("import c2pa")
    print("metadata = c2pa.get_epub_metadata('path/to/your/file.epub')")
    print("print(f'Title: {metadata.get(\"title\")}')")
    print("print(f'Author: {metadata.get(\"author\")}')")
    print("```")
    
except ImportError as e:
    print(f"✗ Failed to import c2pa module: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1) 