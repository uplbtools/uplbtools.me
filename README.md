# uplbtools.me

Org landing site for [UPLB Tools](https://uplbtools.me): open-source utilities for the UP Los Baños community.

## Stack

- Astro 6 (static)
- Node ≥ 22.12
- npm (`package-lock.json`)
- Vercel for `uplbtools.me`
- Cloudflare Workers in `workers/` for subdomain redirects (for example `messenger.uplbtools.me`)

## Develop

```sh
npm install
npm run dev
```

| Command | Action |
| --- | --- |
| `npm run dev` | Local server |
| `npm run build` | Production build to `./dist/` |
| `npm run preview` | Preview the build |
| `npm run generate:og` | Regenerate Open Graph images |

## Deploy

- Default branch: `main` → Vercel production
- Feature work: branch → PR to `main`
- After editing `workers/*`, redeploy the Worker with Wrangler (see the worker README)

## Related

- [Room TBA](https://room-tba.uplbtools.me)
- [GradeSim](https://gradesim.uplbtools.me) (extension landing)
- Org agent defaults: [room-tba/AGENTS.md](https://github.com/uplbtools/room-tba/blob/main/AGENTS.md)
- This repo: [AGENTS.md](AGENTS.md)

## License

See [LICENSE](LICENSE).
