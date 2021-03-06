import shutil
import struct
import uuid
from os import path

import hivex
from hivex.hive_types import *

LOCALE = r'en-US'

CONST_DESC = 'Description'
CONST_ELEMENTS = 'Elements'
CONST_ELEMENT = 'Element'

OBJECT_TYPE_APPLICATION = 0x1000_0000
OBJECT_TYPE_INHERIT = 0x2000_0000
OBJECT_TYPE_DEVICE = 0x3000_0000

OBJECT_APPLICATION_FIRMWARE = 0x0010_0000
OBJECT_APPLICATION_WIN_BOOT = 0x0020_0000
OBJECT_APPLICATION_LEGACY_LOADER = 0x0030_0000
OBJECT_APPLICATION_REAL_MODE = 0x0040_0000

OBJECT_INHERITABLE_BY_ANY = 0x0010_0000
OBJECT_INHERITABLE_BY_APPLICATION = 0x0020_0000
OBJECT_INHERITABLE_BY_DEVICE = 0x0030_0000


def create_object_type(object_type, object_type_flags, object_id, test=None):
    val = object_type + object_type_flags + object_id
    if test:
        assert val == test, f'create_object_type failed, was {val}, should be {test}'
    return val


ELEMENT_CLASS_LIBRARY = 0x1000_0000
ELEMENT_CLASS_APPLICATION = 0x2000_0000
ELEMENT_CLASS_DEVICE = 0x3000_0000
ELEMENT_CLASS_TEMPLATE = 0x4000_0000

ELEMENT_FORMAT_DEVICE = 0x0100_0000
ELEMENT_FORMAT_STRING = 0x0200_0000
ELEMENT_FORMAT_GUID = 0x0300_0000
ELEMENT_FORMAT_GUID_LIST = 0x0400_0000
ELEMENT_FORMAT_INTEGER = 0x0500_0000
ELEMENT_FORMAT_BOOLEAN = 0x0600_0000
ELEMENT_FORMAT_INTEGER_LIST = 0x0700_0000


def create_element_type(element_class, element_format, element_id, test=None):
    val = element_class + element_format + element_id
    val_str = hex(val)[2:].zfill(8)
    if test:
        assert val_str == test, f'create_element_type failed, was {val_str}, should be {test}'
    return val_str


# Global element types
BCDE_LIBRARY_TYPE_INHERIT = create_element_type(ELEMENT_CLASS_LIBRARY, ELEMENT_FORMAT_GUID_LIST, 0x6, '14000006')
BCDE_LIBRARY_TYPE_APPLICATION_DEVICE = create_element_type(ELEMENT_CLASS_LIBRARY, ELEMENT_FORMAT_DEVICE, 0x1,
                                                           '11000001')
BCDE_LIBRARY_TYPE_APPLICATION_PATH = create_element_type(ELEMENT_CLASS_LIBRARY, ELEMENT_FORMAT_STRING, 0x2, '12000002')
BCDE_LIBRARY_TYPE_DESCRIPTION = create_element_type(ELEMENT_CLASS_LIBRARY, ELEMENT_FORMAT_STRING, 0x4, '12000004')
BCDE_LIBRARY_TYPE_PREFERRED_LOCALE = create_element_type(ELEMENT_CLASS_LIBRARY, ELEMENT_FORMAT_STRING, 0x5, '12000005')

# EMS Settings
GUID_EMS_SETTINGS_GROUP = '{0ce4991b-e6b3-4b16-b23c-5e0d9250e5d9}'
OBJECT_TYPE_EMS_SETTINGS = create_object_type(OBJECT_TYPE_INHERIT, OBJECT_INHERITABLE_BY_ANY, 0x0, 0x20100000)
BCDE_LIBRARY_TYPE_EMS_ENABLED = create_element_type(ELEMENT_CLASS_LIBRARY, ELEMENT_FORMAT_BOOLEAN, 0x20, '16000020')

GUID_RESUME_LOADER_SETTINGS_GROUP = '{1afa9c49-16ab-4a5c-901b-212802da9460}'
OBJECT_TYPE_RESUME_LOADER_SETTINGS = create_object_type(OBJECT_TYPE_INHERIT, OBJECT_INHERITABLE_BY_APPLICATION, 0x4,
                                                        0x20200004)
