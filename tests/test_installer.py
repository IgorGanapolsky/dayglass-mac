"""install.sh contacts only the GitHub release downloads unless the person installing opts in to the install ping."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CURL = r"""#!/bin/bash
echo "$@" >> "$STUB_LOG"
out=""; url=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    -o) out="$2"; shift 2 ;;
    http*) url="$1"; shift ;;
    *) shift ;;
  esac
done
if [[ "$url" == *SHA256SUMS ]]; then
  echo "$(shasum -a 256 "$STUB_DMG" | awk '{print $1}')  Dayglass.dmg"
elif [[ -n "$out" ]]; then
  cp "$STUB_DMG" "$out"
fi
"""

HDIUTIL = r"""#!/bin/bash
if [[ "$1" == attach ]]; then
  while [[ $# -gt 0 ]]; do [[ "$1" == -mountpoint ]] && mkdir -p "$2/Dayglass.app/Contents" && break; shift; done
fi
exit 0
"""


class Installer(unittest.TestCase):
    def _run(self, **env):
        tmp = Path(tempfile.mkdtemp())
        bin_dir = tmp / "bin"
        bin_dir.mkdir()
        for name, body in {"curl": CURL, "hdiutil": HDIUTIL, "codesign": "#!/bin/bash\nexit 0\n", "spctl": "#!/bin/bash\nexit 0\n"}.items():
            stub = bin_dir / name
            stub.write_text(body)
            stub.chmod(0o755)
        dmg = tmp / "fake.dmg"
        dmg.write_bytes(b"not a real dmg")
        log = tmp / "curl.log"
        full_env = {k: v for k, v in os.environ.items() if k != "DAYGLASS_INSTALL_PING"}
        full_env.update({
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "STUB_LOG": str(log),
            "STUB_DMG": str(dmg),
            "DAYGLASS_INSTALL_APP_DIR": str(tmp / "Applications" / "Dayglass.app"),
            "DAYGLASS_NO_OPEN": "1",
            **env,
        })
        (tmp / "Applications").mkdir()
        proc = subprocess.run(["bash", str(ROOT / "install.sh")], env=full_env, capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return log.read_text().splitlines()

    def test_default_install_contacts_only_github(self):
        calls = self._run()
        self.assertEqual(len(calls), 2, calls)
        for call in calls:
            self.assertIn("https://github.com/IgorGanapolsky/dayglass-mac/releases/latest/download/", call)
        self.assertFalse(any("posthog" in c for c in calls))

    def test_install_ping_only_when_opted_in(self):
        calls = self._run(DAYGLASS_INSTALL_PING="1")
        self.assertEqual(sum("https://us.i.posthog.com/capture/" in c for c in calls), 1, calls)

    def test_no_quarantine_strip(self):
        self.assertNotIn("xattr", (ROOT / "install.sh").read_text())


if __name__ == "__main__":
    unittest.main()
