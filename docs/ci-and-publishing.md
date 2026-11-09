# Checks, publishing and translation returns

Text changes and returned translations go through pull requests on GitHub; nobody needs
a local copy of the code for them. A local copy is still needed to add images
(`scripts/prepare_assets.py` uses full-resolution originals that are not in Git), add
manuals or pages, or review callout positions.

All three workflows call `scripts/ci.py`, which also runs locally with the same results.

## Manual checks (`.github/workflows/ci.yml`)

Runs on every pull request and push to `main`.

1. `python scripts/ci.py plan --changed <file list>` works out what a change affects. It
   records each model's build to learn exactly which Markdown files the model uses, so an
   edit to `content/en/shared/sff/storage.md` builds S630 and S640 only, and an edit to
   `content/en/shared/warranty.md` builds every manual. Scripts, templates, the glossary and
   shared product or illustration data rebuild everything. Documentation-only changes build
   nothing.
2. `python scripts/ci.py check --plan plan.json` builds those manuals in English with all
   their checks, rebuilds affected manuals in each language that has a translation memory,
   and validates translation packages and their editors when tooling or a package changes.
3. The run's **Summary** lists every result. The **artifact** holds the PDFs, page
   overviews and validation reports, so reviewers can read the changed manuals.

An English failure fails the check. A translation that becomes incomplete because English
changed is a warning (⚠️), with the missing texts listed in the log, unless the pull
request changes that language's `translations/` folder.

To edit text in the browser: open the Markdown file on GitHub, click the pencil, commit to
a new branch and open a pull request. The check attaches the rebuilt PDFs.

## Site (`.github/workflows/pages.yml`)

After *Manual checks* passes for a push to `main`, the publish workflow builds exactly
that commit and deploys it, so a commit that fails its checks never reaches the site; the
site keeps the last good version. If a newer commit has reached `main` in the meantime,
the older run skips and the newer one publishes. Run *Publish site* by hand from the
Actions tab to republish the current `main`. `python scripts/ci.py site` builds:

- the front page (`templates/site/index.html`), generated from the repository: every
  manual with its status, released and preview PDFs, and how complete each language is.
  Opening a manual offers **Continue** (translations saved in this browser, with
  progress), **Translations Sliger already has** (start from the approved translation;
  only new text is left) and **Start a new translation**.
- one translation editor per current package in `translation-packages/` (not those listed
  in `superseded.json`), containing every language in `translations/`. The language is
  chosen in the link (`…/index.html?lang=de`); without it the editor shows the same
  choices. Each language is saved separately in the browser, and a translation file always
  opens as the translation for its own language. Images and fonts are shared by all
  editors in `editors/assets/` (named by content hash); a manual's preview loads them only
  when one of its pages is opened.
- preview PDFs of every manual from `main`, in English and in each language whose memory
  is complete
- the released PDFs from `releases/`

Editors whose English has changed since their package was exported are skipped; export
a new package for the current text. Link straight to a manual with `?manual=S630`.

## Returning translations (`.github/workflows/translation-import.yml`)

1. The translator downloads their translation file (`<package>-<lang>-translation.json`)
   and opens the pre-filled **Return a translation** form from the editor's
   **Send to Sliger**, then drags the file in. They need a GitHub account; otherwise they
   email the file and you import it (`scripts/translation_memory.py import`) or open the
   issue yourself.
2. A maintainer checks the issue and adds the label **`import-translation`**. Uploads never
   start an import on their own.
3. The workflow downloads the file (GitHub attachments only, `.json` or an older editor
   `.zip`, at most 25 MB), expands it against its package and validates it. It imports
   it into `translations/<lang>/memory.json`, builds every manual the language now
   completes, and opens a pull request with the import summary and translator notes.
   A link is posted on the issue. If validation fails, the reason is posted on the issue
   instead.
4. Review the `memory.json` diff and the PDFs in the run artifact, then merge.

GitHub does not start checks on pull requests opened by a workflow. The import run has
already built the translated PDFs; push a commit or close and reopen the pull request to
run the full checks.

## One-time setup (repository settings)

1. **Actions → General → Workflow permissions**: enable *Allow GitHub Actions to create and
   approve pull requests* (needed by the import workflow).
2. **Labels**: create `translation-return` (applied by the issue form) and
   `import-translation` (applied by a maintainer to start an import).
3. **Pages** (needs a public repository, or a paid plan for a private one): Settings →
   Pages → Source: *GitHub Actions*. Then add the repository variable `PAGES_ENABLED` with
   the value `true` (Settings → Secrets and variables → Actions → Variables). Until then,
   the publish workflow skips itself.
4. Recommended: require the *Manual checks* status on `main` (see below).

## Required check on `main`

Requiring the check means a pull request cannot be merged until *Manual checks* passes, so
text that breaks a layout, an invalid package or a broken editor never reaches `main`
or the published site. Rulesets need a public repository, a paid plan for private
repositories, or an organization plan that includes them.

1. Settings → Rules → Rulesets → New ruleset → **New branch ruleset**. Name it (for
   example *Protect main*) and set Enforcement status to **Active**.
2. Target branches → Add target → **Include default branch**.
3. Bypass list: add **Repository admin** with *For pull requests only*. This allows a
   deliberate emergency merge but no direct pushes.
4. Rules:
   - **Restrict deletions** and **Block force pushes**.
   - **Require a pull request before merging** (0 required approvals for a single
     maintainer; GitHub does not let authors approve their own pull requests).
   - **Require status checks to pass** → Add checks → `manuals` (the job in *Manual
     checks*; it is listed once it has run in the past week). Leave *Require branches to
     be up to date* off unless several people merge at once; it forces a re-check
     whenever another pull request merges first.
5. Create.

Once it is active:

- Documentation-only pull requests still get a passing check within seconds, so they
  are never stuck waiting.
- Pull requests opened by the translation import workflow get no checks automatically
  (a GitHub rule for workflow-created pull requests). Close and reopen the pull
  request, or push a commit to its branch, to run them.
- A translation made incomplete by an English edit is a warning and does not block.
  English failures, invalid packages, broken editors, and failures in a pull request
  that changes `translations/<lang>/` do.

Attachment downloads work without extra setup once the repository is public. Private
repository attachments may not be downloadable with the workflow's token.

## Cost and scale

Each manual takes about a minute to build. Pull requests rebuild only what they affect,
but `main` pushes and the site rebuild everything. At around 50 manuals, split the check
into a job matrix and cache site builds by content. Each translation editor is about
20–30 MB, so a site with many packages and languages approaches the 1 GB Pages limit;
publish only current packages' editors by then.