# Debugger settings
GUID_DEBUGGER_SETTINGS_GROUP = '{4636856e-540f-4170-a130-a84776f4c654}'
OBJECT_TYPE_DEBUGGER_SETTINGS = create_object_type(OBJECT_TYPE_INHERIT, OBJECT_INHERITABLE_BY_ANY, 0x0, 0x20100000)
BCDE_LIBRARY_TYPE_DEBUGGER_TYPE = create_element_type(ELEMENT_CLASS_LIBRARY, ELEMENT_FORMAT_INTEGER, 0x11, '15000011')

# Bad memory settings
GUID_BAD_MEMORY_GROUP = '{5189b25c-5558-4bf2-bca4-289b11bd29e2}'
OBJECT_TYPE_BAD_MEMORY = create_object_type(OBJECT_TYPE_INHERIT, OBJECT_INHERITABLE_BY_ANY, 0x0, 0x20100000)

# Boot loader settings
GUID_BOOT_LOADER_SETTINGS_GROUP = '{6efb52bf-1766-41db-a6b3-0ee5eff72bd7}'
OBJECT_TYPE_BOOT_LOADER_SETTINGS = create_object_type(OBJECT_TYPE_INHERIT, OBJECT_INHERITABLE_BY_APPLICATION, 0x3,
                                                      0x20200003)

# Global settings
GUID_GLOBAL_SETTINGS_GROUP = '{7ea2e1ac-2e61-4728-aaa3-896d9d0a9f0e}'
OBJECT_TYPE_GLOBAL_SETTINGS = create_object_type(OBJECT_TYPE_INHERIT, OBJECT_INHERITABLE_BY_ANY, 0x0, 0x20100000)

# Hypervisor settings
GUID_HYPERVISOR_SETTINGS_GROUP = '{7ff607e0-4395-11db-b0de-0800200c9a66}'
OBJECT_TYPE_HYPERVISOR_SETTINGS = create_object_type(OBJECT_TYPE_INHERIT, OBJECT_INHERITABLE_BY_APPLICATION, 0x3,
                                                     0x20200003)
BCDE_OSLOADER_TYPE_HYPERVISOR_DEBUGGER_TYPE = create_element_type(ELEMENT_CLASS_APPLICATION, ELEMENT_FORMAT_INTEGER,
                                                                  0xf3, '250000f3')
BCDE_OSLOADER_TYPE_HYPERVISOR_DEBUGGER_PORT_NUMBER = create_element_type(ELEMENT_CLASS_APPLICATION,
                                                                         ELEMENT_FORMAT_INTEGER, 0xf4, '250000f4')
BCDE_OSLOADER_TYPE_HYPERVISOR_DEBUGGER_BAUDRATE = create_element_type(ELEMENT_CLASS_APPLICATION, ELEMENT_FORMAT_INTEGER,
                                                                      0xf5, '250000f5')

# Windows BootMgr Settings
GUID_WINDOWS_BOOTMGR = '{9dea862c-5cdd-4e70-acc1-f32b344d4795}'
OBJECT_TYPE_WINDOWS_BOOTMGR = create_object_type(OBJECT_TYPE_APPLICATION, OBJECT_APPLICATION_FIRMWARE, 0x2, 0x10100002)
BCDE_BOOTMGR_TYPE_DEFAULT_OBJECT = create_element_type(ELEMENT_CLASS_APPLICATION, ELEMENT_FORMAT_GUID, 0x3, '23000003')
BCDE_BOOTMGR_TYPE_RESUME_OBJECT = create_element_type(ELEMENT_CLASS_APPLICATION, ELEMENT_FORMAT_GUID, 0x6, '23000006')
BCDE_BOOTMGR_TYPE_DISPLAY_ORDER = create_element_type(ELEMENT_CLASS_APPLICATION, ELEMENT_FORMAT_GUID_LIST, 0x1,
                                                      '24000001')
BCDE_BOOTMGR_TYPE_TOOLS_DISPLAY_ORDER = create_element_type(ELEMENT_CLASS_APPLICATION, ELEMENT_FORMAT_GUID_LIST, 0x10,
                                                            '24000010')
