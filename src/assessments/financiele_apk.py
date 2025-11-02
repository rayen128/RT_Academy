"""Financiele APK Calculator - Comprehensive financial analysis tool.

This module provides Financiele APK calculations by offering both simple
and advanced modes for analyzing assets, liabilities, and cash flow.

Features
--------
- Simple Mode: 4 basic input fields with automatic monthly leftover calculation
- Advanced Mode: Detailed breakdown of multiple income sources, expenses,
  assets, and debts
- Real-time validation and calculation of net worth and monthly balance
- Streamlit-based interactive user interface

Dependencies
------------
- streamlit: >=1.0.0 - Web UI framework for interactive data applications
- dataclasses: Built-in - For structured data containers
- typing: Built-in - For type hints and annotations

Example
-------
>>> from src.assessments.financiele_apk import show_financiele_apk
>>> # In a Streamlit app:
>>> show_financiele_apk()
# Displays interactive Financiele APK calculator

Note
----
This module requires Streamlit context to run. All monetary values
are assumed to be in Euros (€). The simple mode includes validation
to ensure input consistency.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import plotly.graph_objects as go
import streamlit as st

from src.database.models import Asset, Liability, MonthlyFlow
from src.UI_components.Applied.questionnaire import (
    BooleanQuestion,
    MultiSelectQuestion,
    NumberQuestion,
    Question,
    Questionnaire,
    QuestionnaireConfig,
    SelectQuestion,
    TextQuestion,
)
from src.UI_components.Basic import (
    display_calculation_button,
    display_info_card,
    display_progress_indicator,
    display_section_header,
)


@dataclass
class QuestionCategory:
    """Represents a category of questions in the Financial APK.

    Attributes
    ----------
    name : str
        Display name of the category
    description : str
        Brief description of what this category covers
    icon : str
        Emoji icon for the category
    questions : List[Question]
        List of questions in this category
    """

    name: str
    description: str
    icon: str
    questions: List[Question]


@dataclass
class CategoryProgress:
    """Tracks progress for a single category.

    Attributes
    ----------
    category_name : str
        Name of the category
    current_question : int
        Current question index within the category
    completed : bool
        Whether the category is completed
    data : Dict[str, Any]
        Collected data for this category
    """

    category_name: str
    current_question: int = 0
    completed: bool = False
    data: Dict[str, Any] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


class CheckboxQuestion(Question):
    """Multiple checkbox selection question.

    Allows users to select multiple items from a list of options
    using individual checkboxes for each option.
    """

    def __init__(
        self,
        key: str,
        text: str,
        options: List[str],
        default_values: Optional[List[str]] = None,
        help_text: Optional[str] = None,
    ):
        """Initialize a checkbox question.

        Parameters
        ----------
        key : str
            Unique identifier for this question
        text : str
            Question text to display
        options : List[str]
            List of checkbox options
        default_values : Optional[List[str]]
            List of initially selected options
        help_text : Optional[str]
            Optional help text
        """
        super().__init__(key, text, help_text)
        self.options = options
        self.default_values = default_values or []

    def render(self, current_value: Any = None) -> List[str]:
        """Render checkbox widgets for each option."""
        if current_value is None:
            current_value = self.default_values

        st.write(self.text)
        if self.help_text:
            st.caption(self.help_text)

        selected = []
        for option in self.options:
            is_checked = option in current_value
            if st.checkbox(option, value=is_checked, key=f"{self.key}_{option}"):
                selected.append(option)

        return selected

    def get_default_value(self) -> List[str]:
        """Get default value."""
        return self.default_values


class ConditionalQuestion(Question):
    """A question that is only shown if a condition is met.

    This allows for dynamic questionnaires where certain questions
    only appear based on previous answers.
    """

    def __init__(
        self,
        key: str,
        text: str,
        base_question: Question,
        condition_key: str,
        condition_value: Any,
        help_text: Optional[str] = None,
    ):
        """Initialize a conditional question.

        Parameters
        ----------
        key : str
            Unique identifier for this question
        text : str
            Question text to display
        base_question : Question
            The underlying question to render if condition is met
        condition_key : str
            Key of the question/field to check
        condition_value : Any
            Value that must match for this question to be shown
        help_text : Optional[str]
            Optional help text
        """
        super().__init__(key, text, help_text)
        self.base_question = base_question
        self.condition_key = condition_key
        self.condition_value = condition_value

    def should_show(self, data: Dict[str, Any]) -> bool:
        """Check if this question should be shown based on current data."""
        current_value = data.get(self.condition_key)

        # Special case for text fields - show if field is not empty
        if isinstance(self.condition_value, str) and self.condition_value == "":
            return current_value is not None and str(current_value).strip() != ""

        # Handle different comparison types
        if isinstance(self.condition_value, list):
            return current_value in self.condition_value
        elif isinstance(self.condition_value, str) and isinstance(current_value, list):
            return self.condition_value in current_value
        else:
            return current_value == self.condition_value

    def render(self, current_value: Any = None) -> Any:
        """Render the base question."""
        return self.base_question.render(current_value)

    def get_default_value(self) -> Any:
        """Get default value from base question."""
        return self.base_question.get_default_value()


class CategoricalQuestionnaire:
    """Manages a multi-category questionnaire with individual progress tracking.

    This class handles multiple categories of questions, each with their own
    progress bar, while maintaining an overall progress indicator.
    """

    def __init__(
        self,
        name: str,
        categories: List[QuestionCategory],
        config: Optional[QuestionnaireConfig] = None,
    ):
        """Initialize the categorical questionnaire.

        Parameters
        ----------
        name : str
            Unique name for this questionnaire
        categories : List[QuestionCategory]
            List of question categories
        config : Optional[QuestionnaireConfig]
            Configuration options
        """
        self.name = name
        self.categories = categories
        self.config = config or QuestionnaireConfig()

        # Session state keys
        self.current_category_key = (
            f"{self.config.session_prefix}_{name}_current_category"
        )
        self.progress_key = f"{self.config.session_prefix}_{name}_progress"
        self.data_key = f"{self.config.session_prefix}_{name}_data"

    def _initialize_session_state(self) -> None:
        """Initialize session state for categorical questionnaire."""
        if self.current_category_key not in st.session_state:
            st.session_state[self.current_category_key] = 0

        if self.progress_key not in st.session_state:
            st.session_state[self.progress_key] = {
                cat.name: CategoryProgress(cat.name) for cat in self.categories
            }

        if self.data_key not in st.session_state:
            st.session_state[self.data_key] = {}

    def _get_current_category_index(self) -> int:
        """Get current category index."""
        return int(st.session_state.get(self.current_category_key, 0))

    def _set_current_category_index(self, index: int) -> None:
        """Set current category index."""
        st.session_state[self.current_category_key] = index

    def _get_progress(self) -> Dict[str, CategoryProgress]:
        """Get progress for all categories."""
        return dict(st.session_state.get(self.progress_key, {}))

    def _update_progress(self, category_name: str, progress: CategoryProgress) -> None:
        """Update progress for a specific category."""
        all_progress = self._get_progress()
        all_progress[category_name] = progress
        st.session_state[self.progress_key] = all_progress

    def _get_all_data(self) -> Dict[str, Any]:
        """Get all collected data."""
        return dict(st.session_state.get(self.data_key, {}))

    def _store_data(self, data: Dict[str, Any]) -> None:
        """Store collected data."""
        all_data = self._get_all_data()
        all_data.update(data)
        st.session_state[self.data_key] = all_data

    def _show_overall_progress(self) -> None:
        """Display overall progress across all categories."""
        progress_data = self._get_progress()
        completed_categories = sum(1 for p in progress_data.values() if p.completed)
        total_categories = len(self.categories)

        overall_progress = (
            completed_categories / total_categories if total_categories > 0 else 0
        )

        display_progress_indicator(
            progress_value=overall_progress,
            title="Financiële APK Voortgang",
            subtitle=f"{completed_categories} van {total_categories} categorieën voltooid",
            show_percentage=True,
        )

    def _show_category_progress(
        self, category: QuestionCategory, progress: CategoryProgress
    ) -> None:
        """Display progress for current category."""
        visible_questions = self._get_visible_questions(category, progress.data)
        total_questions = len(visible_questions)

        if total_questions > 0:
            category_progress = (progress.current_question + 1) / total_questions
            current_q = min(progress.current_question + 1, total_questions)

            display_progress_indicator(
                progress_value=category_progress,
                title=f"{category.icon} {category.name}",
                subtitle=f"Vraag {current_q} van {total_questions}",
                show_percentage=False,
            )

    def _get_visible_questions(
        self, category: QuestionCategory, data: Dict[str, Any]
    ) -> List[Question]:
        """Get list of questions that should be visible based on current data."""
        visible = []
        all_data = self._get_all_data()
        all_data.update(data)  # Include current category data

        for question in category.questions:
            if isinstance(question, ConditionalQuestion):
                if question.should_show(all_data):
                    visible.append(question)
            else:
                visible.append(question)

        return visible

    def _run_category(self, category: QuestionCategory) -> Optional[Dict[str, Any]]:
        """Run a single category questionnaire."""
        progress = self._get_progress()[category.name]
        visible_questions = self._get_visible_questions(category, progress.data)

        if not visible_questions:
            # No questions to show, mark as completed
            progress.completed = True
            self._update_progress(category.name, progress)
            return progress.data

        # Show category description
        st.write(f"### {category.icon} {category.name}")
        st.write(category.description)
        st.write("---")

        # Show category progress
        self._show_category_progress(category, progress)

        current_question_idx = progress.current_question

        # Check if we've completed all visible questions
        if current_question_idx >= len(visible_questions):
            progress.completed = True
            self._update_progress(category.name, progress)
            return progress.data

        # Render current question
        question = visible_questions[current_question_idx]
        current_value = question.render(progress.data.get(question.key))

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])

        # Previous button
        with col1:
            if current_question_idx > 0:
                if st.button(
                    "Vorige vraag", key=f"prev_q_{category.name}_{current_question_idx}"
                ):
                    progress.data[question.key] = current_value
                    progress.current_question = max(0, current_question_idx - 1)
                    self._update_progress(category.name, progress)
                    st.rerun()

        # Next/Complete button
        with col2:
            if current_question_idx < len(visible_questions) - 1:
                button_text = "Volgende vraag"
                key = f"next_q_{category.name}_{current_question_idx}"
            else:
                button_text = "Voltooien categorie"
                key = f"complete_cat_{category.name}"

            if st.button(button_text, key=key, type="primary"):
                progress.data[question.key] = current_value
                progress.current_question = current_question_idx + 1

                # Check if category is now complete
                if progress.current_question >= len(visible_questions):
                    progress.completed = True

                self._update_progress(category.name, progress)
                st.rerun()

        # Skip category button
        with col3:
            if st.button("Sla categorie over", key=f"skip_cat_{category.name}"):
                progress.completed = True
                self._update_progress(category.name, progress)
                st.rerun()

        return None

    def reset(self) -> None:
        """Reset the entire questionnaire."""
        keys_to_remove = [self.current_category_key, self.progress_key, self.data_key]
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]

    def is_complete(self) -> bool:
        """Check if all categories are completed."""
        progress_data = self._get_progress()
        return all(progress.completed for progress in progress_data.values())

    def get_data(self) -> Optional[Dict[str, Any]]:
        """Get all collected data if questionnaire is complete."""
        if self.is_complete():
            return self._get_all_data()
        return None

    def run(self) -> Optional[Dict[str, Any]]:
        """Run the categorical questionnaire."""
        self._initialize_session_state()

        # Show overall progress
        self._show_overall_progress()

        # Check if questionnaire is complete
        if self.is_complete():
            st.success("🎉 Alle categorieën voltooid!")
            return self.get_data()

        current_category_idx = self._get_current_category_index()

        # Find next incomplete category
        progress_data = self._get_progress()
        for i, category in enumerate(self.categories):
            if not progress_data[category.name].completed:
                current_category_idx = i
                break

        # Run current category
        category = self.categories[current_category_idx]
        category_data = self._run_category(category)

        if category_data is not None:
            # Category completed, store data and move to next
            self._store_data(category_data)

            # Find next incomplete category
            next_category_idx = None
            for i, cat in enumerate(self.categories):
                if not progress_data[cat.name].completed:
                    next_category_idx = i
                    break

            if next_category_idx is not None:
                self._set_current_category_index(next_category_idx)
                st.rerun()

        return None


def create_comprehensive_financiele_apk_questionnaire() -> CategoricalQuestionnaire:
    """Create the comprehensive categorical Financiele APK questionnaire.

    Creates 8 categories of questions covering all aspects of personal finance:
    - Persoonlijke situatie
    - Woonsituatie
    - Financiële producten
    - Geordende zaken
    - Bezittingen
    - Schulden
    - Inkomsten & uitgaven
    - Doelen

    Returns
    -------
    CategoricalQuestionnaire
        Complete multi-category questionnaire
    """
    categories = []

    # Category 1: Persoonlijke situatie
    persoonlijk_questions = [
        SelectQuestion(
            key="relatievorm",
            text="Wat is je relatievorm?",
            options=[
                "Alleenstaand",
                "Samenwonend",
                "Getrouwd",
                "Gescheiden",
                "Weduwe/weduwnaar",
            ],
            help_text="Selecteer je huidige relatiesituatie",
        ),
        NumberQuestion(
            key="leeftijd",
            text="Wat is je leeftijd?",
            min_value=16,
            max_value=100,
            step=1,
            format_str="%d",
            help_text="Voer je leeftijd in jaren in",
        ),
        ConditionalQuestion(
            key="partner_leeftijd",
            text="Wat is de leeftijd van je partner?",
            base_question=NumberQuestion(
                key="partner_leeftijd",
                text="Wat is de leeftijd van je partner?",
                min_value=16,
                max_value=100,
                step=1,
                format_str="%d",
                help_text="Voer de leeftijd van je partner in jaren in",
            ),
            condition_key="relatievorm",
            condition_value=["Samenwonend", "Getrouwd"],
        ),
        NumberQuestion(
            key="aantal_kinderen",
            text="Hoeveel kinderen heb je?",
            min_value=0,
            max_value=20,
            step=1,
            format_str="%d",
            help_text="Voer het aantal kinderen in (0 als je geen kinderen hebt)",
        ),
    ]

    categories.append(
        QuestionCategory(
            name="Persoonlijke situatie",
            description="Basis informatie over jezelf en je gezinssituatie",
            icon="👤",
            questions=persoonlijk_questions,
        )
    )

    # Category 2: Woonsituatie
    woning_questions = [
        SelectQuestion(
            key="woon_situatie",
            text="Wat is je woonsituatie?",
            options=["Huur", "Koop", "Bij ouders/familie", "Anders"],
            help_text="Selecteer hoe je woont",
        ),
        ConditionalQuestion(
            key="maandelijkse_huur",
            text="Wat betaal je maandelijks aan huur?",
            base_question=NumberQuestion(
                key="maandelijkse_huur",
                text="Wat betaal je maandelijks aan huur? (€)",
                min_value=0,
                step=50,
                help_text="Voer je maandelijkse huurkosten in euro's in",
            ),
            condition_key="woon_situatie",
            condition_value="Huur",
        ),
        ConditionalQuestion(
            key="woningwaarde",
            text="Wat is de huidige waarde van je woning?",
            base_question=NumberQuestion(
                key="woningwaarde",
                text="Wat is de huidige waarde van je woning? (€)",
                min_value=0,
                step=1000,
                help_text="Geschatte marktwaarde van je woning",
            ),
            condition_key="woon_situatie",
            condition_value="Koop",
        ),
        ConditionalQuestion(
            key="hypotheekbedrag",
            text="Wat is het resterende hypotheekbedrag?",
            base_question=NumberQuestion(
                key="hypotheekbedrag",
                text="Wat is het resterende hypotheekbedrag? (€)",
                min_value=0,
                step=1000,
                help_text="Het bedrag dat je nog moet afbetalen op je hypotheek",
            ),
            condition_key="woon_situatie",
            condition_value="Koop",
        ),
        ConditionalQuestion(
            key="hypotheek_maandlasten",
            text="Wat zijn je maandelijkse hypotheeklasten?",
            base_question=NumberQuestion(
                key="hypotheek_maandlasten",
                text="Wat zijn je maandelijkse hypotheeklasten? (€)",
                min_value=0,
                step=50,
                help_text="Totale maandelijkse kosten hypotheek inclusief rente en aflossing",
            ),
            condition_key="woon_situatie",
            condition_value="Koop",
        ),
        ConditionalQuestion(
            key="hypotheek_rente",
            text="Wat is het rentepercentage van je hypotheek?",
            base_question=NumberQuestion(
                key="hypotheek_rente",
                text="Wat is het rentepercentage van je hypotheek? (%)",
                min_value=0,
                max_value=20,
                step=0.1,
                help_text="Het huidige rentepercentage van je hypotheek",
            ),
            condition_key="woon_situatie",
            condition_value="Koop",
        ),
    ]

    categories.append(
        QuestionCategory(
            name="Woonsituatie",
            description="Informatie over je woning en woonkosten",
            icon="🏠",
            questions=woning_questions,
        )
    )

    # Category 3: Financiële producten
    financiele_producten_questions = [
        CheckboxQuestion(
            key="financiele_producten",
            text="Welke financiële producten heb je?",
            options=[
                "Hypotheek",
                "Aansprakelijkheidsverzekering",
                "Inboedelverzekering",
                "Levensverzekering",
                "Beleggingsrekening",
                "Pensioenregeling (werkgever)",
                "Pensioenbeleggingsrekening",
                "Zorgverzekering",
                "Autoverzekering",
                "Reisverzekering",
            ],
            help_text="Selecteer alle producten die je hebt",
        ),
        TextQuestion(
            key="overige_financiele_producten",
            text="Andere financiële producten die je hebt:",
            placeholder="Bijvoorbeeld: specifieke verzekeringen, andere beleggingen...",
            help_text="Vul eventuele andere financiële producten in die niet in de lijst stonden",
        ),
    ]

    categories.append(
        QuestionCategory(
            name="Financiële producten",
            description="Overzicht van je verzekeringen en financiële diensten",
            icon="📋",
            questions=financiele_producten_questions,
        )
    )

    # Category 4: Geordende zaken
    geordende_zaken_questions = [
        BooleanQuestion(
            key="heeft_testament",
            text="Heb je een testament?",
            help_text="Een testament regelt wat er met je bezittingen gebeurt na overlijden",
        ),
        BooleanQuestion(
            key="pensioenopbouw_actief",
            text="Bouw je actief pensioen op?",
            help_text="Dit kan via je werkgever of een eigen pensioenregeling zijn",
        ),
        BooleanQuestion(
            key="heeft_volmacht",
            text="Heb je volmachten of andere juridische documenten geregeld?",
            help_text="Bijvoorbeeld een levenstestament, volmacht voor financiële zaken, etc.",
        ),
    ]

    categories.append(
        QuestionCategory(
            name="Geordende zaken",
            description="Juridische en administratieve zaken",
            icon="📄",
            questions=geordende_zaken_questions,
        )
    )

    # Category 5: Bezittingen
    bezittingen_questions = [
        NumberQuestion(
            key="spaarsaldo",
            text="Wat is je totale spaarsaldo? (€)",
            min_value=0,
            step=500,
            help_text="Totaal spaargeld op alle spaarrekeningen",
        ),
        TextQuestion(
            key="auto_merk",
            text="Welk automerk/model heb je?",
            placeholder="Bijvoorbeeld: Toyota Yaris, BMW X3...",
            help_text="Laat leeg als je geen auto hebt",
        ),
        NumberQuestion(
            key="auto_waarde",
            text="Wat is de geschatte waarde van je auto? (€)",
            min_value=0,
            step=500,
            help_text="Huidige marktwaarde van je auto (0 als je geen auto hebt)",
        ),
        NumberQuestion(
            key="beleggingen_waarde",
            text="Wat is de totale waarde van je beleggingen? (€)",
            min_value=0,
            step=500,
            help_text="Aandelen, obligaties, ETFs, crypto, etc.",
        ),
        TextQuestion(
            key="overige_bezittingen",
            text="Andere waardevolle bezittingen:",
            placeholder="Bijvoorbeeld: sieraden, kunst, verzamelingen...",
            help_text="Bezittingen met aanzienlijke waarde die je wilt meenemen",
        ),
        NumberQuestion(
            key="overige_bezittingen_waarde",
            text="Geschatte waarde overige bezittingen (€)",
            min_value=0,
            step=500,
            help_text="Totale geschatte waarde van je overige bezittingen",
        ),
    ]

    categories.append(
        QuestionCategory(
            name="Bezittingen",
            description="Overzicht van je vermogen en waardevolle spullen",
            icon="💰",
            questions=bezittingen_questions,
        )
    )

    # Category 6: Schulden
    schulden_questions = [
        SelectQuestion(
            key="schuld_type_1",
            text="Welk type schuld heb je (eerste schuld)?",
            options=[
                "Geen schulden",
                "Studieschuld",
                "Persoonlijke lening",
                "Creditcard schuld",
                "Doorlopend krediet",
                "Auto financiering",
                "Overige lening",
            ],
            help_text="Selecteer je belangrijkste type schuld",
        ),
        ConditionalQuestion(
            key="schuld_bedrag_1",
            text="Wat is het totale bedrag van deze schuld?",
            base_question=NumberQuestion(
                key="schuld_bedrag_1",
                text="Wat is het totale bedrag van deze schuld? (€)",
                min_value=0,
                step=100,
                help_text="Het totale bedrag dat je nog moet afbetalen",
            ),
            condition_key="schuld_type_1",
            condition_value=[
                "Studieschuld",
                "Persoonlijke lening",
                "Creditcard schuld",
                "Doorlopend krediet",
                "Auto financiering",
                "Overige lening",
            ],
        ),
        ConditionalQuestion(
            key="schuld_maandlasten_1",
            text="Wat betaal je maandelijks af?",
            base_question=NumberQuestion(
                key="schuld_maandlasten_1",
                text="Wat betaal je maandelijks af? (€)",
                min_value=0,
                step=25,
                help_text="Maandelijkse aflossing van deze schuld",
            ),
            condition_key="schuld_type_1",
            condition_value=[
                "Studieschuld",
                "Persoonlijke lening",
                "Creditcard schuld",
                "Doorlopend krediet",
                "Auto financiering",
                "Overige lening",
            ],
        ),
        # Second debt (optional)
        SelectQuestion(
            key="schuld_type_2",
            text="Heb je nog een tweede type schuld?",
            options=[
                "Geen tweede schuld",
                "Studieschuld",
                "Persoonlijke lening",
                "Creditcard schuld",
                "Doorlopend krediet",
                "Auto financiering",
                "Overige lening",
            ],
            help_text="Optioneel: selecteer een tweede type schuld",
        ),
        ConditionalQuestion(
            key="schuld_bedrag_2",
            text="Wat is het totale bedrag van deze tweede schuld?",
            base_question=NumberQuestion(
                key="schuld_bedrag_2",
                text="Wat is het totale bedrag van deze tweede schuld? (€)",
                min_value=0,
                step=100,
                help_text="Het totale bedrag van je tweede schuld",
            ),
            condition_key="schuld_type_2",
            condition_value=[
                "Studieschuld",
                "Persoonlijke lening",
                "Creditcard schuld",
                "Doorlopend krediet",
                "Auto financiering",
                "Overige lening",
            ],
        ),
        ConditionalQuestion(
            key="schuld_maandlasten_2",
            text="Wat betaal je maandelijks af aan deze tweede schuld?",
            base_question=NumberQuestion(
                key="schuld_maandlasten_2",
                text="Wat betaal je maandelijks af aan deze tweede schuld? (€)",
                min_value=0,
                step=25,
                help_text="Maandelijkse aflossing van je tweede schuld",
            ),
            condition_key="schuld_type_2",
            condition_value=[
                "Studieschuld",
                "Persoonlijke lening",
                "Creditcard schuld",
                "Doorlopend krediet",
                "Auto financiering",
                "Overige lening",
            ],
        ),
    ]

    categories.append(
        QuestionCategory(
            name="Schulden",
            description="Overzicht van je leningen en verplichtingen",
            icon="📉",
            questions=schulden_questions,
        )
    )

    # Category 7: Inkomsten & uitgaven
    inkomsten_uitgaven_questions = [
        NumberQuestion(
            key="primair_inkomen",
            text="Wat is je primaire netto maandinkomen? (€)",
            min_value=0,
            step=100,
            help_text="Je belangrijkste bron van inkomen (salaris, uitkering, etc.)",
        ),
        NumberQuestion(
            key="bijinkomen",
            text="Heb je bijkomende inkomsten per maand? (€)",
            min_value=0,
            step=50,
            help_text="Freelance, huur, dividenden, etc. (0 als je geen bijinkomen hebt)",
        ),
        NumberQuestion(
            key="vaste_lasten",
            text="Wat zijn je totale vaste lasten per maand? (€)",
            min_value=0,
            step=50,
            help_text="Huur/hypotheek, verzekeringen, abonnementen, telefoon, etc.",
        ),
        NumberQuestion(
            key="energie_kosten",
            text="Wat betaal je maandelijks aan energie? (€)",
            min_value=0,
            step=25,
            help_text="Gas, water, licht",
        ),
        NumberQuestion(
            key="variabele_kosten",
            text="Wat geef je gemiddeld uit aan variabele kosten? (€)",
            min_value=0,
            step=50,
            help_text="Boodschappen, kleding, entertainment, hobby's, etc.",
        ),
        NumberQuestion(
            key="spaarritme",
            text="Hoeveel denk je realistisch per maand te kunnen sparen/beleggen? (€)",
            min_value=0,
            step=25,
            help_text="Het bedrag dat je maandelijks opzij kunt zetten",
        ),
    ]

    categories.append(
        QuestionCategory(
            name="Inkomsten & uitgaven",
            description="Je maandelijkse geldstromen",
            icon="💳",
            questions=inkomsten_uitgaven_questions,
        )
    )

    # Category 8: Doelen
    doelen_questions = [
        TextQuestion(
            key="doel_1_naam",
            text="Wat is je eerste financiële doel?",
            placeholder="Bijvoorbeeld: noodfonds, nieuwe auto, eigen huis...",
            help_text="Beschrijf je belangrijkste financiële doel",
        ),
        ConditionalQuestion(
            key="doel_1_bedrag",
            text="Hoeveel geld heb je hiervoor nodig?",
            base_question=NumberQuestion(
                key="doel_1_bedrag",
                text="Hoeveel geld heb je hiervoor nodig? (€)",
                min_value=0,
                step=500,
                help_text="Het totale bedrag dat je nodig hebt voor dit doel",
            ),
            condition_key="doel_1_naam",
            condition_value="",  # Show if name is not empty
        ),
        ConditionalQuestion(
            key="doel_1_huidig",
            text="Hoeveel heb je hier al voor gespaard?",
            base_question=NumberQuestion(
                key="doel_1_huidig",
                text="Hoeveel heb je hier al voor gespaard? (€)",
                min_value=0,
                step=100,
                help_text="Het bedrag dat je al hebt gespaard voor dit doel",
            ),
            condition_key="doel_1_naam",
            condition_value="",
        ),
        ConditionalQuestion(
            key="doel_1_datum",
            text="Wanneer wil je dit doel bereikt hebben?",
            base_question=TextQuestion(
                key="doel_1_datum",
                text="Wanneer wil je dit doel bereikt hebben?",
                placeholder="Bijvoorbeeld: over 2 jaar, in 2027...",
                help_text="Geef een indicatie van wanneer je dit doel wilt bereiken",
            ),
            condition_key="doel_1_naam",
            condition_value="",
        ),
        ConditionalQuestion(
            key="doel_1_prioriteit",
            text="Hoe belangrijk is dit doel voor je?",
            base_question=SelectQuestion(
                key="doel_1_prioriteit",
                text="Hoe belangrijk is dit doel voor je?",
                options=["Hoog", "Middel", "Laag"],
                help_text="Geef de prioriteit van dit doel aan",
            ),
            condition_key="doel_1_naam",
            condition_value="",
        ),
        # Second goal (optional)
        TextQuestion(
            key="doel_2_naam",
            text="Heb je nog een tweede financieel doel? (optioneel)",
            placeholder="Bijvoorbeeld: vakantie, studie, verbouwing...",
            help_text="Optioneel: beschrijf een tweede financieel doel",
        ),
        ConditionalQuestion(
            key="doel_2_bedrag",
            text="Hoeveel geld heb je hiervoor nodig?",
            base_question=NumberQuestion(
                key="doel_2_bedrag",
                text="Hoeveel geld heb je hiervoor nodig? (€)",
                min_value=0,
                step=500,
                help_text="Het totale bedrag voor je tweede doel",
            ),
            condition_key="doel_2_naam",
            condition_value="",
        ),
        ConditionalQuestion(
            key="doel_2_prioriteit",
            text="Hoe belangrijk is dit tweede doel?",
            base_question=SelectQuestion(
                key="doel_2_prioriteit",
                text="Hoe belangrijk is dit tweede doel?",
                options=["Hoog", "Middel", "Laag"],
                help_text="Geef de prioriteit van dit tweede doel aan",
            ),
            condition_key="doel_2_naam",
            condition_value="",
        ),
    ]

    categories.append(
        QuestionCategory(
            name="Doelen",
            description="Je financiële doelstellingen en plannen",
            icon="🎯",
            questions=doelen_questions,
        )
    )

    config = QuestionnaireConfig(
        session_prefix="comprehensive_financiele_apk",
        show_progress=True,
        show_previous_answers=False,  # Categories handle their own context
        navigation_style="columns",
    )

    return CategoricalQuestionnaire("comprehensive_apk", categories, config)


def validate_financial_consistency(
    monthly_income: float, monthly_expenses: float, monthly_leftover: float
) -> Tuple[bool, str]:
    """Validate consistency between income, expenses and leftover amount.

    Parameters
    ----------
    monthly_income : float
        Total monthly income in euros
    monthly_expenses : float
        Total monthly expenses in euros
    monthly_leftover : float
        User-reported monthly leftover amount in euros

    Returns
    -------
    Tuple[bool, str]
        Boolean indicating if values are consistent and warning message if not

    Example
    -------
    >>> is_valid, message = validate_financial_consistency(3000.0, 2500.0, 500.0)
    >>> is_valid
    True
    >>> is_valid, message = validate_financial_consistency(3000.0, 2500.0, 300.0)
    >>> is_valid
    False
    """
    calculated_leftover = monthly_income - monthly_expenses
    difference = abs(calculated_leftover - monthly_leftover)
    tolerance = 50.0  # €50 tolerance

    if difference <= tolerance:
        return True, ""

    if monthly_leftover > calculated_leftover:
        return (
            False,
            f"⚠️ Je zegt €{monthly_leftover:,.2f} over te houden, maar op basis "
            f"van je inkomen (€{monthly_income:,.2f}) en uitgaven "
            f"(€{monthly_expenses:,.2f}) zou je €{calculated_leftover:,.2f} "
            f"over moeten houden. Controleer je bedragen.",
        )
    return (
        False,
        f"⚠️ Op basis van je inkomen (€{monthly_income:,.2f}) en uitgaven "
        f"(€{monthly_expenses:,.2f}) zou je €{calculated_leftover:,.2f} over "
        f"moeten houden, maar je zegt slechts €{monthly_leftover:,.2f} over "
        f"te houden. Mogelijk heb je uitgaven vergeten?",
    )


@dataclass
class FinancieleAPKData:  # pylint: disable=too-many-instance-attributes
    """Data structure for comprehensive Financiele APK information.

    Represents all financial data collected from either simple or advanced
    input modes, providing a unified structure for Financiele APK calculations
    and display.

    Attributes
    ----------
    monthly_income : float
        Total monthly income in euros
    monthly_expenses : float
        Total monthly expenses in euros
    monthly_leftover : float
        Manually entered or calculated leftover amount
    total_assets : float
        Total value of all assets in euros
    total_debt : float
        Total amount of all debts in euros
    assets : List[Asset]
        Detailed list of individual assets
    liabilities : List[Liability]
        Detailed list of individual debts
    income_streams : List[MonthlyFlow]
        Detailed list of income sources
    expense_streams : List[MonthlyFlow]
        Detailed list of expense categories

    Example
    -------
    >>> data = FinancieleAPKData(
    ...     monthly_income=3000.0,
    ...     monthly_expenses=2500.0,
    ...     monthly_leftover=500.0,
    ...     total_assets=10000.0,
    ...     total_debt=5000.0,
    ...     assets=[Asset(name="Savings", value=10000.0)],
    ...     liabilities=[Liability(name="Loan", amount=5000.0)],
    ...     income_streams=[MonthlyFlow(name="Salary", amount=3000.0)],
    ...     expense_streams=[MonthlyFlow(name="Living", amount=2500.0)]
    ... )
    >>> data.monthly_income
    3000.0

    Note
    ----
    In simple mode, assets, liabilities, income_streams, and expense_streams
    will contain single items representing the totals.
    """

    monthly_income: float
    monthly_expenses: float
    monthly_leftover: float
    total_assets: float
    total_debt: float
    assets: List[Asset]
    liabilities: List[Liability]
    income_streams: List[MonthlyFlow]
    expense_streams: List[MonthlyFlow]


def show_onboarding() -> bool:
    """Show the onboarding screen for Financiele APK.

    Displays welcome message, explains what the tool does, and provides
    a start button to begin the assessment process.

    Returns
    -------
    bool
        True if user clicked "Start APK" button, False otherwise

    Example
    -------
    >>> # In Streamlit context:
    >>> if show_onboarding():
    ...     # User clicked start, proceed to questionnaire
    ...     pass
    """
    # Display title
    display_section_header("Welkom bij de Financiële APK", "🏦")

    # Progress indicator at 0%
    display_progress_indicator(
        progress_value=0.0, title="Voortgang Financiële APK", show_percentage=True
    )

    st.write("---")

    # Explanation section
    st.write("### Wat houdt de Financiële APK in?")

    # Bullet points explaining the tool
    st.markdown(
        """
    - 🔍 **De tool helpt je inzicht te krijgen in jouw financiële situatie**
      We analyseren je huidige inkomsten, uitgaven, bezittingen en schulden

    - ⚠️ **Je ontdekt aandachtspunten, valkuilen en kansen**
      Identificeer risico's en mogelijkheden voor verbetering

    - 📋 **Op basis hiervan worden actiepunten en een concreet plan gemaakt**
      Krijg praktische stappen om je financiële situatie te verbeteren

    - 🎯 **Je doelen worden doorgerekend (sparen of beleggen)**
      We berekenen realistische scenario's voor je financiële doelen

    - 🚀 **Tot slot ga je aan de slag met uitvoeren en monitoren**
      Implementeer het plan en houd je voortgang bij
    """
    )

    st.write("---")

    # Information card with additional context
    display_info_card(
        title="Waarom een Financiële APK?",
        content=(
            "Net zoals een auto een APK nodig heeft voor veiligheid, heeft je "
            "financiële situatie regelmatig een check-up nodig. Deze tool helpt "
            "je om grip te krijgen op je geld en slimme keuzes te maken voor je "
            "toekomst."
        ),
        icon="💡",
        card_type="info",
    )

    st.write("")

    # Center the start button
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        start_clicked = display_calculation_button(
            label="Start APK",
            key="start_financiele_apk",
            help_text="Begin met de financiële analyse",
            button_type="primary",
        )

    return start_clicked


def create_financiele_apk_questionnaire() -> Questionnaire:
    """Create a questionnaire for collecting Financiele APK data.

    Creates a step-by-step questionnaire to collect the user's financial
    information including income, expenses, leftover money, assets, and debts.

    Returns
    -------
    Questionnaire
        Configured questionnaire with financial questions

    Example
    -------
    >>> questionnaire = create_financiele_apk_questionnaire()
    >>> # In Streamlit context:
    >>> data = questionnaire.run()
    >>> if data:
    ...     print(f"Monthly income: €{data['monthly_income']:,.2f}")

    Note
    ----
    The questionnaire collects data for simple Financiele APK calculation.
    All monetary values are in Euros (€).
    """
    questions = [
        NumberQuestion(
            key="monthly_income",
            text="Wat is je maandelijks netto totaal inkomen gemiddeld genomen?",
            min_value=0.0,
            step=100.0,
            format_str="%.2f",
            help_text="Voer je totale maandelijkse netto inkomen in euro's in",
        ),
        NumberQuestion(
            key="monthly_expenses",
            text="Wat zijn je totale maandelijkse uitgaven?",
            min_value=0.0,
            step=100.0,
            format_str="%.2f",
            help_text=(
                "Voer je totale maandelijkse uitgaven in euro's in "
                "(huur, boodschappen, verzekeringen, etc.)"
            ),
        ),
        NumberQuestion(
            key="monthly_leftover",
            text=(
                "Hoeveel geld houd je gemiddeld maandelijks over "
                "om te kunnen sparen of beleggen?"
            ),
            min_value=0.0,
            step=50.0,
            format_str="%.2f",
            help_text=(
                "(Tip: je kunt dit nagaan door je bankafschriften te checken. "
                "Reken alleen echt het geld dat je overhoudt. Dus niet geld "
                "dat je apart zet voor een vakantie, een nieuwe auto of "
                "andere spaardoelen.)"
            ),
        ),
        NumberQuestion(
            key="total_assets",
            text="Hoeveel spaargeld, beleggingen of andere bezittingen bezit je nu?",
            min_value=0.0,
            step=1000.0,
            format_str="%.2f",
            help_text=(
                "Voer de totale waarde van je bezittingen in euro's in "
                "(spaargeld, investeringen, huis, auto, etc.)"
            ),
        ),
        NumberQuestion(
            key="total_debt",
            text="Wat is je totaal aantal schulden?",
            min_value=0.0,
            step=1000.0,
            format_str="%.2f",
            help_text='Als je geen schulden hebt, vul hier "0" in.',
        ),
    ]

    config = QuestionnaireConfig(
        session_prefix="financiele_apk",
        show_progress=True,
        show_previous_answers=True,
        navigation_style="columns",
    )

    return Questionnaire("financiele_apk_data", questions, config)


def _create_simple_financial_lists(
    monthly_income: float,
    monthly_expenses: float,
    total_assets: float,
    total_debt: float,
) -> Tuple[List[Asset], List[Liability], List[MonthlyFlow], List[MonthlyFlow]]:
    """Create simple financial data lists for consistency with advanced mode.

    Parameters
    ----------
    monthly_income : float
        Total monthly income in euros
    monthly_expenses : float
        Total monthly expenses in euros
    total_assets : float
        Total value of assets in euros
    total_debt : float
        Total amount of debt in euros

    Returns
    -------
    Tuple[List[Asset], List[Liability], List[MonthlyFlow], List[MonthlyFlow]]
        Tuple containing assets, liabilities, income_streams, expense_streams lists
    """
    assets = (
        [Asset(name="Totale bezittingen", value=total_assets)]
        if total_assets > 0
        else []
    )
    liabilities = (
        [Liability(name="Totale schulden", amount=total_debt)] if total_debt > 0 else []
    )
    income_streams = (
        [MonthlyFlow(name="Maandelijks inkomen", amount=monthly_income)]
        if monthly_income > 0
        else []
    )
    expense_streams = (
        [MonthlyFlow(name="Maandelijkse uitgaven", amount=monthly_expenses)]
        if monthly_expenses > 0
        else []
    )

    return assets, liabilities, income_streams, expense_streams


def questionnaire_data_to_financiele_apk(
    data: Dict[str, float],
) -> FinancieleAPKData:
    """Convert questionnaire data to FinancieleAPKData structure.

    Transforms the flat dictionary returned by the questionnaire into
    a structured FinancieleAPKData object with user-provided values.

    Parameters
    ----------
    data : Dict[str, float]
        Dictionary containing questionnaire responses with keys:
        'monthly_income', 'monthly_expenses', 'monthly_leftover',
        'total_assets', 'total_debt'

    Returns
    -------
    FinancieleAPKData
        Complete financial data structure with user-provided monthly leftover
        and single-item lists for consistency

    Example
    -------
    >>> data = {
    ...     'monthly_income': 3000.0,
    ...     'monthly_expenses': 2500.0,
    ...     'monthly_leftover': 400.0,
    ...     'total_assets': 10000.0,
    ...     'total_debt': 5000.0
    ... }
    >>> overview = questionnaire_data_to_financiele_apk(data)
    >>> overview.monthly_leftover
    400.0

    Note
    ----
    Creates single-item lists for assets, liabilities, income_streams,
    and expense_streams to maintain consistency with advanced mode structure.
    Uses user-provided monthly_leftover instead of calculating it.
    """
    monthly_income = data.get("monthly_income", 0.0)
    monthly_expenses = data.get("monthly_expenses", 0.0)
    monthly_leftover = data.get("monthly_leftover", 0.0)
    total_assets = data.get("total_assets", 0.0)
    total_debt = data.get("total_debt", 0.0)

    # Create simple data structures for consistency
    assets, liabilities, income_streams, expense_streams = (
        _create_simple_financial_lists(
            monthly_income, monthly_expenses, total_assets, total_debt
        )
    )

    return FinancieleAPKData(
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        monthly_leftover=monthly_leftover,
        total_assets=total_assets,
        total_debt=total_debt,
        assets=assets,
        liabilities=liabilities,
        income_streams=income_streams,
        expense_streams=expense_streams,
    )


def comprehensive_data_to_financiele_apk(data: Dict[str, Any]) -> FinancieleAPKData:
    """Convert comprehensive questionnaire data to FinancieleAPKData structure.

    Transforms the detailed categorical questionnaire data into a simplified
    FinancieleAPKData structure for display and analysis.

    Parameters
    ----------
    data : Dict[str, Any]
        Dictionary containing comprehensive questionnaire responses

    Returns
    -------
    FinancieleAPKData
        Complete financial data structure with calculated totals
    """
    # Calculate monthly income
    monthly_income = data.get("primair_inkomen", 0.0) + data.get("bijinkomen", 0.0)

    # Calculate monthly expenses
    monthly_expenses = (
        data.get("vaste_lasten", 0.0)
        + data.get("energie_kosten", 0.0)
        + data.get("variabele_kosten", 0.0)
        + data.get("hypotheek_maandlasten", 0.0)
        + data.get("maandelijkse_huur", 0.0)
        + data.get("schuld_maandlasten_1", 0.0)
        + data.get("schuld_maandlasten_2", 0.0)
    )

    # Calculate monthly leftover
    monthly_leftover = monthly_income - monthly_expenses

    # Calculate total assets
    total_assets = (
        data.get("spaarsaldo", 0.0)
        + data.get("auto_waarde", 0.0)
        + data.get("beleggingen_waarde", 0.0)
        + data.get("overige_bezittingen_waarde", 0.0)
        + data.get("woningwaarde", 0.0)
    )

    # Calculate total debt
    total_debt = (
        data.get("hypotheekbedrag", 0.0)
        + data.get("schuld_bedrag_1", 0.0)
        + data.get("schuld_bedrag_2", 0.0)
    )

    # Create detailed lists for assets
    assets = []
    if data.get("spaarsaldo", 0.0) > 0:
        assets.append(Asset(name="Spaarsaldo", value=data["spaarsaldo"]))
    if data.get("auto_waarde", 0.0) > 0:
        auto_name = data.get("auto_merk", "Auto")
        if not auto_name.strip():
            auto_name = "Auto"
        assets.append(Asset(name=auto_name, value=data["auto_waarde"]))
    if data.get("beleggingen_waarde", 0.0) > 0:
        assets.append(Asset(name="Beleggingen", value=data["beleggingen_waarde"]))
    if data.get("overige_bezittingen_waarde", 0.0) > 0:
        assets.append(
            Asset(name="Overige bezittingen", value=data["overige_bezittingen_waarde"])
        )
    if data.get("woningwaarde", 0.0) > 0:
        assets.append(Asset(name="Woning", value=data["woningwaarde"]))

    # Create detailed lists for liabilities
    liabilities = []
    if data.get("hypotheekbedrag", 0.0) > 0:
        liabilities.append(Liability(name="Hypotheek", amount=data["hypotheekbedrag"]))
    if data.get("schuld_bedrag_1", 0.0) > 0:
        debt_name = data.get("schuld_type_1", "Schuld")
        if debt_name == "Geen schulden":
            debt_name = "Schuld"
        liabilities.append(Liability(name=debt_name, amount=data["schuld_bedrag_1"]))
    if data.get("schuld_bedrag_2", 0.0) > 0:
        debt_name = data.get("schuld_type_2", "Tweede schuld")
        if debt_name == "Geen tweede schuld":
            debt_name = "Tweede schuld"
        liabilities.append(Liability(name=debt_name, amount=data["schuld_bedrag_2"]))

    # Create detailed lists for income streams
    income_streams = []
    if data.get("primair_inkomen", 0.0) > 0:
        income_streams.append(
            MonthlyFlow(name="Primair inkomen", amount=data["primair_inkomen"])
        )
    if data.get("bijinkomen", 0.0) > 0:
        income_streams.append(MonthlyFlow(name="Bijinkomen", amount=data["bijinkomen"]))

    # Create detailed lists for expense streams
    expense_streams = []
    if data.get("vaste_lasten", 0.0) > 0:
        expense_streams.append(
            MonthlyFlow(name="Vaste lasten", amount=data["vaste_lasten"])
        )
    if data.get("energie_kosten", 0.0) > 0:
        expense_streams.append(
            MonthlyFlow(name="Energie", amount=data["energie_kosten"])
        )
    if data.get("variabele_kosten", 0.0) > 0:
        expense_streams.append(
            MonthlyFlow(name="Variabele kosten", amount=data["variabele_kosten"])
        )
    if data.get("hypotheek_maandlasten", 0.0) > 0:
        expense_streams.append(
            MonthlyFlow(name="Hypotheek", amount=data["hypotheek_maandlasten"])
        )
    if data.get("maandelijkse_huur", 0.0) > 0:
        expense_streams.append(
            MonthlyFlow(name="Huur", amount=data["maandelijkse_huur"])
        )
    if data.get("schuld_maandlasten_1", 0.0) > 0:
        debt_name = data.get("schuld_type_1", "Schuld aflossing")
        expense_streams.append(
            MonthlyFlow(
                name=f"{debt_name} aflossing", amount=data["schuld_maandlasten_1"]
            )
        )
    if data.get("schuld_maandlasten_2", 0.0) > 0:
        debt_name = data.get("schuld_type_2", "Tweede schuld aflossing")
        expense_streams.append(
            MonthlyFlow(
                name=f"{debt_name} aflossing", amount=data["schuld_maandlasten_2"]
            )
        )

    return FinancieleAPKData(
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        monthly_leftover=monthly_leftover,
        total_assets=total_assets,
        total_debt=total_debt,
        assets=assets,
        liabilities=liabilities,
        income_streams=income_streams,
        expense_streams=expense_streams,
    )


def validate_comprehensive_data_completeness(data: Dict[str, Any]) -> List[str]:
    """Validate completeness of comprehensive questionnaire data.

    Checks for missing or incomplete data in the comprehensive questionnaire
    and returns warnings for areas that need attention.

    Parameters
    ----------
    data : Dict[str, Any]
        Complete questionnaire data

    Returns
    -------
    List[str]
        List of warning messages for missing data
    """
    warnings = []

    # Check personal information
    if not data.get("leeftijd"):
        warnings.append("Persoonlijke situatie: Leeftijd ontbreekt")
    if not data.get("relatievorm"):
        warnings.append("Persoonlijke situatie: Relatievorm ontbreekt")

    # Check housing situation
    if not data.get("woon_situatie"):
        warnings.append("Woonsituatie: Type woning (huur/koop) ontbreekt")
    elif data.get("woon_situatie") == "Huur" and not data.get("maandelijkse_huur"):
        warnings.append("Woonsituatie: Huurkosten ontbreken")
    elif data.get("woon_situatie") == "Koop":
        if not data.get("woningwaarde"):
            warnings.append("Woonsituatie: Woningwaarde ontbreekt")
        if not data.get("hypotheekbedrag") and not data.get("hypotheek_maandlasten"):
            warnings.append("Woonsituatie: Hypotheekgegevens ontbreken")

    # Check financial products
    financial_products = data.get("financiele_producten", [])
    if not financial_products:
        warnings.append("Financiële producten: Geen producten geselecteerd")

    # Check organized affairs
    if data.get("heeft_testament") is None:
        warnings.append("Geordende zaken: Testament-status ontbreekt")
    if data.get("pensioenopbouw_actief") is None:
        warnings.append("Geordende zaken: Pensioenopbouw-status ontbreekt")

    # Check assets
    total_assets = (
        data.get("spaarsaldo", 0)
        + data.get("auto_waarde", 0)
        + data.get("beleggingen_waarde", 0)
        + data.get("overige_bezittingen_waarde", 0)
    )
    if total_assets == 0:
        warnings.append("Bezittingen: Geen bezittingen ingevuld")

    # Check income
    if not data.get("primair_inkomen"):
        warnings.append("Inkomsten & uitgaven: Primair inkomen ontbreekt")
    if not data.get("vaste_lasten") and not data.get("variabele_kosten"):
        warnings.append("Woonsituatie: Uitgavengegevens ontbreken")

    # Check goals
    if not data.get("doel_1_naam"):
        warnings.append("Doelen: Geen financiële doelen ingevuld")
    elif data.get("doel_1_naam") and not data.get("doel_1_bedrag"):
        warnings.append("Doelen: Doelbedrag voor eerste doel ontbreekt")

    return warnings


def display_data_completeness_warnings(data: Dict[str, Any], mode: str) -> None:
    """Display warnings for missing data in the questionnaire.

    Parameters
    ----------
    data : Dict[str, Any]
        Questionnaire data
    mode : str
        Questionnaire mode ('quick' or 'comprehensive')
    """
    if mode == "comprehensive":
        warnings = validate_comprehensive_data_completeness(data)

        if warnings:
            st.warning("⚠️ **Ontbrekende gegevens gedetecteerd**")
            st.write("Voor een completere analyse missen we nog gegevens over:")
            for warning in warnings:
                st.write(f"• {warning}")
            st.write("---")
            st.info(
                "💡 Je kunt de APK later opnieuw doen om deze gegevens aan te vullen."
            )

    # For quick mode, we already have the existing validation


def create_cash_flow_visualization(data: FinancieleAPKData) -> go.Figure:
    """Create a bar chart visualization for monthly cash flow.

    Parameters
    ----------
    data : FinancieleAPKData
        Complete financial data structure

    Returns
    -------
    go.Figure
        Plotly figure showing income, expenses, and leftover amount
    """
    categories = ["Inkomsten", "Uitgaven", "Over/Tekort"]
    amounts = [data.monthly_income, data.monthly_expenses, data.monthly_leftover]
    colors = ["green", "red", "blue" if data.monthly_leftover >= 0 else "orange"]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=categories,
            y=amounts,
            marker_color=colors,
            text=[f"€{amt:,.0f}" for amt in amounts],
            textposition="auto",
        )
    )

    fig.update_layout(
        title="Maandelijkse Kasstromen",
        xaxis_title="Categorieën",
        yaxis_title="Bedrag (€)",
        showlegend=False,
        height=400,
    )

    return fig


def create_net_worth_visualization(data: FinancieleAPKData) -> go.Figure:
    """Create a bar chart visualization for net worth calculation.

    Parameters
    ----------
    data : FinancieleAPKData
        Complete financial data structure

    Returns
    -------
    go.Figure
        Plotly figure showing assets, liabilities, and net worth
    """
    net_worth = data.total_assets - data.total_debt

    categories = ["Bezittingen", "Schulden", "Eigen Vermogen"]
    # Make debt negative for visualization
    amounts = [data.total_assets, -data.total_debt, net_worth]
    colors = ["green", "red", "blue" if net_worth >= 0 else "orange"]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=categories,
            y=amounts,
            marker_color=colors,
            text=[f"€{abs(amt):,.0f}" for amt in amounts],
            textposition="auto",
        )
    )

    fig.update_layout(
        title="Eigen Vermogen Overzicht",
        xaxis_title="Categorieën",
        yaxis_title="Bedrag (€)",
        showlegend=False,
        height=400,
    )

    return fig


def display_summary(data: FinancieleAPKData) -> None:
    """Display comprehensive Financiele APK summary with metrics and visualizations.

    Calculates and displays key financial metrics including net worth and
    monthly leftover from the provided financial data, along with interactive
    charts showing cash flow and net worth breakdown.

    Parameters
    ----------
    data : FinancieleAPKData
        Complete financial data structure containing all user inputs and
        calculated values

    Returns
    -------
    None
        This function updates the Streamlit UI directly with metrics and charts

    Example
    -------
    >>> # In Streamlit context:
    >>> data = FinancieleAPKData(
    ...     monthly_income=3000.0, monthly_expenses=2500.0,
    ...     monthly_leftover=500.0, total_assets=10000.0, total_debt=5000.0,
    ...     assets=[], liabilities=[], income_streams=[], expense_streams=[]
    ... )
    >>> display_summary(data)
    # Displays metrics and charts for Financiele APK

    Note
    ----
    Uses the user-provided monthly_leftover value instead of calculating it.
    Includes interactive visualizations for better understanding of cash flow
    and net worth.
    """
    # Calculate totals from the data
    net_worth = data.total_assets - data.total_debt
    # Use the user-provided monthly_leftover instead of calculating it
    monthly_leftover = data.monthly_leftover

    # Display summary metrics
    st.write("### 📊 Financiele APK")

    # Assets, Liabilities, and Net Worth
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Totale Bezittingen", f"€{data.total_assets:,.2f}")
    with col2:
        st.metric("Totale Schulden", f"€{data.total_debt:,.2f}")
    with col3:
        st.metric("Eigen Vermogen", f"€{net_worth:,.2f}")

    st.write("---")

    # Monthly Cash Flow
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Maandelijkse Inkomsten", f"€{data.monthly_income:,.2f}")
    with col2:
        st.metric("Maandelijkse Uitgaven", f"€{data.monthly_expenses:,.2f}")
    with col3:
        label = "Maandelijks Over" if monthly_leftover >= 0 else "Maandelijks Tekort"
        delta_color = "normal" if monthly_leftover >= 0 else "inverse"
        st.metric(
            label,
            f"€{abs(monthly_leftover):,.2f}",
            delta=f"{'Positief' if monthly_leftover >= 0 else 'Negatief'} saldo",
            delta_color=delta_color,
        )

    st.write("---")

    # Visualizations Section
    st.write("### 📈 Visualisatie")

    # Create two columns for the charts
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Maandelijks overzicht**")
        cash_flow_fig = create_cash_flow_visualization(data)
        st.plotly_chart(cash_flow_fig, use_container_width=True)

        # Text summary for cash flow
        if data.monthly_leftover > 0:
            st.success(
                f"✅ Je houdt maandelijks €{data.monthly_leftover:,.2f} over "
                f"voor sparen/beleggen"
            )
        elif data.monthly_leftover < 0:
            st.error(
                f"⚠️ Je hebt een maandelijks tekort van "
                f"€{abs(data.monthly_leftover):,.2f}"
            )
        else:
            st.warning("💡 Je inkomsten en uitgaven zijn precies gelijk")

    with col2:
        st.write("**Vermogen overzicht**")
        net_worth_fig = create_net_worth_visualization(data)
        st.plotly_chart(net_worth_fig, use_container_width=True)

        # Text summary for net worth
        if net_worth > 0:
            st.success(f"💰 Je eigen vermogen is €{net_worth:,.2f}")
        elif net_worth < 0:
            st.error(
                f"📉 Je hebt een negatief eigen vermogen van €{abs(net_worth):,.2f}"
            )
        else:
            st.warning("💡 Je bezittingen en schulden zijn gelijk aan elkaar")


def show_financiele_apk() -> None:
    """Display the complete Financiele APK calculator interface.

    Main entry point for the Financiele APK calculator. Implements a step-by-step
    flow starting with onboarding, then questionnaire, and finally results.

    Returns
    -------
    None
        This function creates Streamlit UI components directly

    Example
    -------
    >>> # In Streamlit app:
    >>> show_financiele_apk()
    # Creates expandable "💶 Financiele APK" section with step-by-step flow

    Note
    ----
    Uses session state to track progress through the assessment steps.
    Starts with onboarding, then moves to questionnaire and results.
    """
    with st.expander("💶 Financiele APK", expanded=True):
        # Initialize session state for APK flow
        if "apk_step" not in st.session_state:
            st.session_state.apk_step = "onboarding"
        if "apk_started" not in st.session_state:
            st.session_state.apk_started = False

        # Step 1: Onboarding
        if st.session_state.apk_step == "onboarding":
            if show_onboarding():
                st.session_state.apk_step = "questionnaire"
                st.session_state.apk_started = True
                st.rerun()

        # Step 2: Questionnaire
        elif st.session_state.apk_step == "questionnaire":
            st.write("### Financiele APK - Uitgebreide Vragenlijst")

            # Add mode selection
            if "apk_mode" not in st.session_state:
                st.session_state.apk_mode = None

            if st.session_state.apk_mode is None:
                st.write("Kies je voorkeur:")
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "🚀 Snelle APK",
                        key="quick_mode",
                        help="4 basis vragen voor een snelle analyse",
                    ):
                        st.session_state.apk_mode = "quick"
                        st.rerun()

                with col2:
                    if st.button(
                        "📊 Uitgebreide APK",
                        key="comprehensive_mode",
                        help="Volledige analyse met 8 categorieën",
                    ):
                        st.session_state.apk_mode = "comprehensive"
                        st.rerun()

                return  # Don't proceed until mode is selected

            # Run the selected questionnaire mode
            if st.session_state.apk_mode == "quick":
                # Show progress at 20% when questionnaire starts
                display_progress_indicator(
                    progress_value=0.2,
                    title="Voortgang Financiële APK - Snelle Modus",
                    subtitle="Vragenlijst gestart",
                    show_percentage=True,
                )

                questionnaire = create_financiele_apk_questionnaire()
                questionnaire_data = questionnaire.run()

                # If questionnaire is completed, show results
                if questionnaire_data is not None:
                    st.session_state.apk_step = "results"
                    st.session_state.questionnaire_data = questionnaire_data
                    st.rerun()

            elif st.session_state.apk_mode == "comprehensive":
                # Use the comprehensive categorical questionnaire
                questionnaire = create_comprehensive_financiele_apk_questionnaire()
                questionnaire_data = questionnaire.run()

                # If questionnaire is completed, show results
                if questionnaire_data is not None:
                    st.session_state.apk_step = "results"
                    st.session_state.questionnaire_data = questionnaire_data
                    st.rerun()

        # Step 3: Results
        elif st.session_state.apk_step == "results":
            # Show progress at 100% when showing results
            display_progress_indicator(
                progress_value=1.0,
                title="Voortgang Financiële APK",
                subtitle="APK voltooid!",
                show_percentage=True,
            )

            questionnaire_data = st.session_state.get("questionnaire_data", {})
            apk_mode = st.session_state.get("apk_mode", "quick")

            # Convert questionnaire data to Financiele APK data based on mode
            if apk_mode == "comprehensive":
                financial_data = comprehensive_data_to_financiele_apk(
                    questionnaire_data
                )

                # For comprehensive mode, skip the old validation since we have detailed data
                st.success(
                    "Uitgebreide APK voltooid! Hier is je complete Financiele APK:"
                )

                # Display completeness warnings
                display_data_completeness_warnings(questionnaire_data, apk_mode)

            else:
                # Original quick mode validation and conversion
                monthly_income = questionnaire_data.get("monthly_income", 0.0)
                monthly_expenses = questionnaire_data.get("monthly_expenses", 0.0)
                monthly_leftover = questionnaire_data.get("monthly_leftover", 0.0)

                is_consistent, warning_message = validate_financial_consistency(
                    monthly_income, monthly_expenses, monthly_leftover
                )

                if not is_consistent:
                    st.warning(warning_message)
                    st.info(
                        "💡 We gebruiken je opgegeven bedragen, maar controleer "
                        "deze nog even."
                    )

                financial_data = questionnaire_data_to_financiele_apk(
                    questionnaire_data
                )
                st.success("Snelle APK voltooid! Hier is je Financiele APK:")

            st.write("---")

            # Display the summary
            display_summary(financial_data)

            # Add reset button to allow starting over
            st.write("---")
            if st.button("Nieuwe APK starten", key="reset_questionnaire"):
                # Reset session state to restart the flow
                st.session_state.apk_step = "onboarding"
                st.session_state.apk_started = False
                if "apk_mode" in st.session_state:
                    del st.session_state.apk_mode
                if "questionnaire_data" in st.session_state:
                    del st.session_state.questionnaire_data
                # Also reset questionnaire data for both modes
                quick_questionnaire = create_financiele_apk_questionnaire()
                quick_questionnaire.reset()
                comprehensive_questionnaire = (
                    create_comprehensive_financiele_apk_questionnaire()
                )
                comprehensive_questionnaire.reset()
                st.rerun()
