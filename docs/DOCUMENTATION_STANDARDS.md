# RT Academy Documentation Standards

## Table of Contents
1. [Introduction](#introduction)
2. [File Structure](#file-structure)
3. [Documentation Formats](#documentation-formats)
4. [Type Hints](#type-hints)
5. [Examples and Tests](#examples-and-tests)
6. [AI/Agent Guidelines](#ai-agent-guidelines)
7. [Validation and Enforcement](#validation-and-enforcement)

## Introduction

This document outlines the documentation standards for the RT Academy project. These standards are designed to be:
- Clear and consistent
- Machine-readable
- AI/Agent-friendly
- Easy to validate
- Maintainable

## File Structure

### Module Header
Every Python file must start with:
```python
"""
[MODULE_NAME] - [BRIEF_DESCRIPTION]

This module [DOES_WHAT] by providing [WHAT_FUNCTIONALITY].

Features:
    - [FEATURE_1]: [BRIEF_DESCRIPTION]
    - [FEATURE_2]: [BRIEF_DESCRIPTION]

Dependencies:
    - [DEPENDENCY_1]: [VERSION] - [WHY_NEEDED]
    - [DEPENDENCY_2]: [VERSION] - [WHY_NEEDED]

Example:
    >>> from module_name import main_function
    >>> result = main_function(param1, param2)
    >>> print(result)
    Expected output

Note:
    [IMPORTANT_NOTES_ABOUT_USAGE]
"""

# Standard library imports
import os
from typing import List, Dict

# Third-party imports
import streamlit as st
import numpy as np

# Local imports
from .utils import helper_function
```

### Class Documentation
```python
@dataclass
class ExampleClass:
    """[CLASS_NAME] represents [WHAT_IT_REPRESENTS].
    
    Detailed description of the class's purpose and behavior.
    
    Attributes:
        attr1 (type): Description of attribute 1
        attr2 (type): Description of attribute 2
    
    Properties:
        prop1 (type): Description of property 1
        prop2 (type): Description of property 2
    
    Class Attributes:
        CLASS_ATTR (type): Description of class attribute
    
    Example:
        >>> obj = ExampleClass(attr1=value1, attr2=value2)
        >>> obj.method()
        Expected output
    
    Note:
        Important implementation details or usage warnings
    """
```

### Function Documentation
```python
def example_function(
    param1: type1,
    param2: type2,
    *args: Any,
    **kwargs: Any
) -> ReturnType:
    """[VERB] [WHAT_IT_DOES] with [THESE_INPUTS].
    
    Extended description of function behavior.
    
    Args:
        param1 (type1): Description of param1
            Indented additional details if needed
        param2 (type2): Description of param2
        *args: Description of variable args
        **kwargs: Description of keyword args
    
    Returns:
        ReturnType: Description of return value
            Multiple lines for complex returns
    
    Raises:
        ErrorType1: When and why this error occurs
        ErrorType2: When and why this error occurs
    
    Example:
        >>> result = example_function(1, "test")
        >>> print(result)
        Expected output
    
    Note:
        Important implementation notes
        Performance considerations
        Edge cases
    """
```

## Documentation Formats

### Variable and Constant Documentation
```python
# Constants should use UPPER_CASE and include units and valid ranges
MAX_INTEREST_RATE: float = 100.0  # Maximum interest rate (percentage, 0-100)
DEFAULT_YEARS: int = 30  # Default investment period (years, 1-50)

# Configuration dictionaries should be documented with types and valid values
FREQUENCY_MAP: Dict[str, int] = {
    'Yearly': 1,     # Annual compounding
    'Monthly': 12,   # Monthly compounding
    'Daily': 365,    # Daily compounding
}
```

### Error Messages
Error messages should follow this format:
```python
error_msg = (
    f"Invalid {param_name}: {value}. "
    f"Must be between {min_value} and {max_value}. "
    f"See documentation at {doc_url}"
)
```

## Type Hints

### Basic Types
```python
from typing import (
    List, Dict, Tuple, Set, Optional, Union, 
    Sequence, Mapping, Any, TypeVar, Generic
)

# Use descriptive type variables
T = TypeVar('T')
Number = Union[int, float]
OptionalStr = Optional[str]
```

### Custom Types
```python
from dataclasses import dataclass
from typing import NewType

# Use NewType for semantic types
EuroAmount = NewType('EuroAmount', float)
Percentage = NewType('Percentage', float)

# Use dataclasses for complex types
@dataclass
class MonetaryValue:
    amount: EuroAmount
    currency: str = "EUR"
```

## Examples and Tests

### Doctest Examples
Every public function should include doctests:
```python
def calculate_interest(
    principal: EuroAmount,
    rate: Percentage
) -> EuroAmount:
    """Calculate simple interest.
    
    Args:
        principal: Initial amount
        rate: Interest rate as percentage
    
    Returns:
        Interest earned
    
    Example:
        >>> calculate_interest(EuroAmount(100.0), Percentage(5.0))
        5.0
        >>> calculate_interest(EuroAmount(0.0), Percentage(5.0))
        0.0
        >>> calculate_interest(EuroAmount(100.0), Percentage(0.0))
        0.0
    """
```

## AI/Agent Guidelines

### Context Markers
Use special markers for AI/Agent parsing:
```python
# @AI_CONTEXT: This section handles financial calculations
# @REQUIRES_VALIDATION: Input values must be validated
# @EDGE_CASES: Handle negative numbers, zero, and very large values
# @DEPENDENCIES: numpy>=1.20.0, streamlit>=1.0.0
```

### Function Signatures
Include AI-friendly signatures:
```python
# @FUNCTION_SIGNATURE
# Input: (principal: float, rate: float, time: int)
# Output: float
# Constraints: principal >= 0, 0 <= rate <= 100, time > 0
# Example: calculate_compound_interest(1000, 5, 3) -> 1157.625
```

## Validation and Enforcement

### Pre-commit Hooks
Install pre-commit hooks to validate:
- Documentation presence
- Documentation format
- Type hints
- Examples

### Continuous Integration
Use GitHub Actions to:
- Run documentation tests
- Validate format
- Check coverage
- Generate documentation

### Tools
Recommended tools:
- pydocstyle: Documentation style checking
- mypy: Type checking
- sphinx: Documentation generation
- black: Code formatting
- pylint: Code quality
