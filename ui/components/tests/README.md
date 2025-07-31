# UI Component Tests

This directory contains tests for UI components, following clean code and domain-driven design principles.

## 🏗️ Structure

```
ui/components/
├── agents.py                    # Component code
├── tests/                       # Tests co-located with component
│   ├── __init__.py
│   ├── README.md               # This file
│   └── test_agents_ui.py       # Test for agents component
└── ... (other components)

run_ui_tests.py                  # Test runner (project root)
```

## 🧪 Running Tests

### Option 1: Direct Test (Recommended)
```bash
# From project root
streamlit run ui/components/tests/test_agents_ui.py
```

### Option 2: Using Test Runner
```bash
# From project root
python run_ui_tests.py
```

## 🎯 Test Philosophy

### **Co-location Principle**
- Tests are placed next to the code they test
- Makes it easy to find and maintain tests
- Follows domain-driven design principles

### **Clean Code Approach**
- Each test file focuses on one component
- Mock data is realistic and comprehensive
- Tests are fast and don't require external dependencies

### **Fast Feedback**
- No LLM calls or simulation setup
- Instant startup for UI testing
- Visual feedback for layout changes

## 📝 Adding New Tests

1. **Create test file** in `ui/components/tests/`
2. **Follow naming convention**: `test_<component_name>_ui.py`
3. **Use mock data** to avoid external dependencies
4. **Update test runner** if needed

## 🔧 Example Test Structure

```python
#!/usr/bin/env python3
"""
Test for <Component Name> UI
"""

import streamlit as st
import sys
import os

# Add project root to path (go up 4 levels: tests -> components -> ui -> project_root)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

# Import component
from ui.components.<component_name> import <component_function>

# Mock data classes
class MockData:
    # ... mock data setup

def main():
    """Test the component with mock data."""
    st.set_page_config(page_title="<Component> Test", layout="wide")
    
    # Setup mock session state
    if 'engine' not in st.session_state:
        st.session_state.engine = MockEngine()
    
    # Display component
    <component_function>()

if __name__ == "__main__":
    main()
```

## 🚀 Benefits

- **Fast Development**: Test UI changes instantly
- **Clean Architecture**: Tests co-located with code
- **Maintainable**: Easy to find and update tests
- **Realistic**: Uses actual component code with mock data

## 🔧 Path Resolution

The test files use a relative path to reach the project root:
- **Current location**: `ui/components/tests/test_agents_ui.py`
- **Project root**: `spark-world/` (4 levels up)
- **Import path**: `from ui.components.agents import display_agents_page`

This ensures tests work regardless of where they're run from, as long as the project structure is maintained. 