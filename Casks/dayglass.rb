cask "dayglass" do
  version "2.4.1"
  sha256 "f65644e1652f18884ce4708c03fe3a78b9fd031cdda42b7f456bfa939298e47a"

  url "https://github.com/IgorGanapolsky/dayglass-mac/releases/download/v#{version}/Dayglass.dmg"
  name "Dayglass"
  desc "On-device meeting memory with no meeting bot"
  homepage "https://www.dayglass.io/"

  depends_on arch: :arm64
  depends_on macos: :sonoma

  app "Dayglass.app"

  uninstall launchctl: "com.iganapolsky.dayglass-server",
            quit:      "com.iganapolsky.dayglass"

  zap trash: [
    "~/.dayglass",
    "~/Library/Application Support/Dayglass",
    "~/Library/LaunchAgents/com.iganapolsky.dayglass-server.plist",
    "~/Library/Preferences/com.iganapolsky.dayglass.plist",
  ]
end
