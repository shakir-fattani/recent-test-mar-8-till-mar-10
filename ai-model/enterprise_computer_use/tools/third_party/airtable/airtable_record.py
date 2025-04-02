"""Airtable tools for interacting with Airtable API.

Refer to https://pyairtable.readthedocs.io/en/stable/tables.html for more information.
"""

import logging
import os
from typing import Any, ClassVar, Literal

from pyairtable import Api

from enterprise_computer_use.tools.base import BaseTool, CLIResult, ToolError

logger = logging.getLogger(__name__)


class AirtableRecordTool(BaseTool):
    """
    A tool for interacting with Airtable Python SDK.
    Supports operations like listing records, creating records, and updating records.

    Available commands:
        - all: Retrieve all records from an Airtable table (base_id and table_id are required)
        - create: Create a new record in an Airtable table (record_data, base_id, table_id are required)
        - batch_create: Create multiple records in an Airtable table (records_data, base_id, table_id are required, up to 10 records per batch)
        - update: Update an existing record in an Airtable table (record_data, record_id, base_id, table_id are required)
        - batch_update: Update multiple records in an Airtable table (records_data, base_id, table_id are required, up to 10 records per batch)
        - delete: Delete a record from an Airtable table (record_id, base_id, table_id are required)
        - batch_delete: Delete multiple records from an Airtable table (record_ids, base_id, table_id are required, up to 10 records per batch)
        - filter: Filter records using a formula (formula, base_id, table_id are required)

    Example inputs and outputs:
        All records:
            Input: {"command": "all", "base_id": "appExampleBaseId", "table_id": "tblExampleTableId"}
            Output: [
                {
                    "id": "rec5eR7IzKSAOBHCz",
                    "createdTime": "2017-03-14T22:04:31.000Z",
                    "fields": {
                        "Name": "Alice",
                        "Email": "alice@example.com"
                    }
                }
            ]

        Create record:
            Input: {
                "command": "create",
                "base_id": "appExampleBaseId",
                "table_id": "tblExampleTableId",
                "record_data": {"Name": "Bob"}
            }
            Output: {
                "id": "recwAcQdqwe21asdf",
                "createdTime": "...",
                "fields": {"Name": "Bob"}
            }

        Update record:
            Input: {
                "command": "update",
                "base_id": "appExampleBaseId",
                "table_id": "tblExampleTableId",
                "record_id": "recwAcQdqwe21asdf",
                "record_data": {"Name": "Robert"}
            }
            Output: {
                "id": "recwAcQdqwe21asdf",
                "createdTime": "...",
                "fields": {"Name": "Robert"}
            }

        Delete record:
            Input: {
                "command": "delete",
                "base_id": "appExampleBaseId",
                "table_id": "tblExampleTableId",
                "record_id": "recwAcQdqwe21asdf"
            }
            Output: {'id': 'recwAcQdqwe21asdf', 'deleted': True}

        Batch create records:
            Input: {
                "command": "batch_create",
                "base_id": "appExampleBaseId",
                "table_id": "tblExampleTableId",
                "records_data": [{"Name": "Bob"}, {"Name": "Alice"}]
            }
            Output: [
                {"id": "rec1", "fields": {"Name": "Bob"}},
                {"id": "rec2", "fields": {"Name": "Alice"}}
            ]

        Batch update records:
            Input: {
                "command": "batch_update",
                "base_id": "appExampleBaseId",
                "table_id": "tblExampleTableId",
                "records_data": [
                    {"id": "rec1", "fields": {"Name": "Robert"}},
                    {"id": "rec2", "fields": {"Name": "Alicia"}}
                ]
            }
            Output: [
                {"id": "rec1", "fields": {"Name": "Robert"}},
                {"id": "rec2", "fields": {"Name": "Alicia"}}
            ]

        Batch delete records:
            Input: {
                "command": "batch_delete",
                "base_id": "appExampleBaseId",
                "table_id": "tblExampleTableId",
                "record_ids": ["rec1", "rec2"]
            }
            Output: [
                {"id": "rec1", "deleted": true},
                {"id": "rec2", "deleted": true}
            ]
    """

    name: ClassVar[Literal["airtable_record"]] = "airtable_record"

    def __init__(self):
        """Initialize Airtable tool."""
        api_key = os.getenv("AIRTABLE_API_KEY")
        if not api_key:
            raise ToolError("AIRTABLE_API_KEY environment variable not set")
        self.api = Api(api_key)
        super().__init__()

    async def __call__(
        self,
        *,
        command: Literal[
            "all",
            "create",
            "batch_create",
            "update",
            "batch_update",
            "delete",
            "batch_delete",
            "filter",
        ],
        base_id: str,
        table_id: str | None = None,
        record_data: dict[str, Any] | None = None,
        records_data: list[dict[str, Any]] | None = None,
        record_id: str | None = None,
        record_ids: list[str] | None = None,
        formula: str | None = None,
        **kwargs,
    ) -> CLIResult:
        """
        Execute Airtable operations.
        Args:
            command: The operation to perform (all, create, batch_create, update, batch_update, delete, batch_delete, filter)
            base_id: Airtable base ID (starts with 'app')
            table_id: Airtable table ID (starts with 'tbl')
            record_data: Data for single create/update operations
            records_data: Data for batch create/update operations
            record_id: Record ID for update/delete operations
            record_ids: List of record IDs for batch delete operations
            formula: Formula string for filtering records

        Returns:
            CLIResult containing operation output or error
        """
        try:
            if not table_id:
                raise ToolError("table_id is required for this operation")
            table = self.api.table(base_id, table_id)

            if command == "all":
                records = table.all()
                return CLIResult(
                    output=f"Retrieved {len(records)} records: {records}"
                )
            elif command == "create":
                if not record_data:
                    raise ToolError(
                        "record_data is required for create operation"
                    )
                record = table.create(record_data)
                return CLIResult(output=f"Created record: {record}")
            elif command == "batch_create":
                if not records_data:
                    raise ToolError(
                        "records_data is required for batch create operation"
                    )
                records = table.batch_create(records_data)
                return CLIResult(
                    output=f"Created {len(records)} records: {records}"
                )
            elif command == "update":
                if not record_data or not record_id:
                    raise ToolError(
                        "record_data and record_id are required for update operation"
                    )
                record = table.update(record_id, record_data)
                return CLIResult(output=f"Updated record: {record}")
            elif command == "batch_update":
                if not records_data:
                    raise ToolError(
                        "records_data is required for batch update operation"
                    )
                records = table.batch_update(records_data)  # type: ignore
                return CLIResult(
                    output=f"Updated {len(records)} records: {records}"
                )
            elif command == "delete":
                if not record_id:
                    raise ToolError(
                        "record_id is required for delete operation"
                    )
                result = table.delete(record_id)
                return CLIResult(output=f"Delete result: {result}")
            elif command == "batch_delete":
                if not record_ids:
                    raise ToolError(
                        "record_ids is required for batch delete operation"
                    )
                result = table.batch_delete(record_ids)
                return CLIResult(
                    output=f"Deleted {len(result)} records: {result}"
                )
            elif command == "filter":
                if not formula:
                    raise ToolError("formula is required for filter operation")
                records = table.all(formula=formula)
                return CLIResult(
                    output=f"Found {len(records)} matching records: {records}"
                )

        except Exception as e:
            raise ToolError(f"Airtable operation failed: {str(e)}") from e

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
                                "all",
                                "create",
                                "batch_create",
                                "update",
                                "batch_update",
                                "delete",
                                "batch_delete",
                                "filter",
                            ],
                            "description": "The Airtable operation to perform",
                        },
                        "base_id": {
                            "type": "string",
                            "description": "Airtable base ID (starts with 'app')",
                        },
                        "table_id": {
                            "type": "string",
                            "description": "Airtable table ID (starts with 'tbl')",
                        },
                        "record_data": {
                            "type": "object",
                            "description": "Data for single create/update operations",
                        },
                        "records_data": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "List of records for batch create/update operations",
                        },
                        "record_id": {
                            "type": "string",
                            "description": "Record ID for update/delete operations",
                        },
                        "record_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of record IDs for batch delete operations",
                        },
                        "formula": {
                            "type": "string",
                            "description": "Formula string for filtering records (use airtable_formula tool to create formulas)",
                        },
                    },
                    "required": ["command", "base_id"],
                },
            }

        # Add a catch-all return or raise an exception
        raise ValueError(
            f"Model {model} is not supported. Please specify a supported model type."
        )
