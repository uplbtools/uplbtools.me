/** Keep in sync with room-tba `src/constants/community-links.ts` MESSENGER_*_TARGET. */
const REDIRECTS = {
  "/contribute": "https://m.me/j/Aba1V0prvQyLrafZ/",
  "/maintain": "https://m.me/j/AbZtqMU8UUTiwQfn/",
};

const DEFAULT = REDIRECTS["/contribute"];

export default {
  async fetch(request) {
    const path = new URL(request.url).pathname.replace(/\/$/, "") || "/";
    const target = REDIRECTS[path] ?? DEFAULT;
    return Response.redirect(target, 302);
  },
};
