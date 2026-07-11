export type ToolStatus = "active" | "live";

export type ToolEntry = {
  id: string;
  name: string;
  description: string;
  href: string;
  githubHref?: string;
  actionLabel: string;
  status: ToolStatus;
  statusLabel: string;
  platform: string;
  tags: string[];
  screenshot: string;
  screenshotAlt: string;
};

export const tools: ToolEntry[] = [
  {
    id: "room-tba",
    name: "Room TBA",
    description:
      "Look up room schedules, navigate between class buildings, and view jeepney routes around the UPLB campus.",
    href: "https://room-tba.uplbtools.me",
    githubHref: "https://github.com/uplbtools/room-tba",
    actionLabel: "Launch app",
    status: "active",
    statusLabel: "Active",
    platform: "Astro / MapLibre",
    tags: ["Map", "Open source"],
    screenshot: "/room-tba-screenshot.png",
    screenshotAlt: "Room TBA campus map and room search",
  },
  {
    id: "gradesim",
    name: "Elbi GradeSim",
    description:
      "GWA simulation browser extension that overlays on the UPLB AMIS grades portal to model target graduation honor requirements.",
    href: "https://gradesim.uplbtools.me",
    githubHref: "https://github.com/uplbtools/gradesim",
    actionLabel: "Install extension",
    status: "active",
    statusLabel: "Active",
    platform: "Browser extension",
    tags: ["Extension", "Open source"],
    screenshot: "/gradesim-screenshot.png",
    screenshotAlt: "Elbi GradeSim AMIS extension",
  },
];
