# Development

Install with `pip install -r requirements.txt`. The old `requirments.txt`
spelling remains as a compatibility shim.

Run offline tests with `python -m unittest discover -v`. Tests mock HTTP and
never use real FPL tokens. CI runs on Python 3.10 and 3.12.

The API layer makes read-only requests. Public endpoints get no private token;
only `my-team` receives `X-API-Authorization`. Redirects are rejected to avoid
sending credentials elsewhere. HTTP 429 is not retried automatically. Errors
do not echo response bodies or credential-bearing network details.

Current squad access still requires `FPL_AUTH_TOKEN` in an untracked `.env`.
No transfer, captaincy or account writes are implemented.