BCDE_BOOTMGR_TYPE_TIMEOUT = create_element_type(ELEMENT_CLASS_APPLICATION, ELEMENT_FORMAT_INTEGER, 0x4, '25000004')

# Firmware BootMgr Settings
GUID_FIRMWARE_BOOTMGR = '{a5a30fa2-3d06-4e9f-b5f4-a01df9d1fcba}'
OBJECT_TYPE_FIRMWARE_BOOTMGR = create_object_type(OBJECT_TYPE_APPLICATION, OBJECT_APPLICATION_FIRMWARE, 0x1, 0x10100001)

# Windows MemTest
GUID_WINDOWS_MEMORY_TESTER = '{b2721d73-1db4-4c62-bf78-c548a880142d}'
OBJECT_TYPE_WINDOWS_MEMORY_TESTER = create_object_type(OBJECT_TYPE_APPLICATION, OBJECT_APPLICATION_WIN_BOOT, 0x5,
                                                       0x10200005)
BCDE_LIBRARY_TYPE_ALLOW_BAD_MEMORY_ACCESS = create_element_type(ELEMENT_CLASS_LIBRARY, ELEMENT_FORMAT_BOOLEAN, 0xb,
                                                                '1600000b')

# Windows resume
OBJECT_TYPE_WINDOWS_RESUME = create_object_type(OBJECT_TYPE_APPLICATION, OBJECT_APPLICATION_WIN_BOOT, 0x4, 0x10200004)
BCDE_LIBRARY_TYPE_ISOLATED_EXECUTION_CONTEXT = create_element_type(ELEMENT_CLASS_LIBRARY, ELEMENT_FORMAT_BOOLEAN, 0x60,
                                                                   '16000060')
BCDE_LIBRARY_TYPE_ALLOWED_IN_MEMORY_SETTINGS = create_element_type(ELEMENT_CLASS_LIBRARY, ELEMENT_FORMAT_INTEGER_LIST,
                                                                   0x77, '17000077')
BCDE_RESUME_LOADER_TYPE_HIBERFILE_PATH = create_element_type(ELEMENT_CLASS_APPLICATION, ELEMENT_FORMAT_STRING, 0x2,
                                                             '22000002')
BCDE_RESUME_LOADER_TYPE_BOOT_MENU_POLICY = create_element_type(ELEMENT_CLASS_APPLICATION, ELEMENT_FORMAT_INTEGER, 0x8,
                                                               '25000008')

# Windows loader
OBJECT_TYPE_WINDOWS_LOADER = create_object_type(OBJECT_TYPE_APPLICATION, OBJECT_APPLICATION_WIN_BOOT, 0x3, 0x10200003)
BCDE_OSLOADER_TYPE_OS_DEVICE = create_element_type(ELEMENT_CLASS_APPLICATION, ELEMENT_FORMAT_DEVICE, 0x1, '21000001')
BCDE_OSLOADER_TYPE_SYSTEM_ROOT = create_element_type(ELEMENT_CLASS_APPLICATION, ELEMENT_FORMAT_STRING, 0x2, '22000002')
BCDE_OSLOADER_TYPE_ASSOCIATED_RESUME_OBJECT = create_element_type(ELEMENT_CLASS_APPLICATION, ELEMENT_FORMAT_GUID, 0x3,
                                                                  '23000003')
BCDE_OSLOADER_TYPE_NX_POLICY = create_element_type(ELEMENT_CLASS_APPLICATION, ELEMENT_FORMAT_INTEGER, 0x20, '25000020')
BCDE_OSLOADER_TYPE_BOOT_MENU_POLICY = create_element_type(ELEMENT_CLASS_APPLICATION, ELEMENT_FORMAT_INTEGER, 0xc2,
                                                          '250000c2')


def format_uuid(uuid_val):
    string = str(uuid_val)
    return r'{' + string + r'}'


def pack_uint64(i):
    return struct.pack('<Q', i)


def uuid_to_device_id(uuid_val):
    # uuids are encoded with little endian for some parts
    return bytearray(uuid_val.bytes_le)


