cask "dayglass" do
  version "2.4.0"
  sha256 "1e90b843bcd341374547494f1a099ee791dfb599d750e5e7a5668cdc099f4c51"

  url "https://github.com/IgorGanapolsky/dayglass-mac/releases/download/v#{version}/Dayglass.dmg"
  name "Dayglass"
  desc "On-device meeting memory with no meeting bot"
  homepage "https://www.dayglass.io/"

  depends_on macos: :ventura

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
