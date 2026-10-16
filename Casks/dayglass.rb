cask "dayglass" do
  version "2.0.0"
  sha256 "9b0c20192c0daca405994e531c0508c6d3de4b0fd43055b0dfc369f65a8b1424"

  url "https://github.com/IgorGanapolsky/dayglass-mac/releases/download/v#{version}/Dayglass.dmg"
  name "Dayglass"
  desc "100% On-Device Screen & Meeting Memory for macOS with 384K SubQ Snap Decision Engine"
  homepage "https://igorganapolsky.github.io/dayglass-mac/"

  depends_on macos: ">= :ventura"

  app "Dayglass.app"
end
