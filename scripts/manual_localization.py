"""Text lookup used by manual builds: English, a returned translation package, editor
placeholders, or a recorder that lists every translatable text a build uses.

Builds call `text(english, use, page)` for each display string and `markdown(path, english,
layout, page)` for each Markdown file, and `begin_page(number, spec)` before each page.
`use` describes where a string appears; `page` is its 1-based page number (None when the
string is used on many pages)."""
import json
from pathlib import Path
import re


class Localizer:
    """English source text, unchanged."""
    language = 'en'

    @property
    def is_source(self):
        return self.language == 'en'

    def describe(self):
        """Where translated text comes from, for build reports."""
        return 'English source'

    def begin_page(self, number, spec):
        pass

    def text(self, english, use=None, page=None):
        return english

    def markdown(self, path, english, layout=None, page=None):
        """Return Markdown for repository path `content/en/...`; `english` is its source text."""
        return english


class RecordingLocalizer(Localizer):
    """English output that records each string and Markdown file a build uses, with contexts.

    Run builds for several models with one recorder (set `model` before each build) to get a
    translation catalog in which shared text appears once."""

    def __init__(self):
        self.model = None
        self.strings = {}      # English text -> list of {use, model?, page?}
        self.markdown_files = {}  # repository path -> English text
        self.pages = {}        # model -> [{page, id, title, markdown}]

    def begin_page(self, number, spec):
        self.pages.setdefault(self.model, []).append(
            {'page': number, 'id': spec['id'], 'title': spec['title'], 'markdown': []})

    def text(self, english, use=None, page=None):
        if english:
            context = {'use': use or 'label', 'model': self.model}
            if page is not None:
                context['page'] = page
            contexts = self.strings.setdefault(english, [])
            if context not in contexts:
                contexts.append(context)
        return english

    def markdown(self, path, english, layout=None, page=None):
        self.markdown_files[path] = english
        if page is not None:
            entry = self.pages[self.model][page - 1]
            if path not in entry['markdown']:
                entry['markdown'].append(path)
        return english


class PackageLocalizer(Localizer):
    """Translated text from a translation package's `translation/` folder."""

    def __init__(self, package):
        self.package = Path(package)
        job = json.loads((self.package / 'translation/job.json').read_text(encoding='utf-8'))
        self.language = (job.get('target_language') or '').strip()
        if not re.fullmatch(r'[a-z]{2,3}(-[A-Za-z0-9]{2,8})*', self.language) or self.language == 'en':
            raise ValueError('Set a non-English target_language (for example "de") in translation/job.json')
        catalog = json.loads((self.package / 'translation/strings.json').read_text(encoding='utf-8'))
        self.strings = {entry['source']: entry['translation'] for entry in catalog.values()}

    def describe(self):
        return 'translation package ' + self.package.name

    def text(self, english, use=None, page=None):
        if english not in self.strings:
            raise KeyError(f'Translation package has no entry for {english!r}; export a new package')
        value = self.strings[english]
        if not value.strip():
            raise ValueError(f'Untranslated string: {english!r}')
        return value

    def markdown(self, path, english, layout=None, page=None):
        relative = Path(path).relative_to('content/en')
        return (self.package / 'translation/content' / relative).read_text(encoding='utf-8')


class TokenLocalizer(Localizer):
    """Placeholders that the browser translation editor replaces with live translations.

    Strings become `@@S-<id>@@`. Markdown becomes `@@MD-<index>-A@@` (HTML up to and
    including the first `</p>`) and `@@MD-<index>-B@@` (the rest), so templates that
    split rendered Markdown still place each part correctly. Front I/O and illustrated-card
    Markdown keep their `###` headings: `F0` is the introduction and `D<n>` each heading's
    text; `T<n>` is a front I/O title (number stripped), `H<n>` a card heading as written.
    """
    HEADING_LAYOUTS = {'front-io': 'T', 'illustrated-cards': 'H'}
    language = '@@LANG@@'

    def __init__(self, catalog, markdown_files):
        self.ids = {entry['source']: key for key, entry in catalog.items()}
        self.index = {path: number for number, path in enumerate(markdown_files)}

    def text(self, english, use=None, page=None):
        return f'@@S-{self.ids[english]}@@'

    def markdown(self, path, english, layout=None, page=None):
        number = self.index[path]
        if layout not in self.HEADING_LAYOUTS:
            return f'@@MD-{number}-A@@\n\n@@MD-{number}-B@@\n'
        heading = self.HEADING_LAYOUTS[layout]
        headings = len(re.findall(r'^### (.+)$', english, flags=re.MULTILINE))
        parts = [f'@@MD-{number}-F0@@']
        for item in range(headings):
            parts += [f'### @@MD-{number}-{heading}{item}@@', f'@@MD-{number}-D{item}@@']
        return '\n\n'.join(parts) + '\n'
