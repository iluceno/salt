"""
    :codeauthor: Jayesh Kariya <jayeshk@saltstack.com>
"""
import sys

import pytest

import salt.modules.disk as disk
import salt.utils.path
import salt.utils.platform
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.mock import MagicMock, patch
from tests.support.unit import TestCase, skipIf

STUB_DISK_USAGE = {
    "/": {
        "filesystem": None,
        "1K-blocks": 10000,
        "used": 10000,
        "available": 10000,
        "capacity": 10000,
    },
    "/dev": {
        "filesystem": None,
        "1K-blocks": 10000,
        "used": 10000,
        "available": 10000,
        "capacity": 10000,
    },
    "/run": {
        "filesystem": None,
        "1K-blocks": 10000,
        "used": 10000,
        "available": 10000,
        "capacity": 10000,
    },
    "/run/lock": {
        "filesystem": None,
        "1K-blocks": 10000,
        "used": 10000,
        "available": 10000,
        "capacity": 10000,
    },
    "/run/shm": {
        "filesystem": None,
        "1K-blocks": 10000,
        "used": 10000,
        "available": 10000,
        "capacity": 10000,
    },
    "/run/user": {
        "filesystem": None,
        "1K-blocks": 10000,
        "used": 10000,
        "available": 10000,
        "capacity": 10000,
    },
    "/sys/fs/cgroup": {
        "filesystem": None,
        "1K-blocks": 10000,
        "used": 10000,
        "available": 10000,
        "capacity": 10000,
    },
}


STUB_DISK_INODEUSAGE = {
    "/": {
        "inodes": 10000,
        "used": 10000,
        "free": 10000,
        "use": 10000,
        "filesystem": None,
    },
    "/dev": {
        "inodes": 10000,
        "used": 10000,
        "free": 10000,
        "use": 10000,
        "filesystem": None,
    },
    "/run": {
        "inodes": 10000,
        "used": 10000,
        "free": 10000,
        "use": 10000,
        "filesystem": None,
    },
    "/run/lock": {
        "inodes": 10000,
        "used": 10000,
        "free": 10000,
        "use": 10000,
        "filesystem": None,
    },
    "/run/shm": {
        "inodes": 10000,
        "used": 10000,
        "free": 10000,
        "use": 10000,
        "filesystem": None,
    },
    "/run/user": {
        "inodes": 10000,
        "used": 10000,
        "free": 10000,
        "use": 10000,
        "filesystem": None,
    },
    "/sys/fs/cgroup": {
        "inodes": 10000,
        "used": 10000,
        "free": 10000,
        "use": 10000,
        "filesystem": None,
    },
}

STUB_DISK_PERCENT = {
    "/": 50,
    "/dev": 10,
    "/run": 10,
    "/run/lock": 10,
    "/run/shm": 10,
    "/run/user": 10,
    "/sys/fs/cgroup": 10,
}

STUB_DISK_BLKID = {"/dev/sda": {"TYPE": "ext4", "UUID": None}}


