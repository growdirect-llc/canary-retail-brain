import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

const config: QuartzConfig = {
  configuration: {
    pageTitle: "Canary Retail Brain",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "en-US",
    baseUrl: "crb.growdirect.io",
    ignorePatterns: [
      ".obsidian",
      "ready-to-show-confirmation.md",
      "ACKNOWLEDGMENT.md",
      "CONTRIBUTING.md",
      "NOTICE.md",
      "SECURITY.md",
      "README.md",
    ],
    defaultDateType: "created",
    theme: {
      fontOrigin: "googleFonts",
      cdnCaching: true,
      typography: {
        header: "Source Serif 4",
        body: "Inter",
        code: "IBM Plex Mono",
      },
      colors: {
        lightMode: {
          light: "#F5F0E8",
          lightgray: "#EAE4D6",
          gray: "#6B6B6B",
          darkgray: "#3A3A3A",
          dark: "#1C3A2B",
          secondary: "#2A5240",
          tertiary: "#4CAF7D",
          highlight: "rgba(28,58,43,0.06)",
          textHighlight: "#BF870044",
        },
        darkMode: {
          light: "#0f1c10",
          lightgray: "#1C3A2B",
          gray: "#4CAF7D",
          darkgray: "#C8C0B0",
          dark: "#F5F0E8",
          secondary: "#4CAF7D",
          tertiary: "#BF8700",
          highlight: "rgba(76,175,125,0.12)",
          textHighlight: "#BF870055",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({
        priority: ["frontmatter", "filesystem"],
      }),
      Plugin.SyntaxHighlighting({
        theme: {
          light: "github-light",
          dark: "github-dark",
        },
        keepBackground: false,
      }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "shortest" }),
      Plugin.Description(),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage(),
      Plugin.TagPage(),
      Plugin.ContentIndex({
        enableSiteMap: true,
        enableRSS: true,
      }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.NotFoundPage(),
    ],
  },
}

export default config
