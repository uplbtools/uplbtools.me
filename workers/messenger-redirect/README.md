# messenger.uplbtools.me redirects

Cloudflare Worker for role-specific Messenger group chat short links.

| Path | Target |
| ---- | ------ |
| `/contribute` | Contributors GC |
| `/maintain` | Maintainers GC |
| `/` (default) | Contributors GC |

Canonical URLs are referenced from [room-tba `community-links.ts`](https://github.com/uplbtools/room-tba/blob/staging/src/constants/community-links.ts).

## Deploy

```sh
cd workers/messenger-redirect
wrangler deploy
```

Requires Cloudflare account access to the `uplbtools.me` zone.
