"""Airtable formula tools for creating complex query formulas.

This module provides tools for building Airtable formulas using the pyairtable.formulas module.
Refer to: https://pyairtable.readthedocs.io/en/stable/formulas.html for more details.
"""

from typing import Any, ClassVar, Literal

from pyairtable.formulas import (
    AND,
    DATETIME_DIFF,
    EQ,
    GT,
    GTE,
    LT,
    LTE,
    NE,
    NOT,
    OR,
    TODAY,
    XOR,
    Field,
    match as airtable_match,
)

from enterprise_computer_use.tools.base import BaseTool, CLIResult, ToolError


class AirtableFormulaTool(BaseTool):
    """
    A tool for creating Airtable formulas for complex queries.

    Available commands:
        - match: Create formula for matching field values with various operators
        - compound: Create compound formulas using logical operators (AND, OR, NOT, XOR)
        - datetime: Create datetime comparison formulas

    Example inputs and outputs:
        Match formula:
            Input: {
                "command": "match",
                "field_values": {"Name": "Bob", "Age": [">=", 21]},
                "match_any": false
            }
            Output: "AND({Name}='Bob', {Age}>=21)"

        Compound formula:
            Input: {
                "command": "compound",
                "operator": "and",
                "conditions": [
                    {"field": "Customer", "op": "eq", "value": "Alice"},
                    {"field": "Status", "op": "ne", "value": "Cancelled"}
                ]
            }
            Output: "AND({Customer}='Alice', {Status}!='Cancelled')"

        Datetime formula:
            Input: {
                "command": "datetime",
                "field": "Purchase Date",
                "days_ago": 7,
                "comparison": ">="
            }
            Output: "DATETIME_DIFF(TODAY(), {Purchase Date}, 'days')>=7"
    """

    name: ClassVar[Literal["airtable_formula"]] = "airtable_formula"

    OPERATORS = {"eq": EQ, "ne": NE, "gt": GT, "gte": GTE, "lt": LT, "lte": LTE}

    LOGICAL_OPS = {"and": AND, "or": OR, "not": NOT, "xor": XOR}

    async def __call__(
        self,
        *,
        command: Literal["match", "compound", "datetime"],
        field_values: dict[str, Any] | None = None,
        match_any: bool = False,
        operator: str | None = None,
        conditions: list[dict] | None = None,
        field: str | None = None,
        days_ago: int | None = None,
        comparison: str | None = None,
        **kwargs,
    ) -> CLIResult:
        """
        Create Airtable formulas based on the specified command and parameters.

        Args:
            command: The type of formula to create
            field_values: Dictionary of field names and values for match command
            match_any: Whether to use OR instead of AND for match command
            operator: Logical operator for compound formulas (and, or, not, xor)
            conditions: List of conditions for compound formulas
            field: Field name for datetime formulas
            days_ago: Number of days for datetime comparison
            comparison: Comparison operator for datetime formula

        Returns:
            CLIResult containing the formula string
        """
        try:
            if command == "match":
                if not field_values:
                    raise ToolError(
                        "field_values is required for match command"
                    )
                formula = airtable_match(field_values, match_any=match_any)
                return CLIResult(output=str(formula))

            elif command == "compound":
                if not operator or not conditions:
                    raise ToolError(
                        "operator and conditions are required for compound command"
                    )

                if operator not in self.LOGICAL_OPS:
                    raise ToolError(
                        f"Invalid operator. Must be one of: {', '.join(self.LOGICAL_OPS.keys())}"
                    )

                formula_parts = []
                for condition in conditions:
                    if not all(
                        k in condition for k in ["field", "op", "value"]
                    ):
                        raise ToolError(
                            "Each condition must have field, op, and value"
                        )
                    if condition["op"] not in self.OPERATORS:
                        raise ToolError(
                            f"Invalid operator. Must be one of: {', '.join(self.OPERATORS.keys())}"
                        )

                    formula_parts.append(
                        self.OPERATORS[condition["op"]](
                            Field(condition["field"]), condition["value"]
                        )
                    )

                formula = self.LOGICAL_OPS[operator](*formula_parts)
                return CLIResult(output=str(formula))

            elif command == "datetime":
                if not all([field, days_ago is not None, comparison]):
                    raise ToolError(
                        "field, days_ago, and comparison are required for datetime command"
                    )
                if comparison not in self.OPERATORS:
                    raise ToolError(
                        f"Invalid comparison. Must be one of: {', '.join(self.OPERATORS.keys())}"
                    )

                formula = self.OPERATORS[comparison](
                    DATETIME_DIFF(TODAY(), Field(field), "days"),  # type: ignore
                    days_ago,
                )
                return CLIResult(output=str(formula))

        except Exception as e:
            raise ToolError(f"Formula creation failed: {str(e)}") from e

    def to_params(self, **kwargs) -> dict[str, Any]:
        """Convert tool to function parameters for LLM."""
        model = kwargs.get("model")

        if model == "claude":
            return {
                "name": self.name,
                "description": self.__class__.__doc__,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "enum": ["match", "compound", "datetime"],
                            "description": "The type of formula to create",
                        },
                        "field_values": {
                            "type": "object",
                            "additionalProperties": True,
                            "description": "Dictionary of field names and values for match command. Values can be direct values or [operator, value] tuples for comparisons",
                        },
                        "match_any": {
                            "type": "boolean",
                            "description": "If True, matches if any field matches; if False, all fields must match",
                            "default": False,
                        },
                        "operator": {
                            "type": "string",
                            "enum": ["and", "or", "not", "xor"],
                            "description": "Logical operator for compound formulas",
                        },
                        "conditions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "field": {"type": "string"},
                                    "op": {
                                        "type": "string",
                                        "enum": list(self.OPERATORS.keys()),
                                    },
                                    "value": {},  # Allow any value type
                                },
                                "required": ["field", "op", "value"],
                            },
                            "description": "List of conditions for compound formulas",
                        },
                        "field": {
                            "type": "string",
                            "description": "Field name for datetime formulas",
                        },
                        "days_ago": {
                            "type": "integer",
                            "description": "Number of days for datetime comparison",
                        },
                        "comparison": {
                            "type": "string",
                            "enum": list(self.OPERATORS.keys()),
                            "description": "Comparison operator for datetime formula",
                        },
                    },
                    "required": ["command"],
                },
            }

        # Add a catch-all return or raise an exception
        raise ValueError(
            f"Model {model} is not supported. Please specify a supported model type."
        )
