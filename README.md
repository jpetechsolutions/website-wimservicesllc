# wimservicesllc.com

Static site for **WIM Services, LLC** (Warren B. Merrill), Florida business brokerage.
Built and hosted the same way as the other JPE client sites: `src/` → `public/`, served by a
Cloudflare Worker with static assets, auto-deployed on push to `main`.

See `NOTES.md` for research sources and the open items to confirm with the client.

## Build

```bash
python3 src/build.py
```

All page copy lives in `src/build.py`. The build writes every page into `public/`, plus
`sitemap.xml`, `robots.txt`, `_headers`, `_redirects`, `favicon.svg` and `wrangler.jsonc`.
CSS and JS are fingerprinted (`?v=<hash>`) so visitors never get stale styles.

Commit both `src/` and `public/`.

## Local preview

```bash
python3 -m http.server 8099 --directory public
```

## Deploy

```bash
npm install
npx wrangler login          # once
npx wrangler deploy
```

Preview URL: `https://wim-services.<account>.workers.dev`

For Git-connected auto-deploy: Cloudflare dashboard → Workers & Pages → Create →
Import a repository → deploy command `npx wrangler deploy`.

## Structure

```
src/build.py          all page content + templates
public/css/site.css   design system (ink / brass / bone, Newsreader + Inter)
public/js/site.js     nav, scroll reveals, count-up, form validation
public/fonts/         self-hosted variable fonts — no Google Fonts requests
public/*.html         generated — do not edit by hand
```

## Pages

`/` · `/about` · `/selling-a-business` · `/buying-a-business` · `/industries` ·
`/listings` · `/contact` · `/privacy` · `/terms` · custom 404

## Before launch

Two values in the `SITE` dict at the top of `src/build.py` are intentionally empty:

- `web3forms_key` — create a Web3Forms key pointed at Warren's inbox and paste it here.
  Until then the contact form tells visitors to call or email instead of silently failing.
- `ga4_id` — GA4 measurement ID. No analytics tags load while this is empty, which is why
  the privacy policy currently states that the site uses no analytics. **Update the privacy
  policy when analytics or any ad pixel is added.**

Then work through the "Confirm with Warren" list in `NOTES.md` — in particular the office
address, the unverified BBF award, and the SBA pre-qualified claim.
