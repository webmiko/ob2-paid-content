const PROVIDER_LABELS: Record<string, string> = {
  youtube: "YouTube",
  vimeo: "Vimeo",
  rutube: "Rutube",
  vk: "VK Video",
  dzen: "Дзен",
};

export function videoProviderLabel(provider: string | null | undefined): string | null {
  if (!provider) {
    return null;
  }
  return PROVIDER_LABELS[provider] ?? provider;
}

export const VIDEO_URL_PLACEHOLDER =
  "YouTube, Vimeo, Rutube, VK Video или Дзен (https://…)";
