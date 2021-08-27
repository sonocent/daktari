import logging
import re
from semver import VersionInfo
from typing import Optional

from daktari.check import Check, CheckResult
from daktari.command_utils import get_stdout
from daktari.os import OS


class TfenvInstalled(Check):
    name = "tfenv.installed"

    suggestions = {
        OS.OS_X: "<cmd>brew install tfenv</cmd>",
        OS.UBUNTU: """<cmd>git clone https://github.com/tfutils/tfenv.git ~/.tfenv</cmd>
                      <cmd>sudo ln -s ~/.tfenv/bin/* /usr/local/bin</cmd>""",
        OS.GENERIC: "Install tfenv: https://github.com/tfutils/tfenv",
    }

    def check(self) -> CheckResult:
        return self.verify_install("tfenv")


class TerraformInstalled(Check):
    def __init__(
        self, required_version: Optional[str] = None, recommended_version: Optional[str] = None, use_tfenv: bool = False
    ):
        self.required_version = required_version
        self.recommended_version = recommended_version
        self.name = "terraform.installed"
        self.use_tfenv = use_tfenv

        if use_tfenv:
            self.depends_on = [TfenvInstalled]

            # Read the required tf-version from tfenv (i.e. .terraform-version files)
            tfenv_version = open(".terraform-version", "r").read().strip()
            logging.debug(f"Terraform version required from .terraform-version file is: {tfenv_version}")
            self.required_version = f"=={tfenv_version}"
            self.suggestions = {OS.GENERIC: "<cmd>tfenv install</cmd>"}
        else:
            self.suggestions = {
                OS.OS_X: "<cmd>brew tap hashicorp/tap && brew install hashicorp/tap/terraform</cmd>",
                OS.GENERIC: "Install Terraform: https://learn.hashicorp.com/tutorials/terraform/install-cli",
            }

    def check(self) -> CheckResult:
        installed_version = get_terraform_version()
        return self.validate_semver_expression(
            "Terraform", installed_version, self.required_version, self.recommended_version
        )


version_pattern = re.compile("Terraform v([0-9\\.]+)")


def get_terraform_version() -> Optional[VersionInfo]:
    raw_version = get_stdout("terraform version")
    if raw_version:
        match = version_pattern.search(raw_version)
        if match:
            version_string = match.group(1)
            try:
                version = VersionInfo.parse(version_string)
            except ValueError:
                return None
            logging.debug(f"Terraform version: {version}")
            return version
    return None
