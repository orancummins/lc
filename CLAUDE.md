# Léann · LC study app

A single-file Python app (`app.py`, stdlib `http.server`) with study pages for each
Leaving Cert subject. All HTML/CSS/JS lives in the `INDEX_HTML` string in `app.py`;
subject content sits in the subject folders (`spanish/`, `biology/`, …).

- Add a topic: add an entry to that subject's `topics` in `SUBJECT_HOMES`, a
  `render…()` function, and a line in `renderContent()`.
- Run locally: `./run.sh` (port 2009). To test without touching the live server:
  `python -c "import app; app.PORT=2019; app.main()"`.
- Mobile first: the main user reads this on a phone, so check layouts at ~375px wide.

## Deploying

**Live site:** https://oran-dev.com/lc/ (served from a home Mac via nginx + Cloudflare Tunnel).

**To deploy, get the change onto `main` on GitHub (orancummins/lc).** The server
checks GitHub every minute and deploys new commits on `main` by itself
(`~/dev-server/dev-server-page/scripts/autodeploy.sh`, LaunchAgent
`com.orandev.lc-autodeploy`, log at `~/dev-server/logs/lc-autodeploy.log`).

- From a cloud or phone session: commit and push to `main`. If you can only push
  to your own branch, open a pull request; merging it deploys.
- On the server Mac itself: commit, then `git push origin main`. The auto-deployer
  restarts the app within about a minute (it tracks which commit is running), or run
  `~/dev-server/dev-server-page/scripts/deploy_app.sh lc --restart-only` to restart straight away.
- Check the live build: `curl https://oran-dev.com/lc/version`. The build ID is a
  hash of `app.py` and the verb data, so it changes when those change. Open tabs
  on phones reload themselves when it changes.

Keep `main` deployable: run `python3 -c "import ast; ast.parse(open('app.py').read())"`
before pushing.
