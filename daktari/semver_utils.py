from semver import VersionInfo
from typing import Optional


def try_parse_semver(semver_str: Optional[str]) -> VersionInfo:
    try:
        return None if semver_str is None else VersionInfo.parse(semver_str)
    except ValueError:
        return None
