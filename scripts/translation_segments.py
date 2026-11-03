"""Split manual Markdown into translatable segments, the unit of a translation memory.

Must match segmentMarkdown() and needsTranslation() in templates/translation-editor/editor.js
exactly: the editor and the build look up the same English text. translation_editor_check.py
compares both on every file. Headings, list markers, table pipes, note wrappers and model
conditions stay fixed; the text between them is a segment."""
import re

from translation_package import term_pattern

TABLE_SEPARATOR = re.compile(r'\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*')
JINJA = re.compile(r'{{.*?}}|{%.*?%}', re.S)
LETTER = r'[^\W\d_]'


def split_outside_templates(line, separator):
    pieces, current, closing, i = [], '', None, 0
    while i < len(line):
        pair = line[i:i + 2]
        if not closing and pair in ('{{', '{%'):
            closing = '}}' if pair == '{{' else '%}'
            current += pair
            i += 2
        elif closing and pair == closing:
            closing = None
            current += pair
            i += 2
        elif not closing and line[i] == separator:
            pieces.append(current)
            current = ''
            i += 1
        else:
            current += line[i]
            i += 1
    pieces.append(current)
    return pieces


def segment_markdown(text, models=()):
    """Return {'eol', 'lines'}: each line is a list of {'fixed': str} or {'text', 'role', 'models'}."""
    eol = '\r\n' if '\r\n' in text else '\n'
    source_lines = re.split(r'\r?\n', text)
    branch, taken, lines = None, [], []
    for index, line in enumerate(source_lines):
        parts = []

        def fixed(value):
            if value:
                parts.append({'fixed': value})

        def segment(value, role):
            lead, body, trail = re.fullmatch(r'(\s*)(.*?)(\s*)', value, re.S).groups()
            fixed(lead)
            if body:
                parts.append({'text': body, 'role': role, 'models': branch})
            fixed(trail)

        is_separator = lambda value: bool(TABLE_SEPARATOR.fullmatch(value)) and '|' in value
        if not line.strip():
            fixed(line)
        elif m := re.fullmatch(r'\s*{%\s*(if|elif|else|endif)\b\s*(.*?)\s*%}\s*', line):
            fixed(line)
            if m[1] == 'endif':
                branch, taken = None, []
            elif m[1] == 'else':
                branch = [model for model in models if model not in taken]
            else:
                condition = re.fullmatch(r"model\s*(==|!=)\s*'([^']*)'", m[2])
                if not condition:
                    raise ValueError('Unsupported condition: ' + line)
                if m[1] == 'if':
                    taken = []
                branch = [model for model in models if (model == condition[2]) == (condition[1] == '==')]
                taken += branch
        elif is_separator(line):
            fixed(line)
        elif re.fullmatch(r'\s*\|.*\|\s*', line):
            heading = index + 1 < len(source_lines) and is_separator(source_lines[index + 1])
            cells = split_outside_templates(line, '|')
            for k, cell in enumerate(cells):
                if k:
                    fixed('|')
                if k in (0, len(cells) - 1):
                    fixed(cell)
                else:
                    segment(cell, 'table heading' if heading else 'table cell')
        elif m := re.fullmatch(r'(\s*#{1,6}\s+(?:[0-9]+\.\s+)?)(.*)', line):
            fixed(m[1])
            segment(m[2], 'heading')
        elif m := re.fullmatch(r'(\s*(?:[0-9]+\.|[-*+])\s+)(.*)', line):
            fixed(m[1])
            segment(m[2], 'list item')
        elif m := re.fullmatch(r'(\s*<p\b[^>]*>)(.*?)(</p>\s*)', line):
            fixed(m[1])
            strong = re.fullmatch(r'<strong>(.*)</strong>', m[2])
            if strong and '<strong>' not in strong[1]:
                fixed('<strong>')
                segment(strong[1], 'note')
                fixed('</strong>')
            else:
                segment(m[2], 'note')
            fixed(m[3])
        elif m := re.fullmatch(r'( {0,3}> ?)(.*)', line):
            fixed(m[1])
            segment(m[2], 'quote')
        else:
            segment(line, 'paragraph')
        lines.append(parts)
    return {'eol': eol, 'lines': lines}


def assemble(segmented, value):
    """Rebuild Markdown, replacing each segment with value(part)."""
    return segmented['eol'].join(''.join(value(part) if 'text' in part else part['fixed'] for part in parts)
                                 for parts in segmented['lines'])


def segments(segmented):
    return [part for parts in segmented['lines'] for part in parts if 'text' in part]


def needs_translation(text, spec):
    """False for text made only of protected tokens, numbers, units and versions."""
    letters = '[' + spec['hardware_letters'] + ']'
    rest = JINJA.sub(' ', text)
    for pattern in (r'</?[A-Za-z][^>]*>', r'https?://[^\s<>]+|[\w.+-]+@[\w.-]+\.[A-Za-z]+',
                    rf'\*\*{letters}\*\*|<strong>{letters}</strong>', r'(?<![\w])\d+(?:[.,]\d+)*', term_pattern(spec)):
        rest = re.sub(pattern, ' ', rest)
    rest = re.sub(rf'(?<!{LETTER})(mm|in|v(?=\d))(?!{LETTER})', ' ', rest)
    return bool(re.search(LETTER, rest))
