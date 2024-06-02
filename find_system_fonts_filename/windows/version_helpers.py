__all__ = [
    "WindowsVersionHelpers"
]

class WindowsVersionHelpers:
    @staticmethod
    def is_windows_version_or_greater(windows_version, major: int, minor: int, build: int) -> bool:
        """
        Parameters:
            windows_version: An object from getwindowsversion.
            major (int): The minimum major OS version number.
            minor (int): The minimum minor OS version number.
            build (int): The minimum build version number.
        Returns:
            True if the specified version matches or if it is greater than the version of the current Windows OS. Otherwise, False.
        """

        if windows_version.major > major:
            return True
        elif windows_version.major == major and windows_version.minor > minor:
            return True
        else:
            return (
                windows_version.major == major
                and windows_version.minor == minor
                and windows_version.build >= build
            )

    @staticmethod
    def is_windows_vista_sp2_or_greater(windows_version) -> bool:
        # From https://www.lifewire.com/windows-version-numbers-2625171
        return WindowsVersionHelpers.is_windows_version_or_greater(windows_version, 6, 0, 6002)

    @staticmethod
    def is_windows_10_or_greater(windows_version) -> bool:
        # From https://www.lifewire.com/windows-version-numbers-2625171
        return WindowsVersionHelpers.is_windows_version_or_greater(windows_version, 10, 0, 10240)
