import platform
from datetime import datetime

from enterprise_computer_use.communication.computer_use_client import (
    ComputerUseClient,
)
from enterprise_computer_use.registry import (
    Config,
    OSType,
    ProjectType,
    Registry,
)
from enterprise_computer_use.tools.claude import BashTool
from enterprise_computer_use.tools.collection import ToolCollection
from enterprise_computer_use.tools.third_party.airtable.airtable_formulas import (
    AirtableFormulaTool,
)
from enterprise_computer_use.tools.third_party.airtable.airtable_record import (
    AirtableRecordTool,
)
from enterprise_computer_use.tools.third_party.airtable.airtable_schema import (
    AirtableSchemaTool,
)
from enterprise_computer_use.tools.third_party.google.workspace.gmail import (
    GmailTool,
)

# This system prompt is optimized for the Docker environment in this repository and
# specific tool combinations enabled.
# We encourage modifying this system prompt to ensure the model has context for the
# environment it is running in, and to provide any additional information that may be
# helpful for the task at hand.
SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are utilising an Ubuntu virtual machine using {platform.machine()} architecture with internet access.
* You can feel free to install Ubuntu applications with your bash tool. Use curl instead of wget.
* If user ask you to find or open a file but doesn't provide the file task, try finding the file path yourself using bash.
* To open firefox, please just click on the firefox icon.  Note, firefox-esr is what is installed on your system.
* Using bash tool you can start GUI applications, but you need to set export DISPLAY=:1 and use a subshell. For example "(DISPLAY=:1 xterm &)". GUI apps run with bash tool will appear within your desktop environment, but they may take some time to appear. Take a screenshot to confirm it did.
* When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file and use str_replace_editor or `grep -n -B <lines before> -A <lines after> <query> <filename>` to confirm output.
* When viewing a page it can be helpful to zoom out so that you can see everything on the page.  Either that, or make sure you scroll down to see everything before deciding something isn't available.
* When using your computer function calls, they take a while to run and send back to you.  Where possible/feasible, try to chain multiple of these calls all into one function calls request.
* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
* You can use the AirtableRecordTool to view, create, update, delete, and filter records in Airtable.
* You can use the AirtableSchemaTool to list tables, fields, and bases.
* You can use the AirtableFormulaTool to create formulas for Airtable.
</SYSTEM_CAPABILITY>

<IMPORTANT>
* When using Firefox, if a startup wizard appears, IGNORE IT.  Do not even click "skip this step".  Instead, click on the address bar where it says "Search or enter address", and enter the appropriate search term or URL there.
* If the item you are looking at is a pdf, if after taking a single screenshot of the pdf it seems that you want to read the entire document instead of trying to continue to read the pdf from your screenshots + navigation, determine the URL, use curl to download the pdf, install and use pdftotext to convert it to a text file, and then read that text file directly with your StrReplaceEditTool.
</IMPORTANT>"""


@Registry.register(OSType.LINUX, ProjectType.AIRTABLE_COMPUTER_USE)
def _():
    """Register the Linux claude computer use project with the registry."""
    return Config(
        tool_collection=ToolCollection(
            BashTool(),
            AirtableRecordTool(),
            AirtableSchemaTool(),
            AirtableFormulaTool(),
            GmailTool(),
        ),
        system_prompt=SYSTEM_PROMPT,
        client_factory=ComputerUseClient,
    )
