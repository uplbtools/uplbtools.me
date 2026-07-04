# uplbtools.me Agent Guide

**Human developers:** start with [README.md](README.md).

Org-wide agent defaults: see [room-tba/AGENTS.md](https://github.com/uplbtools/room-tba/blob/main/AGENTS.md). This file tailors that playbook to the **org landing site**.

## Doc map

| When | Read |
| --- | --- |
| Site structure | `src/pages/`, `src/components/` |
| Global styles | [src/styles/global.css](src/styles/global.css) |
| Messenger short links | [workers/messenger-redirect/](workers/messenger-redirect/) (Cloudflare Worker) |
| Design alignment with Room TBA | [uplbtools/uplbtools.me#1](https://github.com/uplbtools/uplbtools.me/issues/1) |

## Stack

- **Framework:** Astro 6 (static org landing)
- **Node:** ≥ 22.12
- **Package manager:** npm (`package-lock.json`)
- **Deploy:** Vercel (org hub at `uplbtools.me`)
- **Edge:** Cloudflare Workers in `workers/` for subdomain redirects (e.g. `messenger.uplbtools.me`)

## Branches and deploy

- **Default branch:** `main` → Vercel production on merge
- Feature work: branch → PR to `main`
- No `staging` branch today: use Vercel preview on the PR

Community URLs should match Room TBA constants where linked:

- Discord → `https://discord.uplbtools.me`
- Messenger contribute → `https://room-tba.uplbtools.me/messenger/contribute`
- Messenger maintainers → `https://room-tba.uplbtools.me/messenger/maintain`
- Room TBA → `https://room-tba.uplbtools.me`

## Verify before done

| Step | When |
| --- | --- |
| `npm run build` | Before commit/PR on substantive changes |
| `npm run dev` | UI/content changes: spot-check locally |
| 320px / 768px | Layout changes: no overflow; text wraps or truncates |
| Worker deploy | After editing `workers/*`: redeploy via Wrangler (see worker README) |

## UI guardrails

- Align visually with **Room TBA** warm maroon + light surfaces ([#1](https://github.com/uplbtools/uplbtools.me/issues/1)): not the current dark-zinc-only theme long term
- **No decorative animations**: functional transitions only
- Buttons and chips must stay inside containers at narrow widths

## Architecture (short)

```
src/
 components/ # Hero, Projects, Community, Footer, …
 layouts/ # Layout.astro
 pages/ # index.astro
 styles/ # global.css
workers/
 messenger-redirect/ # Cloudflare Worker for messenger.uplbtools.me
public/ # favicon, screenshots
```

## Commits

- Conventional Commits: `feat(hero): …`, `fix(worker): …`, `docs: …`
- Update README when changing scripts, deploy steps, or community URLs
