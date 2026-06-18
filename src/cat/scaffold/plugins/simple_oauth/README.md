# Simple OAuth

The **reference login flow** for the Cheshire Cat, and the template for any real
SSO integration.

Core only ever does one thing with identity: it trusts a JWT it signed (plus the
master `API_KEY` for headless access). It has no idea how a human logs in. This
plugin fills that gap:

- **`auth.py`** — `SimpleOAuth`, an `Auth` subclass. It inherits JWT/key
  *verification* for free from the core `Auth` base and adds the *login* half:
  `get_provider_login_url` + `authorize_user_from_oauth_code`.
- **`endpoints.py`** — the generic OAuth routes (`/auth/login/{name}`,
  `/auth/callback/{name}`, `/auth/logout`) that dispatch to any registered auth
  handler, plus a built-in **mock identity provider** (`/auth/internal-idp`) used
  by the `simple` handler for local development.
- **`idp.html`** — the mock login page.

## The flow

```
/auth/login/simple  →  mock IdP page  →  enter API_KEY  →
/auth/callback/simple  →  SimpleOAuth.authorize_user_from_oauth_code  →
core jwt.encode(user)  →  access_token cookie set  →  you are in
```

## Going to production

Fork this plugin into e.g. `google-oauth`: keep the route shape, replace the two
methods in `auth.py` with a real provider authorize URL and token exchange, and
drop the mock IdP. Core stays untouched — it just verifies the JWT you mint.

Auth is always on. Out of the box the master key is the dev value `meow`; set a
real `API_KEY` and `JWT_SECRET` in your project `config.py` before deploying.
