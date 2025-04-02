"""This module contains the project registry."""

import os

from enterprise_computer_use.registry import OSType, ProjectType

os_type = os.environ.get("OS")
project = os.environ.get("PROJECT")

if not os_type:
    raise ValueError("OS environment variable must be set")

if not project:
    raise ValueError("PROJECT environment variable must be set")

if os_type not in [os_type.value for os_type in OSType]:
    raise ValueError(
        f"Invalid OS: {os_type}. Must be one of: "
        f"{[os_type.value for os_type in OSType]}"
    )

if project not in [proj.value for proj in ProjectType]:
    raise ValueError(
        f"Invalid PROJECT: {project}. Must be one of: "
        f"{[proj.value for proj in ProjectType]}"
    )

# Import the appropriate project based on the OS type to register it with the
# registry. These imports are used for their side effects.
if os_type == OSType.LINUX.value:
    if project == ProjectType.CLAUDE_COMPUTER_USE.value:
        from enterprise_computer_use.project import (
            linux_claude_computer_use,  # noqa: F401
        )
    elif project == ProjectType.AIRTABLE_COMPUTER_USE.value:
        from enterprise_computer_use.project import (
            linux_airtable_computer_use,  # noqa: F401
        )
    elif project == ProjectType.CONCUR_COMPUTER_USE.value:
        from enterprise_computer_use.project import (
            linux_concur_computer_use,  # noqa: F401
        )
    elif project == ProjectType.PLANNER_GROUNDING_COMPUTER_USE.value:
        from enterprise_computer_use.project import (
            linux_planner_grounding_computer_use,  # noqa: F401
        )
    elif project == ProjectType.COMPUTER_USE.value:
        from enterprise_computer_use.project import (
            linux_computer_use,  # noqa: F401
        )
elif os_type == OSType.MAC.value:
    from enterprise_computer_use.project import (
        mac_claude_computer_use,  # noqa: F401
    )
else:
    raise ValueError(
        f"Invalid OS: {os_type}. Must be one of: "
        f"{[os_type.value for os_type in OSType]}"
    )
