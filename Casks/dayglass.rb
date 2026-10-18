cask "dayglass" do
  version "2.0.0"
  sha256 "0c2d815e3fbfabbf3e0f550a27687d027d8a414ba466aa84fa3d4086e233e03b"

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
