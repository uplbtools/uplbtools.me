export const SITE_ORIGIN = "https://uplbtools.me";
export const SITE_NAME = "uplb.tools";

export const DEFAULT_TITLE = "uplb.tools";
export const DEFAULT_DESCRIPTION =
  "Room TBA, Elbi GradeSim, and other open-source tools for UP Los Baños. Built by UPLB students on GitHub; not an official university site.";

export const DEFAULT_OG_IMAGE = "/og.png";
export const DEFAULT_OG_IMAGE_ALT =
  "uplb.tools: Room TBA and Elbi GradeSim for UP Los Baños";
export const OG_IMAGE_WIDTH = 1200;
export const OG_IMAGE_HEIGHT = 630;

export function absoluteUrl(path: string, origin = SITE_ORIGIN): string {
  return new URL(path, origin).href;
}
