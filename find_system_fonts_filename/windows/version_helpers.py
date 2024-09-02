from ctypes import byref, sizeof
from win32more.Windows.Win32.System.SystemInformation import (
    OSVERSIONINFOEXW,
    VER_BUILDNUMBER,
    VER_MAJORVERSION,
    VER_MINORVERSION,
    VER_SERVICEPACKMAJOR,
    VerSetConditionMask,
    VerifyVersionInfoW,
    _WIN32_WINNT_VISTA,
    _WIN32_WINNT_WIN10,
)
from win32more.Windows.Win32.System.SystemServices import VER_GREATER_EQUAL

__all__ = ["WindowsVersionHelpers"]


class WindowsVersionHelpers:
    @staticmethod
    def is_windows_version_or_greater_service(major_version: int, minor_version: int, service_pack_major: int) -> bool:
        """
        Parameters:
            windows_version: An object from getwindowsversion.
            major_version (int): The minimum major OS version number.
            minor_version (int): The minimum minor OS version number.
            service_pack_major (int): The minimum service pack number.
        Returns:
            True if the specified version matches or if it is greater than the version of the current Windows OS. Otherwise, False.
        """

        osvi = OSVERSIONINFOEXW(sizeof(OSVERSIONINFOEXW), 0, 0, 0, 0, "", 0, 0)
        dwlConditionMask = VerSetConditionMask(
                VerSetConditionMask(
                    VerSetConditionMask(0, VER_MAJORVERSION, VER_GREATER_EQUAL),
                    VER_MINORVERSION, VER_GREATER_EQUAL
                ),
                VER_SERVICEPACKMAJOR, VER_GREATER_EQUAL
            )

        osvi.dwMajorVersion = major_version
        osvi.dwMinorVersion = minor_version
        osvi.wServicePackMajor = service_pack_major

        return bool(VerifyVersionInfoW(byref(osvi), VER_MAJORVERSION | VER_MINORVERSION | VER_SERVICEPACKMAJOR, dwlConditionMask))

    @staticmethod
    def is_windows_version_or_greater_build(major_version: int, minor_version: int, build: int) -> bool:
        """
        Parameters:
            windows_version: An object from getwindowsversion.
            major_version (int): The minimum major OS version number.
            minor_version (int): The minimum minor OS version number.
            build (int): The minimum build version number.
        Returns:
            True if the specified version matches or if it is greater than the version of the current Windows OS. Otherwise, False.
        """

        osvi = OSVERSIONINFOEXW(sizeof(OSVERSIONINFOEXW), 0, 0, 0, 0, "", 0, 0)
        dwlConditionMask = VerSetConditionMask(
                VerSetConditionMask(
                    VerSetConditionMask(0, VER_MAJORVERSION, VER_GREATER_EQUAL),
                    VER_MINORVERSION, VER_GREATER_EQUAL
                ),
                VER_BUILDNUMBER, VER_GREATER_EQUAL
            )

        osvi.dwMajorVersion = major_version
        osvi.dwMinorVersion = minor_version
        osvi.dwBuildNumber = build

        return bool(VerifyVersionInfoW(byref(osvi), VER_MAJORVERSION | VER_MINORVERSION | VER_BUILDNUMBER, dwlConditionMask))

    @staticmethod
    def is_windows_vista_sp2_or_greater() -> bool:  
        HIBYTE = (_WIN32_WINNT_VISTA >> 8) & 0xff 
        LOBYTE = _WIN32_WINNT_VISTA & 0xff 
        return WindowsVersionHelpers.is_windows_version_or_greater_service(HIBYTE, LOBYTE, 2)


    @staticmethod
    def is_windows_10_or_greater() -> bool:
        HIBYTE = (_WIN32_WINNT_WIN10 >> 8) & 0xff 
        LOBYTE = _WIN32_WINNT_WIN10 & 0xff 
        return WindowsVersionHelpers.is_windows_version_or_greater_service(HIBYTE, LOBYTE, 0)
