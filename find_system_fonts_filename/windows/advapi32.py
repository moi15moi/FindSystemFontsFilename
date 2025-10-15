from ctypes import WinDLL, wintypes
from enum import Enum
from ..exceptions import SystemApiError

__all__ = [
    "Advapi32",
    "RegistryDataType"
]

class RegistryDataType(Enum):
    REG_NONE = 0
    REG_SZ = 1
    REG_EXPAND_SZ = 2
    REG_BINARY = 3
    REG_DWORD = 4
    REG_DWORD_LITTLE_ENDIAN = 4
    REG_DWORD_BIG_ENDIAN = 5
    REG_LINK = 6
    REG_MULTI_SZ = 7
    REG_RESOURCE_LIST = 8
    REG_FULL_RESOURCE_DESCRIPTOR = 9
    REG_RESOURCE_REQUIREMENTS_LIST = 10
    REG_QWORD = 11
    REG_QWORD_LITTLE_ENDIAN = REG_QWORD


class Advapi32():
    def __init__(self) -> None:
        advapi32 = WinDLL("advapi32")

        self.HKEY_CURRENT_USER = wintypes.HKEY(0x80000001)
        self.KEY_SET_VALUE = 0x0002

        # https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeyexw
        self.RegOpenKeyExW = advapi32.RegOpenKeyExW
        self.RegOpenKeyExW.restype = wintypes.LONG
        self.RegOpenKeyExW.argtypes = [wintypes.HKEY, wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.PHKEY]
        self.RegOpenKeyExW.errcheck = self.errcheck_lstatus_fails

        # https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regsetvalueexw
        self.RegSetValueExW = advapi32.RegSetValueExW
        self.RegSetValueExW.restype = wintypes.LONG
        self.RegSetValueExW.argtypes = [wintypes.HKEY, wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPBYTE, wintypes.DWORD]
        self.RegSetValueExW.errcheck = self.errcheck_lstatus_fails

        # https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regdeletevaluew
        self.RegDeleteValueW = advapi32.RegDeleteValueW
        self.RegDeleteValueW.restype = wintypes.LONG
        self.RegDeleteValueW.argtypes = [wintypes.HKEY, wintypes.LPCWSTR]
        self.RegDeleteValueW.errcheck = self.errcheck_regdeletevaluew_fails

        # https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regclosekey
        self.RegCloseKey = advapi32.RegCloseKey
        self.RegCloseKey.restype = wintypes.LONG
        self.RegCloseKey.argtypes = [wintypes.HKEY]
        self.RegCloseKey.errcheck = self.errcheck_lstatus_fails

    @staticmethod
    def errcheck_lstatus_fails(result, func, args):
        ERROR_SUCCESS = 0
        if result != ERROR_SUCCESS:
            raise SystemApiError(f"{func.__name__} fails. The result is {result} which is invalid")
        return result

    @staticmethod
    def errcheck_regdeletevaluew_fails(result, func, args):
        ERROR_SUCCESS = 0
        ERROR_FILE_NOT_FOUND = 2
        if result not in (ERROR_SUCCESS, ERROR_FILE_NOT_FOUND):
            raise SystemApiError(f"{func.__name__} fails. The result is {result} which is invalid")
        return result