class DiskTestCase(TestCase, LoaderModuleMockMixin):
    """
    TestCase for salt.modules.disk module
    """

    def setup_loader_modules(self):
        return {disk: {}}

    def test_usage_dict(self):
        with patch.dict(disk.__grains__, {"kernel": "Linux"}), patch(
            "salt.modules.disk.usage", MagicMock(return_value=STUB_DISK_USAGE)
        ):
            mock_cmd = MagicMock(return_value=1)
            with patch.dict(disk.__salt__, {"cmd.run": mock_cmd}):
                self.assertDictEqual(STUB_DISK_USAGE, disk.usage(args=None))

    def test_usage_none(self):
        with patch.dict(disk.__grains__, {"kernel": "Linux"}), patch(
            "salt.modules.disk.usage", MagicMock(return_value="")
        ):
            mock_cmd = MagicMock(return_value=1)
            with patch.dict(disk.__salt__, {"cmd.run": mock_cmd}):
                self.assertEqual("", disk.usage(args=None))

    def test_inodeusage(self):
        with patch.dict(disk.__grains__, {"kernel": "OpenBSD"}), patch(
            "salt.modules.disk.inodeusage", MagicMock(return_value=STUB_DISK_INODEUSAGE)
        ):
            mock = MagicMock()
            with patch.dict(disk.__salt__, {"cmd.run": mock}):
                self.assertDictEqual(STUB_DISK_INODEUSAGE, disk.inodeusage(args=None))

    def test_percent(self):
        with patch.dict(disk.__grains__, {"kernel": "Linux"}), patch(
            "salt.modules.disk.percent", MagicMock(return_value=STUB_DISK_PERCENT)
        ):
            mock = MagicMock()
            with patch.dict(disk.__salt__, {"cmd.run": mock}):
                self.assertDictEqual(STUB_DISK_PERCENT, disk.percent(args=None))

    def test_percent_args(self):
        with patch.dict(disk.__grains__, {"kernel": "Linux"}), patch(
            "salt.modules.disk.percent", MagicMock(return_value="/")
        ):
            mock = MagicMock()
            with patch.dict(disk.__salt__, {"cmd.run": mock}):
                self.assertEqual("/", disk.percent("/"))

    def test_blkid(self):
        with patch.dict(
            disk.__salt__, {"cmd.run_stdout": MagicMock(return_value=1)}
        ), patch("salt.modules.disk.blkid", MagicMock(return_value=STUB_DISK_BLKID)):
            self.assertDictEqual(STUB_DISK_BLKID, disk.blkid())

    @skipIf(salt.utils.platform.is_windows(), "Skip on Windows")
    @skipIf(salt.utils.platform.is_darwin(), "Skip on Darwin")
    @skipIf(salt.utils.platform.is_freebsd(), "Skip on FreeBSD")
    def test_blkid_token(self):
        run_stdout_mock = MagicMock(return_value={"retcode": 1})
        with patch.dict(disk.__salt__, {"cmd.run_all": run_stdout_mock}):
            disk.blkid(token="TYPE=ext4")
            run_stdout_mock.assert_called_with(
                ["blkid", "-t", "TYPE=ext4"], python_shell=False
            )

    def test_dump(self):
        mock = MagicMock(return_value={"retcode": 0, "stdout": ""})
        with patch.dict(disk.__salt__, {"cmd.run_all": mock}):
            disk.dump("/dev/sda")
            mock.assert_called_once_with(
                "blockdev --getro --getsz --getss --getpbsz --getiomin "
                "--getioopt --getalignoff --getmaxsect --getsize "
                "--getsize64 --getra --getfra /dev/sda",
                python_shell=False,
            )

    def test_wipe(self):
        mock = MagicMock(return_value={"retcode": 0, "stdout": ""})
        with patch.dict(disk.__salt__, {"cmd.run_all": mock}):
            disk.wipe("/dev/sda")
            mock.assert_called_once_with("wipefs -a /dev/sda", python_shell=False)

    @pytest.mark.skipif(
        sys.version_info < (3, 6), reason="Py3.5 dictionaries are not ordered"
    )
    def test_tune(self):
        mock = MagicMock(
            return_value=(
                "712971264\n512\n512\n512\n0\n0\n88\n712971264\n365041287168\n512\n512"
            )
        )
        with patch.dict(disk.__salt__, {"cmd.run": mock}):
            mock_dump = MagicMock(return_value={"retcode": 0, "stdout": ""})
            with patch("salt.modules.disk.dump", mock_dump):
                kwargs = {"read-ahead": 512, "filesystem-read-ahead": 1024}
                disk.tune("/dev/sda", **kwargs)

                mock.assert_called_with(
                    "blockdev --setra 512 --setfra 1024 /dev/sda", python_shell=False
                )

    def test_format(self):
        """
        unit tests for disk.format
        """
        device = "/dev/sdX1"
        mock = MagicMock(return_value=0)
        with patch.dict(disk.__salt__, {"cmd.retcode": mock}), patch(
            "salt.utils.path.which", MagicMock(return_value=True)
        ):
            self.assertEqual(disk.format_(device), True)

    def test_fat_format(self):
        """
        unit tests for disk.format when using fat argument
        """
        device = "/dev/sdX1"
        expected = ["mkfs", "-t", "fat", "-F", 12, "/dev/sdX1"]
        mock = MagicMock(return_value=0)
        with patch.dict(disk.__salt__, {"cmd.retcode": mock}), patch(
            "salt.utils.path.which", MagicMock(return_value=True)
        ):
            self.assertEqual(disk.format_(device, fs_type="fat", fat=12), True)
            args, kwargs = mock.call_args_list[0]
            assert expected == args[0]

    @skipIf(
        not salt.utils.path.which("lsblk") and not salt.utils.path.which("df"),
        "lsblk or df not found",
    )
    def test_fstype(self):
        """
        unit tests for disk.fstype
        """
        device = "/dev/sdX1"
        fs_type = "ext4"
        mock = MagicMock(return_value="FSTYPE\n{}".format(fs_type))
        with patch.dict(disk.__grains__, {"kernel": "Linux"}), patch.dict(
            disk.__salt__, {"cmd.run": mock}
        ), patch("salt.utils.path.which", MagicMock(return_value=True)):
            self.assertEqual(disk.fstype(device), fs_type)

    def test_resize2fs(self):
        """
        unit tests for disk.resize2fs
        """
        device = "/dev/sdX1"
        mock = MagicMock()
        with patch.dict(disk.__salt__, {"cmd.run_all": mock}), patch(
            "salt.utils.path.which", MagicMock(return_value=True)
        ):
            disk.resize2fs(device)
            mock.assert_called_once_with(
                "resize2fs {}".format(device), python_shell=False
            )

    @skipIf(salt.utils.platform.is_windows(), "Skip on Windows")
    @skipIf(not salt.utils.path.which("mkfs"), "mkfs not found")
    def test_format_(self):
        """
        unit tests for disk.format_
        """
        device = "/dev/sdX1"
        mock = MagicMock(return_value=0)
        with patch.dict(disk.__salt__, {"cmd.retcode": mock}):
            disk.format_(device=device)
            mock.assert_any_call(["mkfs", "-t", "ext4", device], ignore_retcode=True)

    @skipIf(salt.utils.platform.is_windows(), "Skip on Windows")
    @skipIf(not salt.utils.path.which("mkfs"), "mkfs not found")
    def test_format__fat(self):
        """
        unit tests for disk.format_ with FAT parameter
        """
        device = "/dev/sdX1"
        mock = MagicMock(return_value=0)
        with patch.dict(disk.__salt__, {"cmd.retcode": mock}):
            disk.format_(device=device, fs_type="fat", fat=12)
            mock.assert_any_call(
                ["mkfs", "-t", "fat", "-F", 12, device], ignore_retcode=True
            )
