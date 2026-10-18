cask "dayglass" do
  version "2.0.0"
  sha256 "7d3befbe7cef9a0920cfea92e9c881b390a5be24d179dc8d6df7bd6540cd106e"

  url "https://github.com/IgorGanapolsky/dayglass-mac/releases/download/v#{version}/Dayglass.dmg"
  name "Dayglass"
  desc "100% On-Device Screen & Meeting Memory for macOS with 384K SubQ Snap GraphRAG & Paranoid Mode"
  homepage "https://igorganapolsky.github.io/dayglass-mac/"

  depends_on macos: ">= :ventura"

  app "Dayglass.app"

  postflight do
    system_command "/usr/bin/xattr",
                   args: ["-dr", "com.apple.quarantine", "#{appdir}/Dayglass.app"],
                   sudo: false
  end
end
