"""Interactive Questionnaire Framework - Reusable step-by-step input collection.

This module provides a flexible question    def __init__(  # pylint: disable=too-many-arguments,too-many-positiona    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        key: str,
        text: str,
        placeholder: str = "",
        max_chars: Optional[int] = None,
        help_text: Optional[str] = None
    ):nts
        self,
        key: str,
        text: str,
        min_value: Union[int, float] = 0,
        max_value: Optional[Union[int, float]] = None,
        step: Union[int, float] = 1,
        format_str: str = "%.2f",
        help_text: Optional[str] = None
    ):ework for collecting user input
in a step-by-step manner using Streamlit session state management.

Features
--------
- Step-by-step question navigation with previous/next buttons
- Session state management for persistent data
- Type-safe question definitions with validation
- Customizable question types (number input, text input, etc.)
- Progress tracking and display
- Automatic data collection and aggregation

Dependencies
------------
- streamlit: >=1.0.0 - Web UI framework for interactive applications
- dataclasses: Built-in - For structured data containers
- typing: Built-in - For type hints and annotations
- abc: Built-in - For abstract base classes

Example
-------
>>> from src.utils.questionnaire import Questionnaire, NumberQuestion
>>> questions = [
...     NumberQuestion("income", "What is your monthly income?", min_value=0.0),
...     NumberQuestion("expenses", "What are your monthly expenses?", min_value=0.0)
... ]
>>> questionnaire = Questionnaire("financial", questions)
>>> # In Streamlit context:
>>> data = questionnaire.run()
>>> if data:
...     print(f"Income: {data['income']}, Expenses: {data['expenses']}")

Note
----
This module requires Streamlit context to run. All data is stored in
session state and persists across Streamlit reruns.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence, Union

import streamlit as st


@dataclass
class QuestionnaireConfig:
    """Configuration for questionnaire behavior and appearance.

    Attributes
    ----------
    session_prefix : str
        Prefix for session state keys to avoid conflicts
    show_progress : bool
        Whether to show progress indicators
    show_previous_answers : bool
        Whether to display previously entered answers
    navigation_style : str
        Button layout style ('columns' or 'inline')
    """

    session_prefix: str = "questionnaire"
    show_progress: bool = True
    show_previous_answers: bool = True
    navigation_style: str = "columns"


class Question(ABC):
    """Abstract base class for questionnaire questions.

    Defines the interface that all question types must implement.
    """

    def __init__(self, key: str, text: str, help_text: Optional[str] = None):
        """Initialize a question.

        Parameters
        ----------
        key : str
            Unique identifier for this question's data
        text : str
            The question text to display to the user
        help_text : Optional[str]
            Optional help text or explanation
        """
        self.key = key
        self.text = text
        self.help_text = help_text

    @abstractmethod
    def render(self, current_value: Any = None) -> Any:
        """Render the question UI and return the current value.

        Parameters
        ----------
        current_value : Any
            Previously entered value for this question

        Returns
        -------
        Any
            Current input value from the user
        """
        ...  # pragma: no cover

    @abstractmethod
    def get_default_value(self) -> Any:
        """Get the default value for this question.

        Returns
        -------
        Any
            Default value to use when no previous value exists
        """
        ...  # pragma: no cover


class NumberQuestion(Question):
    """Number input question with validation and formatting.

    Supports integer and float inputs with min/max validation,
    step size control, and currency formatting.
    """

    def __init__(
        self,
        key: str,
        text: str,
        min_value: Union[int, float] = 0,
        max_value: Optional[Union[int, float]] = None,
        step: Union[int, float] = 1,
        format_str: str = "%.2f",
        help_text: Optional[str] = None,
    ):
        """Initialize a number question.

        Parameters
        ----------
        key : str
            Unique identifier for this question
        text : str
            Question text to display
        min_value : Union[int, float]
            Minimum allowed value
        max_value : Optional[Union[int, float]]
            Maximum allowed value (None for no limit)
        step : Union[int, float]
            Step size for increment/decrement
        format_str : str
            Format string for display
        help_text : Optional[str]
            Optional help text
        """
        super().__init__(key, text, help_text)
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.format_str = format_str

    def render(self, current_value: Any = None) -> Union[int, float]:
        """Render number input widget."""
        value: Union[int, float] = (
            current_value if current_value is not None else self.get_default_value()
        )

        result = st.number_input(
            self.text,
            min_value=self.min_value,
            max_value=self.max_value,
            value=value,
            step=self.step,
            format=self.format_str,
            help=self.help_text,
            key=f"input_{self.key}",
        )
        return float(result)  # Ensure we return a proper numeric type

    def get_default_value(self) -> Union[int, float]:
        """Get default value (minimum value or 0)."""
        return self.min_value


class TextQuestion(Question):
    """Text input question with optional placeholder and validation.

    Supports single-line text input with placeholder text
    and basic validation.
    """

    def __init__(
        self,
        key: str,
        text: str,
        placeholder: str = "",
        max_chars: Optional[int] = None,
        help_text: Optional[str] = None,
    ):
        """Initialize a text question.

        Parameters
        ----------
        key : str
            Unique identifier for this question
        text : str
            Question text to display
        placeholder : str
            Placeholder text for empty input
        max_chars : Optional[int]
            Maximum character limit
        help_text : Optional[str]
            Optional help text
        """
        super().__init__(key, text, help_text)
        self.placeholder = placeholder
        self.max_chars = max_chars

    def render(self, current_value: Any = None) -> str:
        """Render text input widget."""
        value: str = (
            current_value if current_value is not None else self.get_default_value()
        )

        result = st.text_input(
            self.text,
            value=value,
            placeholder=self.placeholder,
            max_chars=self.max_chars,
            help=self.help_text,
            key=f"input_{self.key}",
        )
        return str(result)  # Ensure we return a proper string type

    def get_default_value(self) -> str:
        """Get default value (empty string)."""
        return ""


class Questionnaire:
    """Interactive step-by-step questionnaire with navigation and state management.

    Manages a sequence of questions with automatic navigation, progress tracking,
    and data collection using Streamlit session state.
    """

    def __init__(
        self,
        name: str,
        questions: Sequence[Question],
        config: Optional[QuestionnaireConfig] = None,
    ):
        """Initialize questionnaire.

        Parameters
        ----------
        name : str
            Unique name for this questionnaire (used in session state)
        questions : Sequence[Question]
            Sequence of questions to ask in order
        config : Optional[QuestionnaireConfig]
            Configuration options for behavior and appearance
        """
        self.name = name
        self.questions = questions
        self.config = config or QuestionnaireConfig()

        # Session state keys
        self.step_key = f"{self.config.session_prefix}_{name}_step"
        self.data_key = f"{self.config.session_prefix}_{name}_data"

    def _initialize_session_state(self) -> None:
        """Initialize session state variables if they don't exist."""
        if self.step_key not in st.session_state:
            st.session_state[self.step_key] = 0

        if self.data_key not in st.session_state:
            st.session_state[self.data_key] = {}

    def _get_current_step(self) -> int:
        """Get current step number."""
        return int(st.session_state.get(self.step_key, 0))

    def _set_current_step(self, step: int) -> None:
        """Set current step number."""
        st.session_state[self.step_key] = step

    def _get_stored_data(self) -> Dict[str, Any]:
        """Get stored questionnaire data."""
        return dict(st.session_state.get(self.data_key, {}))

    def _store_answer(self, question_key: str, value: Any) -> None:
        """Store answer for a question."""
        data = self._get_stored_data()
        data[question_key] = value
        st.session_state[self.data_key] = data

    def _show_progress(self, current_step: int) -> None:
        """Display progress indicator."""
        if not self.config.show_progress:
            return

        total_steps = len(self.questions)
        progress = (current_step + 1) / total_steps

        st.write(f"### Vraag {current_step + 1} van {total_steps}")
        st.progress(progress)

    def _show_previous_answers(self, current_step: int) -> None:
        """Display previously entered answers."""
        if not self.config.show_previous_answers or current_step == 0:
            return

        data = self._get_stored_data()

        for i in range(current_step):
            question = self.questions[i]
            if question.key in data:
                value = data[question.key]
                if isinstance(question, NumberQuestion):
                    formatted_value = (
                        f"€{value:,.2f}" if "€" in question.text else f"{value:,.2f}"
                    )
                else:
                    formatted_value = str(value)

                st.write(f"**{question.text}:** {formatted_value}")

    def _render_navigation(self, current_step: int, current_value: Any) -> bool:
        """Render navigation buttons and handle navigation logic.

        Returns
        -------
        bool
            True if questionnaire should continue, False if completed
        """
        total_steps = len(self.questions)
        question = self.questions[current_step]

        if self.config.navigation_style == "columns":
            col1, col2 = st.columns(2)
        else:
            col1 = col2 = st

        # Previous button (except for first question)
        if current_step > 0:
            with col1:
                if st.button("Vorige", key=f"prev_{current_step}"):
                    self._store_answer(question.key, current_value)
                    self._set_current_step(current_step - 1)
                    st.rerun()

        # Next/Complete button
        with col2:
            if current_step < total_steps - 1:
                button_text = "Volgende"
                button_key = f"next_{current_step}"
            else:
                button_text = "Voltooi"
                button_key = f"complete_{current_step}"

            if st.button(button_text, key=button_key):
                self._store_answer(question.key, current_value)

                if current_step < total_steps - 1:
                    self._set_current_step(current_step + 1)
                    st.rerun()
                else:
                    # Questionnaire completed
                    self._set_current_step(total_steps)
                    st.rerun()

        return True

    def reset(self) -> None:
        """Reset questionnaire to initial state."""
        if self.step_key in st.session_state:
            del st.session_state[self.step_key]
        if self.data_key in st.session_state:
            del st.session_state[self.data_key]

    def is_complete(self) -> bool:
        """Check if questionnaire is completed."""
        return self._get_current_step() >= len(self.questions)

    def get_data(self) -> Optional[Dict[str, Any]]:
        """Get collected data if questionnaire is complete.

        Returns
        -------
        Optional[Dict[str, Any]]
            Collected data if complete, None otherwise
        """
        if self.is_complete():
            return self._get_stored_data()
        return None

    def run(self) -> Optional[Dict[str, Any]]:
        """Run the questionnaire and return data when complete.

        Returns
        -------
        Optional[Dict[str, Any]]
            Collected data if questionnaire is complete, None if still in progress
        """
        self._initialize_session_state()

        current_step = self._get_current_step()

        # Check if questionnaire is complete
        if current_step >= len(self.questions):
            return self.get_data()

        # Show current question
        question = self.questions[current_step]
        stored_data = self._get_stored_data()

        # Display progress and previous answers
        self._show_progress(current_step)
        self._show_previous_answers(current_step)

        # Render current question
        st.write(f"**{question.text}**")
        current_value = question.render(stored_data.get(question.key))

        # Handle navigation
        self._render_navigation(current_step, current_value)

        return None
