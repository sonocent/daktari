import logging
from tabulate import tabulate
from typing import Dict, Optional
from python_hosts import Hosts

from daktari.check import Check, CheckResult
from daktari.os import OS, check_env_var_exists, get_env_var_value


class WatchmanInstalled(Check):
    name = "watchman.installed"

    suggestions = {
        OS.OS_X: "<cmd>brew install watchman</cmd>",
        OS.GENERIC: "Install watchman: https://facebook.github.io/watchman/docs/install.html#buildinstall",
    }

    def check(self) -> CheckResult:
        return self.verify_install("watchman")


class MkcertInstalled(Check):
    name = "mkcert.installed"

    suggestions = {
        OS.OS_X: "<cmd>brew install mkcert</cmd>",
        OS.GENERIC: "Install mkcert: https://mkcert.dev/#installation",
    }

    def check(self) -> CheckResult:
        return self.verify_install("mkcert")


class KtlintInstalled(Check):
    name = "ktlint.installed"

    suggestions = {
        OS.OS_X: "<cmd>brew install ktlint</cmd>",
        OS.GENERIC: "Install ktlint: https://github.com/pinterest/ktlint#installation",
    }

    def check(self) -> CheckResult:
        return self.verify_install("ktlint")


class JqInstalled(Check):
    name = "jq.installed"

    suggestions = {
        OS.OS_X: "<cmd>brew install jq</cmd>",
        OS.UBUNTU: "<cmd>sudo apt install jq</cmd>",
        OS.GENERIC: "Install jq: https://stedolan.github.io/jq/download/",
    }

    def check(self) -> CheckResult:
        return self.verify_install("jq")


class FlywayInstalled(Check):
    name = "flyway.installed"

    suggestions = {
        OS.OS_X: "<cmd>brew install flyway</cmd>",
        OS.UBUNTU: "<cmd>snap install flyway</cmd>",
        OS.GENERIC: "Install flyway: https://flywaydb.org/documentation/usage/commandline/#download-and-installation",
    }

    def check(self) -> CheckResult:
        return self.verify_install("flyway", "-v")


class ShellcheckInstalled(Check):
    name = "shellcheck.installed"

    suggestions = {
        OS.OS_X: "<cmd>brew install shellcheck</cmd>",
        OS.UBUNTU: "<cmd>sudo apt install shellcheck</cmd>",
        OS.GENERIC: "Install shellcheck: https://github.com/koalaman/shellcheck#user-content-installing",
    }

    def check(self) -> CheckResult:
        return self.verify_install("shellcheck")


class MakeInstalled(Check):
    name = "make.installed"

    suggestions = {
        OS.OS_X: "<cmd>xcode-select --install</cmd>",
        OS.UBUNTU: "<cmd>sudo apt install make</cmd>",
        OS.GENERIC: "Install make: https://www.gnu.org/software/make/",
    }

    def check(self) -> CheckResult:
        return self.verify_install("make")


class GccInstalled(Check):
    name = "gcc.installed"

    suggestions = {
        OS.OS_X: "<cmd>xcode-select --install</cmd>",
        OS.UBUNTU: "<cmd>sudo apt install gcc</cmd>",
        OS.GENERIC: "Install gcc: https://gcc.gnu.org/",
    }

    def check(self) -> CheckResult:
        return self.verify_install("gcc")


class EnvVarSet(Check):
    def __init__(self, variable_name: str, variable_value: Optional[str] = "", provision_command: str = ""):
        self.name = f"env.variableSet.{variable_name}"
        self.suggestions = {OS.GENERIC: provision_command}
        self.variable_name = variable_name
        self.variable_value = variable_value

    def check(self) -> CheckResult:
        if self.variable_value:
            return self.verify(
                get_env_var_value(self.variable_name) == self.variable_value,
                f"{self.variable_name} has <not/> got the required value of f{self.variable_value}",
            )
        else:
            return self.verify(check_env_var_exists(self.variable_name), f"{self.variable_name} is <not/> set")


class YarnInstalled(Check):
    name = "yarn.installed"

    suggestions = {
        OS.OS_X: "<cmd>brew install yarn</cmd>",
        OS.GENERIC: "<cmd>npm install -g yarn</cmd>",
    }

    def check(self) -> CheckResult:
        return self.verify_install("yarn")


class ShfmtInstalled(Check):
    name = "shfmt.installed"

    suggestions = {
        OS.OS_X: "<cmd>brew install shfmt</cmd>",
        OS.UBUNTU: "<cmd>snap install shfmt</cmd>",
        OS.GENERIC: "Install shfmt: https://github.com/mvdan/sh",
    }

    def check(self) -> CheckResult:
        return self.verify_install("shfmt")


class HostAliasesConfigured(Check):
    name = "hostAliases.configured"

    def __init__(self, required_aliases: Dict[str, str]):
        self.required_aliases = required_aliases
        hosts_path = Hosts.determine_hosts_path()
        entries_text = tabulate([(addr, name) for (name, addr) in self.required_aliases.items()], tablefmt="plain")
        self.suggestions = {
            OS.GENERIC: f"""Add the following entries to {hosts_path}:

            {entries_text}"""
        }

    def check(self) -> CheckResult:
        hosts = Hosts()
        entries = [e for e in hosts.entries if e.entry_type in ("ipv4", "ipv6")]
        entries_dict = {}
        for entry in entries:
            for name in entry.names:
                entries_dict[name] = entry.address
        logging.debug(f"Hosts file entries: {entries_dict}")
        for (name, address) in self.required_aliases.items():
            if entries_dict.get(name) != address:
                return self.failed(f"{hosts.hosts_path} alias {name} -> {address} not present")

        return self.passed("{hosts.hosts_path} aliases present")
