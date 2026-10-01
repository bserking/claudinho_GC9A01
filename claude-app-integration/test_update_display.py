import hashlib
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import update_display as updater


class UpdateDisplayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.firmware = Path(self.temp.name) / "claudinho-esp32c3-1.8.3-gc9a01.4-ota.bin"
        self.binary = b"test-firmware-bytes"
        self.firmware.write_bytes(self.binary)
        self.manifest = self.firmware.with_name("SHA256SUMS-GC9A01.txt")
        self.manifest.write_text(hashlib.sha256(self.binary).hexdigest() + "  " + self.firmware.name + "\n")
        self.device = Mock()
        self.addCleanup(patch.stopall)
        patch("update_display.time.sleep", return_value=None).start()
        patch("update_display.time.monotonic", side_effect=itertools.count()).start()
        patch("update_display.print").start()

    @staticmethod
    def status(version="1.8.3-gc9a01.3", approval="pedida", board="esp32c3"):
        return json.dumps({"placa": board, "display": "gc9a01-240x240",
                           "versao": version, "manut": approval})

    def test_default_check_only_reads_the_device(self):
        self.device.request.return_value = self.status()
        updater.update_display(self.device, self.firmware)
        self.device.request.assert_called_once_with("/mini.json", timeout=10)

    def test_wrong_board_blocks_approval_and_upload(self):
        self.device.request.return_value = self.status(board="esp32s3")
        with self.assertRaisesRegex(updater.UpdateError, "kein unterstütztes"):
            updater.update_display(self.device, self.firmware, apply=True)
        self.assertEqual([call.args[0] for call in self.device.request.call_args_list], ["/mini.json"])

    def test_hash_mismatch_blocks_all_network_requests(self):
        self.firmware.write_bytes(b"changed")
        with self.assertRaisesRegex(updater.UpdateError, "Prüfsumme"):
            updater.update_display(self.device, self.firmware, apply=True)
        self.device.request.assert_not_called()

    def test_complete_flash_image_is_rejected(self):
        complete = self.firmware.with_name(self.firmware.name.replace("-ota.bin", "-completo.bin"))
        with self.assertRaisesRegex(updater.UpdateError, "kein Komplettimage"):
            updater.update_display(self.device, complete, apply=True)
        self.device.request.assert_not_called()

    def test_expired_boot_approval_never_uploads(self):
        self.device.request.side_effect = lambda endpoint, *args, **kwargs: (
            "ok\n" if endpoint == "/cmd" else self.status())
        with self.assertRaisesRegex(updater.UpdateError, "Keine rechtzeitige BOOT-Freigabe"):
            updater.update_display(self.device, self.firmware, apply=True)
        self.assertNotIn("/ota", [call.args[0] for call in self.device.request.call_args_list])

    def test_success_accepts_legacy_ack_and_verifies_reboot_version(self):
        self.device.request.side_effect = [self.status(), "ok\n", self.status(approval="liberada"),
                                           "ok, reiniciando\n", self.status(version="1.8.3-gc9a01.4")]
        updater.update_display(self.device, self.firmware, apply=True)
        uploads = [call for call in self.device.request.call_args_list if call.args[0] == "/ota"]
        self.assertEqual(len(uploads), 1)
        self.assertEqual(uploads[0].kwargs["timeout"], 180)
        self.assertIn(b'name="f"', uploads[0].kwargs["raw_data"])
        self.assertIn(self.binary, uploads[0].kwargs["raw_data"])
        self.assertTrue(uploads[0].kwargs["content_type"].startswith("multipart/form-data; boundary="))

    def test_acknowledged_upload_still_requires_new_version(self):
        self.device.request.side_effect = lambda endpoint, *args, **kwargs: (
            "ok\n" if endpoint == "/cmd" else "ok, restarting\n" if endpoint == "/ota"
            else self.status(approval="liberada"))
        with self.assertRaisesRegex(updater.UpdateError, "neue Version aber noch nicht nachweisbar"):
            updater.update_display(self.device, self.firmware, apply=True)
        self.assertEqual(sum(call.args[0] == "/ota" for call in self.device.request.call_args_list), 1)

    def test_ambiguous_upload_error_is_not_retried_or_exposed(self):
        self.device.request.side_effect = [self.status(), "ok\n", self.status(approval="liberada"),
                                           OSError("token=private-secret ip=192.168.1.83")]
        with self.assertRaisesRegex(updater.UpdateError, "Nicht blind wiederholen") as failure:
            updater.update_display(self.device, self.firmware, apply=True)
        self.assertNotIn("private-secret", str(failure.exception))
        self.assertNotIn("192.168.1.83", str(failure.exception))
        self.assertEqual(sum(call.args[0] == "/ota" for call in self.device.request.call_args_list), 1)


if __name__ == "__main__":
    unittest.main()
