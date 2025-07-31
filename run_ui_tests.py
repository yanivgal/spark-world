#!/usr/bin/env python3
"""
UI Test Runner

A simple script to run UI component tests from the project root.
This follows clean code principles by keeping tests co-located but providing easy access.
"""

import sys
import os
import subprocess

def run_agents_test():
    """Run the agents UI test."""
    print("🤖 Running Agents UI Test...")
    test_path = "ui/components/tests/test_agents_ui.py"
    
    if not os.path.exists(test_path):
        print(f"❌ Test file not found: {test_path}")
        return False
    
    try:
        # Run the test using streamlit
        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run", test_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Agents UI test started successfully!")
            print("🌐 Open your browser to see the test results")
            return True
        else:
            print(f"❌ Test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def main():
    """Main test runner."""
    print("🧪 Spark-World UI Test Runner")
    print("=" * 40)
    
    # For now, just run the agents test
    # In the future, this could run multiple tests
    success = run_agents_test()
    
    if success:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 