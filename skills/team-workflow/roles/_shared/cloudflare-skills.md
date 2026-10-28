## Cloudflare skills

When the project runs on Cloudflare (`wrangler.toml`, `wrangler.json` or `wrangler.jsonc`,
Workers, Pages, Zero Trust) and the Cloudflare skills are available (`tw.py addons add
cloudflare`), use them: `workers-best-practices` for Workers code and configuration,
`cloudflare-one` for Zero Trust and SASE (access policies, gateway, tunnels), `turnstile-spin`
for bot verification with server-side Siteverify, `wrangler` for commands, `cloudflare` to
choose products. Check secrets in `wrangler` files and bindings, and that every Turnstile token
is verified on the server.
