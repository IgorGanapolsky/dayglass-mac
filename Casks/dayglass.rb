cask "dayglass" do
  version "2.4.0"
  sha256 "1e90b843bcd341374547494f1a099ee791dfb599d750e5e7a5668cdc099f4c51"

  url "https://github.com/IgorGanapolsky/dayglass-mac/releases/download/v#{version}/Dayglass.dmg"
  name "Dayglass"
  desc "Meeting memory for macOS: local recording and storage, no meeting bot, and a cloud model only if you choose one"
  homepage "https://igorganapolsky.github.io/dayglass-mac/"

  depends_on macos: ">= :ventura"

  app "Dayglass.app"

  postflight do
    system_command "/usr/bin/xattr",
                   args: ["-dr", "com.apple.quarantine", "#{appdir}/Dayglass.app"],
                   sudo: false
  end
end
