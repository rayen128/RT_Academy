"""RT Academy UI Components Package.

This package provides modular, reusable UI components for financial calculators.
Components are organized by category for easy maintenance and selective imports.

Quick Import Examples
--------------------
# Import all components (convenience)
from src.code.UI_components import *

# Import specific categories
from src.code.UI_components.display import display_financial_metrics
from src.code.UI_components.input import display_currency_input
from src.code.UI_components.layout import display_two_column_layout
from src.code.UI_components.status import display_status_message
from src.code.UI_components.charts import display_chart_with_status

# Import multiple components from same category
from src.code.UI_components.input import (
    display_currency_input,
    display_percentage_input,
    display_calculation_button
)

Package Structure
----------------
- display: Visual presentation components (headers, metrics, cards)
- input: User input components (currency, percentage, buttons)
- layout: Structure and organization components (columns, sections)
- status: Status messages and validation display
- charts: Chart visualization with status integration
"""

# pylint: disable=invalid-name

# Expose main categories for explicit imports
from . import (  # pylint: disable=redefined-builtin,invalid-name
    charts,
    display,
    input,
    layout,
    status,
)
from .charts import *

# Import all components for convenience
from .display import *
from .input import *  # pylint: disable=redefined-builtin
from .layout import *
from .status import *

__all__ = [
    # Display components
    "display_section_header",
    "display_financial_metrics",
    "display_info_card",
    # Input components
    "display_currency_input",
    "display_percentage_input",
    "display_calculation_button",
    "display_reset_section",
    # Layout components
    "display_two_column_layout",
    "display_expandable_section",
    # Status components
    "get_financial_status_message",
    "display_status_message",
    "display_validation_results",
    # Chart components
    "display_chart_with_status",
    # Module references
    "display",
    "input",
    "layout",
    "status",
    "charts",
]
