export type OrgContributor = {
  login: string;
  name: string | null;
  avatarUrl: string;
  profileUrl: string;
  contributions: number;
};

const GITHUB_ORG = "uplbtools";
const EXCLUDED_REPOS = new Set(["demo-repository"]);
const HIDDEN_LOGINS = new Set([
  "dependabot[bot]",
  "dependabot",
  "github-actions[bot]",
  "renovate[bot]",
  "semantic-release-bot",
  "cursoragent",
  "cursor-agent",
  "copilot-swe-agent[bot]",
  "github-copilot[bot]",
  "devin-ai-integration[bot]",
  "sweep-ai[bot]",
  "allcontributors[bot]",
]);

const HIDDEN_LOGIN_PATTERNS = [
  /\[bot\]$/i,
  /(?:^|[-_])bot$/i,
  /cursor/i,
  /copilot/i,
  /devin/i,
  /sweep/i,
  /renovate/i,
  /dependabot/i,
  /semantic-release/i,
  /allcontributors/i,
  /greenkeeper/i,
  /codecov/i,
];

type GithubRepo = {
  name: string;
  archived: boolean;
  fork: boolean;
};

type GithubApiContributor = {
  login: string;
  avatar_url: string;
  html_url: string;
  contributions: number;
  type: string;
};

type GithubUserProfile = {
  name?: string | null;
};

export function isVisibleGithubContributor(login: string): boolean {
  const key = login.toLowerCase();
  if (HIDDEN_LOGINS.has(key)) return false;
  return !HIDDEN_LOGIN_PATTERNS.some((pattern) => pattern.test(login));
}

export function formatGithubContributions(count: number): string {
  return count === 1 ? "1 commit" : `${count.toLocaleString()} commits`;
}

function githubHeaders(): HeadersInit {
  const headers: Record<string, string> = {
    Accept: "application/vnd.github+json",
    "User-Agent": "uplbtools.me",
  };
  const token =
    typeof process !== "undefined" ? process.env.GITHUB_TOKEN : undefined;
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

async function githubGet<T>(url: string): Promise<T | null> {
  const res = await fetch(url, { headers: githubHeaders() });
  if (!res.ok) return null;
  return (await res.json()) as T;
}

async function listOrgRepos(): Promise<string[]> {
  const repos: GithubRepo[] = [];
  let page = 1;

  while (page <= 5) {
    const batch = await githubGet<GithubRepo[]>(
      `https://api.github.com/orgs/${GITHUB_ORG}/repos?per_page=100&page=${page}&type=public`,
    );
    if (!batch?.length) break;
    repos.push(...batch);
    if (batch.length < 100) break;
    page += 1;
  }

  return repos
    .filter((repo) => !repo.archived && !repo.fork && !EXCLUDED_REPOS.has(repo.name))
    .map((repo) => repo.name);
}

async function listRepoContributors(
  repo: string,
): Promise<GithubApiContributor[]> {
  const contributors: GithubApiContributor[] = [];
  let page = 1;

  while (page <= 5) {
    const batch = await githubGet<GithubApiContributor[]>(
      `https://api.github.com/repos/${GITHUB_ORG}/${repo}/contributors?per_page=100&page=${page}&anon=false`,
    );
    if (!batch?.length) break;
    contributors.push(...batch);
    if (batch.length < 100) break;
    page += 1;
  }

  return contributors;
}

async function loadDisplayName(login: string): Promise<string | null> {
  const profile = await githubGet<GithubUserProfile>(
    `https://api.github.com/users/${login}`,
  );
  const name = profile?.name?.trim();
  return name || null;
}

export async function fetchOrgTopContributors(
  limit = 12,
): Promise<OrgContributor[]> {
  const repos = await listOrgRepos();
  const totals = new Map<
    string,
    Pick<OrgContributor, "login" | "avatarUrl" | "profileUrl" | "contributions">
  >();

  for (const repo of repos) {
    const rows = await listRepoContributors(repo);
    for (const row of rows) {
      if (row.type !== "User" || !isVisibleGithubContributor(row.login)) {
        continue;
      }

      const existing = totals.get(row.login);
      if (existing) {
        existing.contributions += row.contributions;
        continue;
      }

      totals.set(row.login, {
        login: row.login,
        avatarUrl: row.avatar_url,
        profileUrl: row.html_url,
        contributions: row.contributions,
      });
    }
  }

  const ranked = [...totals.values()].sort(
    (a, b) => b.contributions - a.contributions,
  );
  const top = ranked.slice(0, limit);

  const names = await Promise.all(
    top.map(async (person) => ({
      login: person.login,
      name: await loadDisplayName(person.login),
    })),
  );
  const nameByLogin = new Map(names.map((entry) => [entry.login, entry.name]));

  return top.map((person) => ({
    ...person,
    name: nameByLogin.get(person.login) ?? null,
  }));
}
