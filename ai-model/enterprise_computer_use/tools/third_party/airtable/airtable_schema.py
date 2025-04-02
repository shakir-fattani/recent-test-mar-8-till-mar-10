"""Airtable metadata tools for interacting with Airtable API metadata.

Refer to https://pyairtable.readthedocs.io/en/stable/metadata.html for more information.
"""

import logging
import os
from typing import Any, ClassVar, Literal

from pyairtable import Api

from enterprise_computer_use.tools.base import BaseTool, CLIResult, ToolError

logger = logging.getLogger(__name__)


class AirtableSchemaTool(BaseTool):
    """
    A tool for interacting with Airtable metadata API.
    Supports operations like listing bases, retrieving table schemas, and managing fields.

    Available commands:
        - list_bases: List all accessible bases
        - get_base_schema: Get schema for a specific base
        - list_tables: List all tables in a base
        - get_table_schema: Get schema for a specific table
        - create_table: Create a new table in a base
        - create_field: Create a new field in a table

    Example inputs and outputs:
        List bases:
            Input: {"command": "list_bases"}
            Output: [
                {
                    "id": "appExampleBaseId",
                    "name": "My Base"
                }
            ]

        Get base schema:
            Input: {"command": "get_base_schema", "base_id": "appExampleBaseId"}
            Output: {
                "tables": [
                    {
                        "id": "tblExampleTableId",
                        "name": "My Table",
                        "fields": [...]
                    }
                ]
            }

        Create table:
            Input: {
                "command": "create_table",
                "base_id": "appExampleBaseId",
                "table_name": "New Table",
                "fields": [
                    {
                        "name": "Text Field",
                        "type": "singleLineText"
                    },
                    {
                        "name": "Number Field",
                        "type": "number",
                        "options": {
                            "precision": 2
                        }
                    },
                    {
                        "name": "Currency Field",
                        "type": "currency",
                        "options": {
                            "precision": 2,
                            "symbol": "$"
                        }
                    },
                    {
                        "name": "Categories",
                        "type": "multipleSelects",
                        "options": {
                            "choices": [
                                {"name": "category1", "color": "blueLight2"},
                                {"name": "category2", "color": "greenLight2"}
                            ]
                        }
                    }
                ]
            }

        Field Types and Required Options:
            - Text fields:
                - singleLineText: No options required
                - multiLineText: No options required
                - email: No options required
                - url: No options required

            - Numeric fields:
                - number: options: {"precision": 0-8}
                - currency: options: {"precision": 0-8, "symbol": "$"}
                - percent: options: {"precision": 0-8}

            - Selection fields:
                - singleSelect: options: {"choices": [{"name": "choice", "color": "colorName"}]}
                - multipleSelects: options: {"choices": [{"name": "choice", "color": "colorName"}]}

            - Other fields:
                - date: No options required
                - checkbox: No options required
                - attachment: No options required

        Available colors for select fields:
            Light variants (recommended): blueLight2, greenLight2, redLight2, yellowLight2,
            orangeLight2, pinkLight2, purpleLight2, tealLight2, cyanLight2, grayLight2
    """

    name: ClassVar[Literal["airtable_schema"]] = "airtable_schema"

    def __init__(self):
        """Initialize Airtable schema tool."""
        api_key = os.getenv("AIRTABLE_API_KEY")
        if not api_key:
            raise ToolError("AIRTABLE_API_KEY environment variable not set")
        self.api = Api(api_key)
        super().__init__()

    async def __call__(
        self,
        *,
        command: Literal[
            "list_bases",
            "get_base_schema",
            "list_tables",
            "get_table_schema",
            "create_table",
            "create_field",
        ],
        base_id: str | None = None,
        table_id: str | None = None,
        table_name: str | None = None,
        field_name: str | None = None,
        field_type: str | None = None,
        field_description: str | None = None,
        field_options: dict[str, Any] | None = None,
        fields: list[dict[str, Any]] | None = None,
        **kwargs,
    ) -> CLIResult:
        """
        Execute Airtable metadata operations.

        Args:
            command: The operation to perform
            base_id: Airtable base ID (starts with 'app')
            table_id: Airtable table ID (starts with 'tbl')
            table_name: Name for new table
            field_name: Name for new field
            field_type: Type for new field
            field_description: Description for new field
            field_options: Options for new field
            fields: List of field definitions for new table

        Returns:
            CLIResult containing operation output or error
        """
        try:
            if command == "list_bases":
                bases = self.api.bases()
                return CLIResult(
                    output=f"Retrieved {len(bases)} bases: {bases}"
                )

            if not base_id:
                raise ToolError("base_id is required for this operation")
            base = self.api.base(base_id)

            if command == "get_base_schema":
                schema = base.schema()
                return CLIResult(output=f"Retrieved base schema: {schema}")

            elif command == "list_tables":
                tables = base.tables()
                return CLIResult(
                    output=f"Retrieved {len(tables)} tables: {tables}"
                )

            elif command == "get_table_schema":
                if not table_id:
                    raise ToolError("table_id is required for get_table_schema")
                table = base.table(table_id)
                schema = table.schema()
                return CLIResult(output=f"Retrieved table schema: {schema}")

            elif command == "create_table":
                if not table_name or not fields:
                    raise ToolError(
                        "table_name and fields are required for create_table"
                    )
                table = base.create_table(table_name, fields)
                return CLIResult(output=f"Created table: {table}")

            elif command == "create_field":
                if not table_id or not field_name or not field_type:
                    raise ToolError(
                        "table_id, field_name, and field_type are required for create_field"
                    )
                table = base.table(table_id)
                field = table.create_field(
                    name=field_name,
                    field_type=field_type,
                    description=field_description,
                    options=field_options,
                )
                return CLIResult(output=f"Created field: {field}")

        except Exception as e:
            raise ToolError(
                f"Airtable metadata operation failed: {str(e)}"
            ) from e

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
                            "enum": [
                                "list_bases",
                                "get_base_schema",
                                "list_tables",
                                "get_table_schema",
                                "create_table",
                                "create_field",
                            ],
                            "description": "The Airtable metadata operation to perform",
                        },
                        "base_id": {
                            "type": "string",
                            "description": "Airtable base ID (starts with 'app')",
                        },
                        "table_id": {
                            "type": "string",
                            "description": "Airtable table ID (starts with 'tbl')",
                        },
                        "table_name": {
                            "type": "string",
                            "description": "Name for the new table",
                        },
                        "field_name": {
                            "type": "string",
                            "description": "Name for the new field",
                        },
                        "field_type": {
                            "type": "string",
                            "description": "Type for the new field",
                        },
                        "field_description": {
                            "type": "string",
                            "description": "Description for the new field",
                        },
                        "field_options": {
                            "type": "object",
                            "description": "Options for the new field",
                        },
                        "fields": {
                            "type": "array",
                            "description": "List of field definitions for new table",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                },
                            },
                        },
                    },
                    "required": ["command"],
                },
            }

        # Add a catch-all return or raise an exception
        raise ValueError(
            f"Model {model} is not supported. Please specify a supported model type."
        )
