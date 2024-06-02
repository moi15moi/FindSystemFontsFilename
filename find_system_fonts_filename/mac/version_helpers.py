from platform import mac_ver

__all__ = [
    "MacVersionHelpers"
]


class MacVersionHelpers:
    @staticmethod
    def is_mac_version_or_greater(minimum_major: int, minimum_minor: int) -> bool:
        """
        Parameters:
            major (int): The minimum major OS version number.
            minor (int): The minimum minor OS version number.
        Returns:
            True if the specified version matches or if it is greater than the version of the current Mac OS. Otherwise, False.
        """

        system_major, system_minor = mac_ver()[0].split(".")[:2]

        system_major = int(system_major)
        system_minor = int(system_minor)

        return system_major > minimum_major or (system_major == minimum_major and system_minor >= minimum_minor)
