import json
from pathlib import Path
from typing import Optional

from daktari.check import Check, CheckResult
from daktari.file_utils import file_exists
from daktari.os import OS
from daktari.version_utils import get_simple_cli_version


class OnePasswordCliInstalled(Check):
    name = "onePasswordCli.installed"

    def __init__(self, required_version: Optional[str] = None, recommended_version: Optional[str] = None):
        self.required_version = required_version
        self.recommended_version = recommended_version
        self.suggestions = {
            OS.GENERIC: """
                Install the 1Password CLI (op):
                https://support.1password.com/command-line-getting-started/#set-up-the-command-line-tool""",
            OS.OS_X: """
                Use these commands to update 1pass-cli to correct version:
                <cmd>brew tap glean-notes/homebrew-tap git@github.com:glean-notes/homebrew-tap</cmd>
                <cmd>brew reinstall glean-notes/homebrew-tap/1password-cli</cmd>""",
        }

    def check(self) -> CheckResult:
        installed_version = get_simple_cli_version("op")
        return self.validate_semver_expression(
            "1Password CLI", installed_version, self.required_version, self.recommended_version
        )


class OnePasswordAccountConfigured(Check):
    depends_on = [OnePasswordCliInstalled]
    name = "onePassword.accountConfigured"

    def __init__(self, account_shorthand: str):
        self.account_shorthand = account_shorthand
        self.suggestions = {
            OS.GENERIC: f"<cmd>op signin --account {account_shorthand}.1password.com</cmd>",
        }

    def check(self) -> CheckResult:
            try:
                output = get_stdout("op account list")
                if f"{account_shorthand}.1password.com" in output:
                    return self.passed(f"{self.account_shorthand} is configured with OP CLI for the current user")
                else:
                    return self.failed(f"{self.account_shorthand} is not configured with OP CLI for the current user")
            except subprocess.CalledProcessError:
                return self.failed("1Password CLI command failed. Make sure it's installed and configured.")


def account_exists(path: str, account_shorthand: str) -> bool:
    with open(path) as f:
        config = json.load(f)
    return any(account.get("shorthand") == account_shorthand for account in config.get("accounts", []))