def create_device_value(disk_uuid, part_uuid):
    result = bytearray(0x58)
    # type is qualified partition
    result[0x10] = 0x06
    # unknown
    result[0x18] = 0x48
    # partition id
    result[0x20:0x20 + 16] = uuid_to_device_id(part_uuid)
    result[0x38:0x38 + 16] = uuid_to_device_id(disk_uuid)
    return bytes(result)


class BCD:
    def __init__(self, target_file, disk_uuid, efi_part_uuid, win_part_uuid):
        self.target_file = target_file
        self.disk_uuid = disk_uuid
        self.efi_part_uuid = efi_part_uuid
        self.win_part_uuid = win_part_uuid

        self.hive = hivex.Hivex(path.join(path.dirname(__file__), 'minimal'), write=True)
        self.root = self.hive.root()
        self.objects = None

        self.loader_uuid = uuid.uuid4()
        self.resume_uuid = uuid.uuid4()

    def create(self):
        self._create_description()
        self._create_objects()
        self._create_ems()
        self._create_resume_loader_settings()
        self._create_debugger_settings()
        self._create_bad_memory()
        self._create_boot_loader_settings()
        self._create_global_settings()
        self._create_hypervisor_settings()
        self._create_windows_bootmgr()
        self._create_firmware_bootmgr()
        self._create_windows_memory_tester()
        self._create_windows_resume()
        self._create_windows_loader()
        self.hive.commit(self.target_file)

    def _set_value(self, node, key, t, value):
        self.hive.node_set_value(node, {
            'key': key,
            't': t,
            'value': value
        })

    def _set_sz(self, node, key, string):
        self._set_value(node, key, REG_SZ, string.encode('utf-16-le') + b'\x00\x00')

    def _set_dword(self, node, key, dword):
        self._set_value(node, key, REG_DWORD, struct.pack('<I', dword))

    def _set_binary(self, node, key, binary):
        self._set_value(node, key, REG_BINARY, binary)

    def _set_multi_sz(self, node, key, strings):
        self._set_value(node, key, REG_MULTI_SZ,
                        b''.join(x.encode('utf-16-le') + b'\x00\x00' for x in strings) + b'\x00\x00')

    def _create_description(self):
        node = self.hive.node_add_child(self.root, CONST_DESC)
        self._set_sz(node, 'KeyName', 'BCD00000000')
        self._set_dword(node, 'System', 0x1)
        self._set_dword(node, 'TreatAsSystem', 0x1)

    def _create_objects(self):
        self.objects = self.hive.node_add_child(self.root, 'Objects')

    def _create_object(self, guid, type_dword, firmware_variable=None):
        node = self.hive.node_add_child(self.objects, guid)
        desc = self.hive.node_add_child(node, CONST_DESC)
        self._set_dword(desc, 'Type', type_dword)
        if firmware_variable:
            self._set_binary(desc, 'FirmwareVariable', firmware_variable)
        self.hive.node_add_child(node, CONST_ELEMENTS)
        return node

    def _create_element(self, obj_node, key, setter, value):
        elements = self.hive.node_get_child(obj_node, CONST_ELEMENTS)
        element = self.hive.node_add_child(elements, key)
        setter(element, CONST_ELEMENT, value)

    def _create_ems(self):
        obj_node = self._create_object(GUID_EMS_SETTINGS_GROUP, OBJECT_TYPE_EMS_SETTINGS)
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_EMS_ENABLED, self._set_binary, b'\x00')

    def _create_resume_loader_settings(self):
        obj_node = self._create_object(GUID_RESUME_LOADER_SETTINGS_GROUP, OBJECT_TYPE_RESUME_LOADER_SETTINGS)
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_INHERIT, self._set_multi_sz, [GUID_GLOBAL_SETTINGS_GROUP])

    def _create_debugger_settings(self):
        obj_node = self._create_object(GUID_DEBUGGER_SETTINGS_GROUP, OBJECT_TYPE_DEBUGGER_SETTINGS)
        # 4 means Local debugger type
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_DEBUGGER_TYPE, self._set_binary,
                             pack_uint64(0x4))

    def _create_bad_memory(self):
        # no elements
        self._create_object(GUID_BAD_MEMORY_GROUP, OBJECT_TYPE_BAD_MEMORY)

    def _create_boot_loader_settings(self):
        obj_node = self._create_object(GUID_BOOT_LOADER_SETTINGS_GROUP, OBJECT_TYPE_BOOT_LOADER_SETTINGS)
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_INHERIT, self._set_multi_sz, [
            GUID_GLOBAL_SETTINGS_GROUP,
            GUID_HYPERVISOR_SETTINGS_GROUP
        ])

    def _create_global_settings(self):
        obj_node = self._create_object(GUID_GLOBAL_SETTINGS_GROUP, OBJECT_TYPE_GLOBAL_SETTINGS)
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_INHERIT, self._set_multi_sz, [
            GUID_DEBUGGER_SETTINGS_GROUP,
            GUID_EMS_SETTINGS_GROUP,
            GUID_BAD_MEMORY_GROUP
        ])

    def _create_hypervisor_settings(self):
        obj_node = self._create_object(GUID_HYPERVISOR_SETTINGS_GROUP, OBJECT_TYPE_HYPERVISOR_SETTINGS)
        # 0 means Serial debugger
        self._create_element(obj_node, BCDE_OSLOADER_TYPE_HYPERVISOR_DEBUGGER_TYPE, self._set_binary, pack_uint64(0x0))
        self._create_element(obj_node, BCDE_OSLOADER_TYPE_HYPERVISOR_DEBUGGER_PORT_NUMBER, self._set_binary,
                             pack_uint64(0x1))
        self._create_element(obj_node, BCDE_OSLOADER_TYPE_HYPERVISOR_DEBUGGER_BAUDRATE, self._set_binary,
                             pack_uint64(115200))

    def _create_windows_bootmgr(self):
        obj_node = self._create_object(GUID_WINDOWS_BOOTMGR, OBJECT_TYPE_WINDOWS_BOOTMGR)
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_APPLICATION_DEVICE, self._set_binary,
                             create_device_value(self.disk_uuid, self.efi_part_uuid))
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_APPLICATION_PATH, self._set_sz,
                             r'\EFI\Microsoft\Boot\bootmgfw.efi')
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_DESCRIPTION, self._set_sz, r'Windows Boot Manager')
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_PREFERRED_LOCALE, self._set_sz, LOCALE)
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_INHERIT, self._set_multi_sz, [
            GUID_GLOBAL_SETTINGS_GROUP
        ])
        self._create_element(obj_node, BCDE_BOOTMGR_TYPE_DEFAULT_OBJECT, self._set_sz, format_uuid(self.loader_uuid))
        self._create_element(obj_node, BCDE_BOOTMGR_TYPE_RESUME_OBJECT, self._set_sz, format_uuid(self.resume_uuid))
        self._create_element(obj_node, BCDE_BOOTMGR_TYPE_DISPLAY_ORDER, self._set_multi_sz, [
            format_uuid(self.loader_uuid)
        ])
        self._create_element(obj_node, BCDE_BOOTMGR_TYPE_TOOLS_DISPLAY_ORDER, self._set_multi_sz, [
            GUID_WINDOWS_MEMORY_TESTER
        ])
        # 30 seconds timeout
        self._create_element(obj_node, BCDE_BOOTMGR_TYPE_TIMEOUT, self._set_binary, pack_uint64(30))

    def _create_firmware_bootmgr(self):
        obj_node = self._create_object(GUID_FIRMWARE_BOOTMGR, OBJECT_TYPE_FIRMWARE_BOOTMGR)
        self._create_element(obj_node, BCDE_BOOTMGR_TYPE_DISPLAY_ORDER, self._set_multi_sz, [
            GUID_WINDOWS_BOOTMGR
        ])
        self._create_element(obj_node, BCDE_BOOTMGR_TYPE_TIMEOUT, self._set_binary, pack_uint64(0))

    def _create_windows_memory_tester(self):
        obj_node = self._create_object(GUID_WINDOWS_MEMORY_TESTER, OBJECT_TYPE_WINDOWS_MEMORY_TESTER)
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_APPLICATION_DEVICE, self._set_binary,
                             create_device_value(self.disk_uuid, self.efi_part_uuid))
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_APPLICATION_PATH, self._set_sz,
                             r'\EFI\Microsoft\Boot\memtest.efi')
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_DESCRIPTION, self._set_sz, r'Windows Memory Diagnostic')
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_PREFERRED_LOCALE, self._set_sz, LOCALE)
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_INHERIT, self._set_multi_sz, [
            GUID_GLOBAL_SETTINGS_GROUP
        ])
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_ALLOW_BAD_MEMORY_ACCESS, self._set_binary, b'\x01')

    def _create_windows_resume(self):
        obj_node = self._create_object(format_uuid(self.resume_uuid), OBJECT_TYPE_WINDOWS_RESUME)
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_APPLICATION_DEVICE, self._set_binary,
                             create_device_value(self.disk_uuid, self.win_part_uuid))
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_APPLICATION_PATH, self._set_sz,
                             r'\windows\system32\winresume.efi')
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_DESCRIPTION, self._set_sz, r'Windows Resume Application')
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_PREFERRED_LOCALE, self._set_sz, LOCALE)
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_INHERIT, self._set_multi_sz, [
            GUID_RESUME_LOADER_SETTINGS_GROUP
        ])
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_ISOLATED_EXECUTION_CONTEXT, self._set_binary, b'\x01')
        # 0x15000075 is ???
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_ALLOWED_IN_MEMORY_SETTINGS, self._set_binary,
                             pack_uint64(0x15000075))
        self._create_element(obj_node, BCDE_RESUME_LOADER_TYPE_HIBERFILE_PATH, self._set_sz, r'\hiberfil.sys')
        # 1 is the standard boot menu policy
        self._create_element(obj_node, BCDE_RESUME_LOADER_TYPE_BOOT_MENU_POLICY, self._set_binary, pack_uint64(0x1))

    def _create_windows_loader(self):
        obj_node = self._create_object(format_uuid(self.loader_uuid), OBJECT_TYPE_WINDOWS_RESUME)
        device = create_device_value(self.disk_uuid, self.win_part_uuid)
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_APPLICATION_DEVICE, self._set_binary,
                             device)
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_APPLICATION_PATH, self._set_sz,
                             r'\windows\system32\winload.efi')
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_DESCRIPTION, self._set_sz, r'Windows 10')
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_PREFERRED_LOCALE, self._set_sz, LOCALE)
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_INHERIT, self._set_multi_sz, [
            GUID_BOOT_LOADER_SETTINGS_GROUP
        ])
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_ISOLATED_EXECUTION_CONTEXT, self._set_binary, b'\x01')
        # 0x15000075 is ???
        self._create_element(obj_node, BCDE_LIBRARY_TYPE_ALLOWED_IN_MEMORY_SETTINGS, self._set_binary,
                             pack_uint64(0x15000075))
        self._create_element(obj_node, BCDE_OSLOADER_TYPE_OS_DEVICE, self._set_binary, device)
        self._create_element(obj_node, BCDE_OSLOADER_TYPE_SYSTEM_ROOT, self._set_sz, r'\windows')
        self._create_element(obj_node, BCDE_OSLOADER_TYPE_ASSOCIATED_RESUME_OBJECT, self._set_sz,
                             format_uuid(self.resume_uuid))
        # 0 is opt in
        self._create_element(obj_node, BCDE_OSLOADER_TYPE_NX_POLICY, self._set_binary, pack_uint64(0))
        # 1 is standard
        self._create_element(obj_node, BCDE_OSLOADER_TYPE_BOOT_MENU_POLICY, self._set_binary, pack_uint64(0x1))


def main():
    shutil.copy('minimal', 'target')
    # disk_uuid = uuid.UUID('533fc85c-e6b6-4bd4-b5cd-4badc4b98d06')
    disk_uuid = uuid.UUID('f470029f-14da-41dc-a2ac-f14b055d4a92')
    # efi_part_uuid = uuid.UUID('8cd00792-e072-44aa-babe-ec71c6e27205')
    efi_part_uuid = uuid.UUID('e9cc797b-4481-4f8d-910c-a7295adc39f1')
    # win_part_uuid = uuid.UUID('d218db09-4505-4f72-b670-0683ee7d8036')
    win_part_uuid = uuid.UUID('45847f60-f197-48fd-893c-060eb28b4202')
    bcd = BCD('target', disk_uuid, efi_part_uuid, win_part_uuid)
    bcd.create()


if __name__ == '__main__':
    main()
