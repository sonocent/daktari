import json
import logging
from pathlib import Path
from semver import VersionInfo
from typing import Optional

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stdout
from daktari.file_utils import file_exists
from daktari.os import OS


class OnePassInstalled(Check):
    name = "onepass.installed"

    def __init__(self, required_version: Optional[str] = None, recommended_version: Optional[str] = None):
        self.required_version = required_version
        self.recommended_version = recommended_version
        self.suggestions = {
            OS.GENERIC: "Install OP (1Password CLI): "
            "https://support.1password.com/command-line-getting-started/#set-up-the-command-line-tool",
        }

    def check(self) -> CheckResult:
        installed_version = get_op_version()
        return self.validate_semver_expression(
            "1Password CLI", installed_version, self.required_version, self.recommended_version
        )


def get_op_version() -> Optional[VersionInfo]:
    raw_version = get_stdout("op --version")
    if raw_version:
        try:
            version = VersionInfo.parse(raw_version)
        except ValueError:
            return None
        logging.debug(f"OP Version: {version}")
        return version
    return None


class OPAccountExists(Check):
    depends_on = [OnePassInstalled]
    name = "onepass.contextExists"

    def __init__(self, context_name: str):
        self.context_name = context_name
        self.suggestions = {
            OS.GENERIC: f"<cmd>op signin {context_name}.1password.com <your-email-here></cmd>",
        }

    def check(self) -> CheckResult:

        home = str(Path.home())
        possible_paths = [f"{home}/.op/config", f"{home}/.config/op/config"]

        for config_path in possible_paths:
            if file_exists(config_path):
                op_config = json.loads(open(config_path).read())
                account_json = op_config["accounts"]
                repo = next(
                    filter(lambda op_contexts: op_contexts.get("shorthand") == self.context_name, account_json), None
                )
                if repo is None:
                    return self.failed(f"{self.context_name} is not configured with OP CLI for the current user")

                return self.passed(f"{self.context_name} is configured with OP CLI for the current user")

        return self.failed("No 1Password config appears to be present on this machine.")
