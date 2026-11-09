'use strict';
/* Sliger manual translation editor. Everything runs in this page: nothing is uploaded.
 * Translations are stored per English text (a shared translation memory), saved in this
 * browser, and exported as a translation package ZIP for scripts/translation_package.py. */

const DATA = JSON.parse(document.getElementById('editor-data').textContent);
const MODELS = DATA.package.models;
const PACKAGE = DATA.package;
// Each target language has its own saved workspace (workspaces.js); ?lang=xx selects it.
// Without a valid ?lang the editor shows the chooser instead of a translation.
const PARAMS = new URLSearchParams(location.search);
Workspaces.migrate(PACKAGE.name, PACKAGE.source_commit);
const LANGUAGE = Workspaces.valid(PARAMS.get('lang')) ? PARAMS.get('lang') : null;
const STORAGE_KEY = LANGUAGE && Workspaces.key(PACKAGE.name, PACKAGE.source_commit, LANGUAGE);
if (LANGUAGE && PARAMS.has('fresh')) {  // "Start over": drop this language's saved work first.
  localStorage.removeItem(STORAGE_KEY);
  history.replaceState(null, '', Workspaces.editorLink(location.pathname, LANGUAGE));
}
// Translations Sliger already has for this language (translations/<lang>/memory.json), or null.
const MEMORY = (LANGUAGE && DATA.memories[LANGUAGE]) || null;

// ---------------------------------------------------------------- small helpers
function h(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value == null || value === false) continue;
    if (key.startsWith('on')) node.addEventListener(key.slice(2), value);
    else if (key === 'class') node.className = value;
    else if (key === 'text') node.textContent = value;
    else node.setAttribute(key, value === true ? '' : value);
  }
  for (const child of children.flat()) if (child != null) node.append(child);
  return node;
}
const escapeHtml = text => text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const debounce = (fn, ms) => { let timer; return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms); }; };
const plural = (n, word) => `${n} ${word}${n === 1 ? '' : 's'}`;

// ---------------------------------------------------------------- protected text
// Mirrors protected() in scripts/translation_package.py, which remains the final check.
const JINJA = /{{[\s\S]*?}}|{%[\s\S]*?%}/g;
const WORD = '[\\p{L}\\p{N}_]';
const PROTECTED = [
  {name: 'placeholder', re: JINJA, ordered: true, raw: true},
  {name: 'HTML tag', re: /<\/?[A-Za-z][^>]*>/g, ordered: true},
  {name: 'link or email address', re: /https?:\/\/[^\s<>]+|[\p{L}\p{N}_.+-]+@[\p{L}\p{N}_.-]+\.[A-Za-z]+/gu},
  {name: 'hardware letter', re: new RegExp(`\\*\\*[${DATA.protected.hardware_letters}]\\*\\*|<strong>[${DATA.protected.hardware_letters}]</strong>`, 'g')},
  {name: 'number', re: new RegExp(`(?<!${WORD})\\p{Nd}+(?:[.,]\\p{Nd}+)*`, 'gu')},
  {name: 'technical term', re: termPattern(DATA.protected)},
];

// Same terms and order as term_pattern() in translation_package.py (longest first).
function termPattern(spec) {
  const escape = text => text.replace(/[\\^$.*+?()[\]{}|\/]/g, '\\$&');
  const terms = [...new Set(spec.terms)].sort((a, b) => b.length - a.length || (a < b ? -1 : a > b ? 1 : 0));
  return new RegExp(`(?<!${WORD})(?:${[...terms.map(escape), ...spec.patterns].join('|')})(?!${WORD})`, 'gu');
}

function protectedTokens(text) {
  const withoutJinja = text.replace(JINJA, '');
  return PROTECTED.map(kind => [...(kind.raw ? text : withoutJinja).matchAll(kind.re)].map(m => m[0]));
}

function countOf(list) { const counts = new Map(); for (const item of list) counts.set(item, (counts.get(item) || 0) + 1); return counts; }

function tokenProblems(english, translated) {
  const source = protectedTokens(english), target = protectedTokens(translated), problems = [];
  PROTECTED.forEach((kind, index) => {
    const want = countOf(source[index]), have = countOf(target[index]);
    const missing = [], extra = [];
    for (const [token, n] of want) for (let k = (have.get(token) || 0); k < n; k++) missing.push(token);
    for (const [token, n] of have) for (let k = (want.get(token) || 0); k < n; k++) extra.push(token);
    if (missing.length) problems.push(`Missing ${kind.name}${missing.length > 1 ? 's' : ''}: ${missing.join('  ')}`);
    if (extra.length) problems.push(`Remove or restore ${kind.name}${extra.length > 1 ? 's' : ''}: ${extra.join('  ')}` +
      (kind.name === 'number' ? ' (keep numbers, measurements and decimal points exactly as in English)' : ''));
    if (!missing.length && !extra.length && kind.ordered && source[index].join('\u0000') !== target[index].join('\u0000'))
      problems.push(`Keep these ${kind.name}s in their original order: ${source[index].join('  ')}`);
  });
  if (/\n/.test(translated) && !/\n/.test(english)) problems.push('Remove the line break: this text must stay on one line.');
  return problems;
}

function needsTranslation(text) {
  let rest = text.replace(JINJA, ' ');
  for (const kind of PROTECTED.slice(1)) rest = rest.replace(kind.re, ' ');
  return /\p{L}/u.test(rest.replace(/(?<![\p{L}])(mm|in|v(?=\p{Nd}))(?![\p{L}])/gu, ' '));
}

function tokenRanges(text) {
  const blanked = text.replace(JINJA, m => ' '.repeat(m.length)), ranges = [];
  for (const kind of PROTECTED)
    for (const m of (kind.raw ? text : blanked).matchAll(kind.re)) ranges.push([m.index, m.index + m[0].length]);
  ranges.sort((a, b) => a[0] - b[0] || b[1] - a[1]);
  const merged = [];
  for (const range of ranges) {
    const last = merged[merged.length - 1];
    if (last && range[0] <= last[1]) last[1] = Math.max(last[1], range[1]); else merged.push([...range]);
  }
  return merged;
}

function highlighted(text) {
  const fragment = document.createDocumentFragment();
  let position = 0;
  for (const [start, end] of tokenRanges(text)) {
    fragment.append(text.slice(position, start), h('span', {class: 'tok', title: 'Keep exactly as written'}, text.slice(start, end)));
    position = end;
  }
  fragment.append(text.slice(position));
  return fragment;
}

// ---------------------------------------------------------------- Markdown segmentation
// The translator edits sentence-sized segments; headings, list markers, table pipes,
// note wrappers and model conditions stay locked, so the file structure cannot break.
function splitOutsideTemplates(line, separator) {
  const pieces = []; let current = '', depth = null;
  for (let i = 0; i < line.length; i++) {
    const pair = line.slice(i, i + 2);
    if (!depth && (pair === '{{' || pair === '{%')) { depth = pair === '{{' ? '}}' : '%}'; current += pair; i++; continue; }
    if (depth && pair === depth) { depth = null; current += pair; i++; continue; }
    if (!depth && line[i] === separator) { pieces.push(current); current = ''; continue; }
    current += line[i];
  }
  pieces.push(current);
  return pieces;
}

const TABLE_SEPARATOR = /^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$/;

function segmentMarkdown(text) {
  const eol = text.includes('\r\n') ? '\r\n' : '\n';
  const sourceLines = text.split(/\r?\n/);
  let branch = null, branchTaken = [];
  const lines = sourceLines.map((line, index) => {
    const parts = [];
    const fixed = value => { if (value) parts.push({fixed: value}); };
    const segment = (value, role) => {
      const m = value.match(/^(\s*)([\s\S]*?)(\s*)$/);
      fixed(m[1]);
      if (m[2]) parts.push({text: m[2], role, models: branch});
      fixed(m[3]);
    };
    let m;
    if (!line.trim()) fixed(line);
    else if ((m = line.match(/^\s*{%\s*(if|elif|else|endif)\b\s*(.*?)\s*%}\s*$/))) {
      fixed(line);
      if (m[1] === 'endif') { branch = null; branchTaken = []; }
      else if (m[1] === 'else') branch = MODELS.filter(model => !branchTaken.includes(model));
      else {
        const condition = m[2].match(/^model\s*(==|!=)\s*'([^']*)'$/);
        if (!condition) throw new Error('Unsupported condition: ' + line);
        if (m[1] === 'if') branchTaken = [];
        branch = MODELS.filter(model => (model === condition[2]) === (condition[1] === '=='));
        branchTaken.push(...branch);
      }
    } else if (TABLE_SEPARATOR.test(line) && line.includes('|')) fixed(line);
    else if (/^\s*\|.*\|\s*$/.test(line)) {
      const heading = index + 1 < sourceLines.length && TABLE_SEPARATOR.test(sourceLines[index + 1]) && sourceLines[index + 1].includes('|');
      const cells = splitOutsideTemplates(line, '|');
      cells.forEach((cell, k) => {
        if (k > 0) fixed('|');
        if (k === 0 || k === cells.length - 1) fixed(cell); else segment(cell, heading ? 'table heading' : 'table cell');
      });
    } else if ((m = line.match(/^(\s*#{1,6}\s+(?:\d+\.\s+)?)(.*)$/))) { fixed(m[1]); segment(m[2], 'heading'); }
    else if ((m = line.match(/^(\s*(?:\d+\.|[-*+])\s+)(.*)$/))) { fixed(m[1]); segment(m[2], 'list item'); }
    else if ((m = line.match(/^(\s*<p\b[^>]*>)(.*?)(<\/p>\s*)$/))) {
      fixed(m[1]);
      const strong = m[2].match(/^<strong>(.*)<\/strong>$/);
      if (strong && !strong[1].includes('<strong>')) { fixed('<strong>'); segment(strong[1], 'note'); fixed('</strong>'); }
      else segment(m[2], 'note');
      fixed(m[3]);
    } else if ((m = line.match(/^( {0,3}> ?)(.*)$/))) { fixed(m[1]); segment(m[2], 'quote'); }
    else segment(line, 'paragraph');
    return parts;
  });
  return {eol, lines};
}

const assemble = (segmented, value) =>
  segmented.lines.map(parts => parts.map(part => 'text' in part ? value(part) : part.fixed).join('')).join(segmented.eol);

// ---------------------------------------------------------------- package model
const MD = DATA.markdown.map((file, index) => {
  const seg = segmentMarkdown(file.text);
  if (assemble(seg, part => part.text) !== file.text) throw new Error('Segmentation does not round-trip: ' + file.path);
  return {...file, index, seg};
});
const MD_BY_PATH = Object.fromEntries(MD.map(file => [file.path, file]));
const STRINGS = Object.entries(DATA.strings).map(([id, entry]) => ({id, ...entry}));
const FILE_PAGES = {};
for (const model of MODELS) for (const page of DATA.pages[model])
  for (const path of page.markdown) (FILE_PAGES[path] ||= []).push({model, page: page.page});

const USE_LABELS = {
  title: 'Page title', section: 'Section label above the page title', cover_description: 'Cover subtitle',
  status: 'Edition label (cover and page footers)',
  language_label: 'Language name on the cover tab and page footers, usually in capitals (for example DEUTSCH)',
  'image caption / alternative text': 'Image caption',
  'diagram accessibility label': 'Diagram description for screen readers (not printed)',
  'browser document title': 'Document title (PDF title bar)',
  'front I/O table heading': 'Front-port table heading',
  'contents accessibility label': 'Contents list description for screen readers (not printed)',
  'hardware image accessibility suffix': 'Word added to hardware image descriptions for screen readers (not printed)',
  'cover image accessibility suffix': 'Cover photo description for screen readers (not printed); follows the model name',
  'hardware key patch-color label': 'Screw color label in the hardware list',
};
const USE_ORDER = ['section', 'title', 'cover_description', 'status', 'language_label', 'image caption / alternative text'];
function describeUse(context) {
  const hardware = context.use.match(/^hardware ([A-Z]): (\w+)$/);
  if (hardware) return `Hardware ${hardware[1]} ${{name: 'name', description: 'description', color_label: 'color label'}[hardware[2]] || hardware[2]}`;
  if (context.use.startsWith('hardware chip color')) return 'Screw color name on picture tags';
  return USE_LABELS[context.use] || context.use;
}
const ROLE_LABELS = {heading: 'Heading', 'list item': 'Step / list item', 'table heading': 'Table heading',
  'table cell': 'Table cell', note: 'Note box', quote: 'Highlighted note', paragraph: 'Paragraph'};

const UNITS = new Map();
function addUse(english, use) {
  if (!UNITS.has(english)) UNITS.set(english, {english, uses: [], needs: needsTranslation(english)});
  UNITS.get(english).uses.push(use);
}
for (const entry of STRINGS) for (const context of entry.contexts)
  addUse(entry.source, {model: context.model || null, page: context.page ?? null, label: describeUse(context)});
for (const file of MD) for (const parts of file.seg.lines) for (const part of parts) {
  if (!('text' in part)) continue;
  for (const use of FILE_PAGES[file.path] || [])
    if (!part.models || part.models.includes(use.model)) addUse(part.text, {...use, label: ROLE_LABELS[part.role]});
}

// ---------------------------------------------------------------- state
function loadState() {
  const saved = STORAGE_KEY && Workspaces.read(STORAGE_KEY);
  const loaded = saved && saved.tm ? {job: {...DATA.job, ...saved.job}, tm: saved.tm, ui: saved.ui || {}}
                                   : {job: {...DATA.job}, tm: {}, ui: {}};
  if (LANGUAGE && LANGUAGE !== Workspaces.UNDETERMINED) {
    loaded.job.target_language = LANGUAGE;  // The workspace decides the language.
    loaded.job.target_language_name ||= (MEMORY && MEMORY.language_name) || Workspaces.languageName(LANGUAGE);
  }
  return loaded;
}
const state = loadState();
if (MEMORY && state.ui.memoryVersion !== MEMORY.version) {
  // Fill each memory translation once; later edits (including clearing a box) are kept.
  for (const [english, value] of Object.entries(MEMORY.entries)) if (!(english in state.tm)) state.tm[english] = value;
  state.ui.memoryVersion = MEMORY.version;
}
const fromMemory = english => MEMORY && MEMORY.entries[english] != null && state.tm[english] === MEMORY.entries[english];
const translation = english => { const value = state.tm[english]; return typeof value === 'string' && value.trim() ? value : null; };

function unitStatus(english) {
  const value = translation(english);
  if (value == null) return UNITS.get(english)?.needs === false ? 'auto' : 'todo';
  return tokenProblems(english, value).length ? 'bad' : 'done';
}

const translatedMarkdown = file => assemble(file.seg, part => translation(part.text) ?? part.text);

// Items translated without protected-text problems, out of those needing translation.
function progressOf(tm) {
  const all = [...UNITS.values()].filter(unit => unit.needs);
  const done = all.filter(unit => typeof tm[unit.english] === 'string' && tm[unit.english].trim()
    && !tokenProblems(unit.english, tm[unit.english]).length).length;
  return {done, total: all.length};
}

const saveNow = () => {
  if (!STORAGE_KEY) return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({...state, savedAt: new Date().toISOString(), summary: progressOf(state.tm)}));
    setSaved('Saved in this browser');
  } catch (error) {
    setSaved('Not saved in this browser: download the ZIP to keep your work', true);
  }
};
const save = debounce(saveNow, 400);
function setSaved(text, bad = false) { const node = document.getElementById('saved-state'); node.textContent = text; node.classList.toggle('bad', bad); }

// ---------------------------------------------------------------- template rendering
function renderJinja(text, model) {
  const values = DATA.expressions[model], stack = [];
  let output = '', last = 0, active = true, m;
  const re = /{%\s*([\s\S]*?)\s*%}|{{([\s\S]*?)}}|{#[\s\S]*?#}/g;
  text = text.replace(/\r\n?/g, '\n');
  while ((m = re.exec(text))) {
    if (active) output += text.slice(last, m.index);
    last = re.lastIndex;
    if (m[1] !== undefined) {
      const statement = m[1].trim(); let c;
      if ((c = statement.match(/^(if|elif)\s+model\s*(==|!=)\s*'([^']*)'$/))) {
        const holds = (model === c[3]) === (c[2] === '==');
        if (c[1] === 'if') { stack.push({parent: active, taken: holds}); active = active && holds; }
        else {
          const top = stack[stack.length - 1];
          if (!top) throw new Error('elif without if');
          active = top.parent && !top.taken && holds; top.taken ||= holds;
        }
      } else if (statement === 'else') {
        const top = stack[stack.length - 1];
        if (!top) throw new Error('else without if');
        active = top.parent && !top.taken; top.taken = true;
      } else if (statement === 'endif') {
        const top = stack.pop();
        if (!top) throw new Error('endif without if');
        active = top.parent;
      } else throw new Error('Unsupported template statement: ' + m[0]);
    } else if (m[2] !== undefined && active) {
      const key = m[2].trim();
      if (!(key in values)) throw new Error(`Unknown placeholder {{ ${key} }}`);
      output += values[key];
    }
  }
  if (active) output += text.slice(last);
  if (stack.length) throw new Error('Missing {% endif %}');
  return output.endsWith('\n') ? output.slice(0, -1) : output;  // Jinja drops one trailing newline
}

// Markdown subset used by the manuals (Python-Markdown with tables and sane_lists).
function inline(text) {
  const stash = [];
  const keep = html => `\u0001${stash.push(html) - 1}\u0002`;
  text = text.replace(/\\([\\`*_{}\[\]()#+\-.!|<>])/g, (_, c) => keep(escapeHtml(c)));
  text = text.replace(/`([^`]+)`/g, (_, code) => keep(`<code>${escapeHtml(code)}</code>`));
  text = text.replace(/<\/?[A-Za-z][^>]*>|&(?:#\d+|#x[0-9a-f]+|[a-z][a-z0-9]*);/gi, m => keep(m));
  text = escapeHtml(text);
  text = text.replace(/\[([^\]]+)\]\(([^()\s]+)\)/g, (_, label, url) => `<a href="${url}">${label}</a>`);
  text = text.replace(/\*\*(?=\S)([\s\S]*?\S)\*\*/g, '<strong>$1</strong>').replace(/__(?=\S)([\s\S]*?\S)__/g, '<strong>$1</strong>');
  text = text.replace(/(^|[^*])\*(?=[^\s*])([^*]*?[^\s*])\*(?!\*)/g, '$1<em>$2</em>');
  text = text.replace(/(^|[^\p{L}\p{N}_])_(?=\S)([^_]*?\S)_(?![\p{L}\p{N}_])/gu, '$1<em>$2</em>');
  return text.replace(/\u0001(\d+)\u0002/g, (_, n) => stash[n]);
}

function paragraphLines(lines) {
  return lines.map((line, k) => k < lines.length - 1 && / {2,}$/.test(line)
    ? inline(line.replace(/\s+$/, '')) + '<br />' : inline(line.replace(/\s+$/, ''))).join('\n');
}

function markdownToHtml(source) {
  const lines = source.replace(/\r\n?/g, '\n').split('\n'), out = [];
  const blank = line => !line.trim();
  const listItem = /^ {0,3}(\d+\.|[-*+])\s+(.*)$/;
  const htmlBlock = /^<(p|div|table|ul|ol|h[1-6]|blockquote|pre|section|figure|hr|dl|aside)\b/i;
  const cells = line => line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(cell => cell.trim());
  let i = 0, m;
  while (i < lines.length) {
    const line = lines[i];
    if (blank(line)) { i++; continue; }
    if ((m = line.match(/^(#{1,6})\s+(.*?)\s*#*\s*$/))) { out.push(`<h${m[1].length}>${inline(m[2])}</h${m[1].length}>`); i++; continue; }
    if (line.includes('|') && i + 1 < lines.length && TABLE_SEPARATOR.test(lines[i + 1]) && lines[i + 1].includes('-')) {
      const head = cells(line), rows = [];
      i += 2;
      while (i < lines.length && !blank(lines[i]) && lines[i].includes('|')) rows.push(cells(lines[i++]));
      out.push('<table>\n<thead>\n<tr>\n' + head.map(c => `<th>${inline(c)}</th>`).join('\n') + '\n</tr>\n</thead>\n<tbody>\n' +
        rows.map(row => '<tr>\n' + head.map((_, k) => `<td>${inline(row[k] ?? '')}</td>`).join('\n') + '\n</tr>').join('\n') + '\n</tbody>\n</table>');
      continue;
    }
    if (htmlBlock.test(line)) { const block = []; while (i < lines.length && !blank(lines[i])) block.push(lines[i++]); out.push(block.join('\n')); continue; }
    if (/^ {0,3}>/.test(line)) {
      const quote = [];
      while (i < lines.length && !blank(lines[i])) quote.push(lines[i++].replace(/^ {0,3}> ?/, ''));
      out.push(`<blockquote>\n${markdownToHtml(quote.join('\n'))}\n</blockquote>`);
      continue;
    }
    if ((m = line.match(listItem))) {
      const ordered = /\d/.test(m[1]), start = ordered ? parseInt(m[1], 10) : 1, items = [];
      let loose = false;
      while (i < lines.length) {
        const current = lines[i], item = current.match(listItem);
        if (item && /\d/.test(item[1]) === ordered) { items.push([item[2]]); i++; continue; }
        if (item) break;
        if (blank(current)) {
          let j = i; while (j < lines.length && blank(lines[j])) j++;
          const next = j < lines.length && lines[j].match(listItem);
          if (next && /\d/.test(next[1]) === ordered) { loose = true; i = j; continue; }
          break;
        }
        items[items.length - 1].push(current.trim()); i++;
      }
      const tag = ordered ? 'ol' : 'ul';
      out.push(`<${tag}${ordered && start !== 1 ? ` start="${start}"` : ''}>\n` + items.map(item =>
        loose ? `<li>\n<p>${paragraphLines(item)}</p>\n</li>` : `<li>${paragraphLines(item)}</li>`).join('\n') + `\n</${tag}>`);
      continue;
    }
    const paragraph = [];
    while (i < lines.length && !blank(lines[i]) && !/^#{1,6}\s/.test(lines[i])) paragraph.push(lines[i++]);
    out.push(`<p>${paragraphLines(paragraph)}</p>`);
  }
  return out.join('\n');
}

// One preview part, matching how build_sff_manual.py places rendered Markdown.
function markdownPart(model, mode, index, part) {
  const file = MD[index];
  let rendered = renderJinja(mode === 'english' ? file.text : translatedMarkdown(file), model);
  // Reference-column pages: lines after a `---` rule are the contact block (part C), as split_contact() does.
  if (DATA.templates[model].includes(`@@MD-${index}-C@@`)) {
    const rule = rendered.search(/^-{3,}[ \t]*$/m);
    const [main, contact] = rule < 0 ? [rendered, ''] : [rendered.slice(0, rule), rendered.slice(rendered.indexOf('\n', rule) + 1)];
    if (part === 'C') return markdownToHtml(contact);
    rendered = main;
  }
  if (part === 'AB') return markdownToHtml(rendered);
  if (part === 'A' || part === 'B') {
    const html = markdownToHtml(rendered), cut = html.indexOf('</p>');
    const head = cut < 0 ? html : html.slice(0, cut + 4);
    return part === 'A' ? head : html.slice(head.length);
  }
  const pieces = rendered.split(/^### (.+)$/m);
  if (part === 'F0') return markdownToHtml(pieces[0]);
  const k = Number(part.slice(1));
  if (part[0] === 'T') return pieces[1 + 2 * k].replace(/^\d+\.\s*/, '');  // Front I/O title
  if (part[0] === 'H') return pieces[1 + 2 * k];                          // Card heading as written
  return markdownToHtml(pieces[2 + 2 * k]);
}

// Placeholders such as hw() and ref() print labels that are translated as strings.
function fillStrings(text, mode) {
  return text.replace(/@@S-(s_[0-9a-f]{16})@@/g, (_, id) => {
    const source = DATA.strings[id].source;
    return mode === 'english' ? source : (translation(source) ?? source);
  });
}

// ---------------------------------------------------------------- previews
const assetUrls = [];
function assetUrl(index) {
  if (!assetUrls[index]) {
    const asset = DATA.assets[index], binary = atob(asset.data), bytes = new Uint8Array(binary.length);
    for (let k = 0; k < binary.length; k++) bytes[k] = binary.charCodeAt(k);
    assetUrls[index] = URL.createObjectURL(new Blob([bytes], {type: asset.type}));
  }
  return assetUrls[index];
}

class Preview {
  constructor(model) {
    this.model = model;
    this.issues = [];
    this.frame = h('iframe', {title: `${model} manual preview`, class: 'hidden'});
    document.getElementById('preview-stage').append(this.frame);
    this.ready = this.load();
  }
  async load() {
    let html = DATA.templates[this.model].replace(/@@ASSET-(\d+)@@/g, (_, n) => assetUrl(Number(n)));
    // Adjacent A/B halves (every layout except the split hardware key) render as one block.
    html = html.replace(/<p>@@MD-(\d+)-A@@<\/p>\s*<p>@@MD-\1-B@@<\/p>/g, '<!--md:$1:AB--><!--/md-->');
    html = html.replace(/<p>@@MD-(\d+)-([ABC]|F0|D\d+)@@<\/p>/g, '<!--md:$1:$2--><!--/md-->');
    // Print backgrounds exactly, as the build's Chromium PDF export does.
    html = html.replace('</head>', '<style>*{-webkit-print-color-adjust:exact;print-color-adjust:exact}</style></head>');
    const loaded = new Promise(resolve => this.frame.addEventListener('load', resolve, {once: true}));
    this.frame.srcdoc = html;
    await loaded;
    this.doc = this.frame.contentDocument;
    await Promise.all([this.doc.fonts.ready, ...[...this.doc.images].map(img => img.decode().catch(() => {}))]);
    this.bind();
  }
  bind() {
    this.texts = []; this.attrs = []; this.blocks = [];
    const walker = this.doc.createTreeWalker(this.doc, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT | NodeFilter.SHOW_COMMENT);
    const open = [];
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      if (node.nodeType === Node.COMMENT_NODE) {
        const m = node.data.match(/^md:(\d+):(\w+)$/);
        if (m) open.push({start: node, index: Number(m[1]), part: m[2]});
        else if (node.data === '/md') this.blocks.push({...open.pop(), end: node});
      } else if (node.nodeType === Node.TEXT_NODE) {
        if (node.data.includes('@@')) this.texts.push({node, template: node.data});
      } else for (const attribute of node.attributes)
        if (attribute.value.includes('@@')) this.attrs.push({node, name: attribute.name, template: attribute.value});
    }
  }
  render(mode) {
    const problems = [], strings = DATA.strings;
    const md = (index, part) => {
      try { return fillStrings(markdownPart(this.model, mode, index, part), mode); }
      catch (error) {
        problems.push(`${MD[index].path.replace('content/en/', '')}: ${error.message}`);
        return fillStrings(markdownPart(this.model, 'english', index, part), 'english');
      }
    };
    const fill = template => template.replace(/@@(S-(s_[0-9a-f]{16})|LANG|MD-(\d+)-([TH]\d+))@@/g, (_, token, id, index, part) => {
      if (token === 'LANG') return mode === 'english' ? 'en' : (state.job.target_language || 'en');
      if (id) return mode === 'english' ? strings[id].source : (translation(strings[id].source) ?? strings[id].source);
      return md(Number(index), part);
    });
    for (const item of this.texts) item.node.data = fill(item.template);
    for (const item of this.attrs) item.node.setAttribute(item.name, fill(item.template));
    for (const block of this.blocks) {
      const html = md(block.index, block.part);
      if (block.html === html) continue;
      block.html = html;
      while (block.start.nextSibling && block.start.nextSibling !== block.end) block.start.nextSibling.remove();
      const range = this.doc.createRange();
      range.setStartAfter(block.start);
      block.end.parentNode.insertBefore(range.createContextualFragment(html), block.end);
    }
    this.mode = mode;
    const check = this.frame.contentWindow.eval('(' + DATA.layout_check + ')');
    this.issues = mode === 'english' ? [] : check();
    this.templateProblems = problems;
  }
  show(pageId) {
    for (const other of Object.values(previews)) other.frame.classList.toggle('hidden', other !== this);
    const target = pageId && this.doc.getElementById(pageId);
    if (target) this.doc.defaultView.scrollTo(0, target.offsetTop - 12);
  }
}

const previews = {};
let previewMode = 'translated';
function fitPreviews() {
  const stage = document.getElementById('preview-stage');
  const width = 11 * 96 + 48, scale = stage.clientWidth / width;
  for (const preview of Object.values(previews)) {
    preview.frame.style.width = width + 'px';
    preview.frame.style.height = (stage.clientHeight / scale) + 'px';
    preview.frame.style.transform = `scale(${scale})`;
  }
}

async function renderPreviews() {
  for (const preview of Object.values(previews)) { await preview.ready; preview.render(previewMode); }
  renderNav();
  showLayoutWarnings();
}
const schedulePreview = debounce(renderPreviews, 350);

// ---------------------------------------------------------------- navigation
const NAV = [
  {key: 'project', label: 'Start here: project details'},
  {key: 'labels', label: 'Labels used throughout'},
  ...MODELS.flatMap(model => DATA.pages[model].map(page => ({key: `${model}:${page.page}`, model, page: page.page, id: page.id, label: page.title}))),
];
let current = state.ui.current && NAV.some(entry => entry.key === state.ui.current) ? state.ui.current : 'project';

function entryUnits(entry) {
  const seen = new Set(), list = [];
  const push = (english, label, group, extra = {}) => {
    if (seen.has(english)) return;
    seen.add(english);
    list.push({english, label, group, ...extra});
  };
  if (entry.key === 'labels') {
    for (const item of STRINGS) {
      const general = item.contexts.filter(context => context.page == null);
      if (general.length) push(item.source, describeUse(general[0]), 'Labels used on many pages');
    }
    return list;
  }
  if (!entry.model) return list;
  const strings = STRINGS.flatMap(item => item.contexts.filter(context => context.model === entry.model && context.page === entry.page)
    .map(context => ({item, context})));
  const order = context => { const k = USE_ORDER.indexOf(context.use); return k < 0 ? USE_ORDER.length + (context.use.startsWith('diagram') ? 1 : 0) : k; };
  strings.sort((a, b) => order(a.context) - order(b.context));
  for (const {item, context} of strings) push(item.source, describeUse(context), 'Titles, captions and labels');
  const page = DATA.pages[entry.model].find(item => item.page === entry.page);
  for (const path of page.markdown) {
    const file = MD_BY_PATH[path], models = [...new Set((FILE_PAGES[path] || []).map(use => use.model))];
    const group = models.length > 1 ? `Text shared by ${models.join(' and ')} (translate once)` : `${models[0]} text`;
    for (const parts of file.seg.lines) for (const part of parts)
      if ('text' in part && (!part.models || part.models.includes(entry.model)))
        push(part.text, ROLE_LABELS[part.role], group, {models: part.models && part.models.length < MODELS.length ? part.models : null});
  }
  return list;
}

function entryCounts(entry) {
  const counts = {total: 0, done: 0, bad: 0};
  for (const unit of entryUnits(entry)) {
    const status = unitStatus(unit.english);
    if (status === 'auto') continue;
    counts.total++;
    if (status === 'done') counts.done++;
    if (status === 'bad') counts.bad++;
  }
  return counts;
}

function layoutIssues(entry) {
  return entry.model ? (previews[entry.model]?.issues || []).filter(issue => issue.page === entry.id) : [];
}

function renderNav() {
  const nav = document.getElementById('nav');
  nav.replaceChildren();
  let heading = null;
  for (const entry of NAV) {
    const group = entry.model ? `${entry.model} manual` : 'Translation';
    if (group !== heading) { nav.append(h('h2', {text: group})); heading = group; }
    let badge = null;
    if (entry.key !== 'project') {
      const counts = entryCounts(entry), issues = layoutIssues(entry);
      if (counts.bad) badge = h('span', {class: 'state bad', title: 'Fix highlighted problems'}, `${counts.bad} !`);
      else if (issues.length) badge = h('span', {class: 'state warn', title: 'Text does not fit on the page'}, 'fit');
      else if (counts.total && counts.done === counts.total) badge = h('span', {class: 'state done', title: 'All translated'}, '✓');
      else if (counts.total) badge = h('span', {class: 'state', title: 'Translated / total'}, `${counts.done}/${counts.total}`);
    }
    nav.append(h('a', {href: '#' + entry.key, 'aria-current': entry.key === current ? 'page' : null,
      onclick: event => { event.preventDefault(); select(entry.key); }},
      h('span', {class: 'num'}, entry.page ? String(entry.page) : ''), h('span', {class: 'label', title: entry.label}, entry.label), badge));
  }
  const all = [...UNITS.values()].filter(unit => unit.needs);
  const done = all.filter(unit => unitStatus(unit.english) === 'done').length;
  document.getElementById('progress-bar').style.width = (100 * done / all.length) + '%';
  document.getElementById('progress-text').textContent = `${done} of ${all.length} items translated`;
}

function select(key) {
  current = key;
  state.ui.current = key;
  save();
  renderNav();
  renderMain();
  document.getElementById('editor').scrollTop = 0;
  showPreviewFor();
}

function showPreviewFor() {
  const entry = NAV.find(item => item.key === current);
  const model = entry.model || MODELS[0];
  const preview = previews[model];
  document.getElementById('preview-title').textContent = entry.model ? `${model} · page ${entry.page}` : `${model} · cover`;
  preview.ready.then(() => { preview.show(entry.id || 'cover'); showLayoutWarnings(); });
}

function showLayoutWarnings() {
  const entry = NAV.find(item => item.key === current), box = document.getElementById('layout-warnings');
  const model = entry.model || MODELS[0], preview = previews[model];
  const messages = layoutIssues(entry).length
    ? ['This page does not fit: the text runs into the footer or off the page. Shorten the translation on this page until this message disappears.'] : [];
  if (preview?.templateProblems?.length) messages.push(...preview.templateProblems.map(text => 'Preview shows English for ' + text));
  box.replaceChildren(...messages.map(text => h('div', {text})));
}

// ---------------------------------------------------------------- editor panel
function renderMain() {
  const main = document.getElementById('editor');
  const entry = NAV.find(item => item.key === current);
  main.replaceChildren();
  if (entry.key === 'project') return renderProject(main);
  main.append(h('h1', {text: entry.model ? `${entry.model} · page ${entry.page}: ${entry.label}` : entry.label}));
  main.append(h('p', {class: 'intro', text: entry.model
    ? 'Translate each item. Shared text is translated once and fills in everywhere it is used, including the other manual.'
    : 'These labels appear on many pages, in picture tags, or in descriptions for screen readers.'}));
  const hide = h('input', {type: 'checkbox', id: 'hide-done', checked: !!state.ui.hideDone,
    onchange: event => { state.ui.hideDone = event.target.checked; save(); renderMain(); }});
  main.append(h('label', {class: 'filter'}, hide, 'Hide finished items'));
  let group = null, shown = 0;
  const units = entryUnits(entry);
  for (const unit of units) {
    const status = unitStatus(unit.english);
    if (state.ui.hideDone && (status === 'done' || status === 'auto')) continue;
    if (unit.group !== group) { main.append(h('h2', {text: unit.group})); group = unit.group; }
    main.append(unitCard(unit, entry));
    shown++;
  }
  if (!shown) main.append(h('p', {class: 'intro', text: units.length ? 'Everything on this page is translated.' : 'Nothing to translate on this page.'}));
  const index = NAV.findIndex(item => item.key === current);
  if (index < NAV.length - 1) main.append(h('p', {}, h('button', {type: 'button', class: 'primary', onclick: () => select(NAV[index + 1].key)}, `Next: ${NAV[index + 1].model ? NAV[index + 1].model + ' page ' + NAV[index + 1].page : NAV[index + 1].label} →`)));
}

function otherUses(english, entry) {
  const uses = UNITS.get(english).uses.filter(use => use.model && !(use.model === entry.model && use.page === entry.page));
  return [...new Set(uses.map(use => `${use.model} p.${use.page}`))];
}

function unitCard(unit, entry) {
  const english = unit.english, needs = UNITS.get(english).needs;
  const card = h('div', {class: 'unit'});
  const area = h('textarea', {rows: 1, lang: state.job.target_language || null, spellcheck: 'true',
    'aria-label': `Translation of: ${english}`, placeholder: needs ? 'Type the translation…' : 'No translation needed (numbers or codes only)'});
  area.value = state.tm[english] ?? '';
  const chips = h('span'), problems = h('div', {class: 'problems', role: 'status'});
  const uses = otherUses(english, entry);
  const memoryBadge = h('span', {class: 'badge memory', title: 'Approved earlier for another manual or version. Check it fits here.'}, 'From translation memory');
  card.append(h('div', {class: 'meta'}, h('span', {class: 'badge'}, unit.label), memoryBadge,
    unit.models ? h('span', {class: 'badge model', title: 'This passage differs between the models'}, `${unit.models.join(', ')} only`) : null,
    uses.length ? h('span', {title: uses.join(', ')}, `Also used on ${uses.slice(0, 4).join(', ')}${uses.length > 4 ? ` and ${uses.length - 4} more` : ''}`) : null));
  card.append(h('div', {class: 'src', lang: 'en'}, highlighted(english)));
  card.append(area);
  const tokens = [...new Set(protectedTokens(english).flat())];
  const tools = h('div', {class: 'tools'});
  if (needs) tools.append(h('button', {type: 'button', class: 'link', title: 'Copy the English text into the box, then translate around the highlighted parts',
    onclick: () => { if (!area.value.trim() || area.value === english) { area.value = english; } else { area.setRangeText(english, area.selectionStart, area.selectionEnd, 'end'); } area.focus(); update(); }}, 'Start from English'));
  if (tokens.length) tools.append(h('span', {text: 'Keep exactly (click to insert):'}), chips);
  card.append(tools, problems);

  const resize = () => { area.style.height = 'auto'; area.style.height = area.scrollHeight + 2 + 'px'; };
  function refresh() {
    const value = area.value, status = unitStatus(english);
    memoryBadge.hidden = !fromMemory(english);
    card.className ='unit ' + (status === 'done' ? 'done' : status === 'bad' ? 'bad' : status === 'auto' ? 'auto' : '');
    const counts = countOf(protectedTokens(value).flat());
    chips.replaceChildren(...tokens.map(token => {
      const want = protectedTokens(english).flat().filter(item => item === token).length;
      const ok = (counts.get(token) || 0) >= want;
      const shown = value => value == null ? '—' : fillStrings(value, 'english').replace(/<[^>]+>/g, '');
      const values = token.startsWith('{{') ? MODELS.map(model => `${model}: ${shown(DATA.expressions[model][token.slice(2, -2).trim()])}`).join(', ') : '';
      return h('button', {type: 'button', class: 'chip ' + (value.trim() ? (ok ? 'ok' : 'missing') : ''),
        title: values ? `Inserted automatically (${values})` : 'Insert at the cursor',
        onmousedown: event => event.preventDefault(),
        onclick: () => { area.setRangeText(token, area.selectionStart, area.selectionEnd, 'end'); area.focus(); update(); }}, token);
    }), ' ');
    problems.textContent = translation(english) != null ? tokenProblems(english, value).join(' · ') : '';
  }
  function update() {
    if (area.value.trim()) state.tm[english] = area.value; else delete state.tm[english];
    resize(); refresh(); save(); renderNav(); schedulePreview();
  }
  area.addEventListener('input', update);
  area.addEventListener('keydown', event => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
      event.preventDefault();
      const areas = [...document.querySelectorAll('#editor textarea')];
      areas[areas.indexOf(area) + 1]?.focus();
    }
  });
  requestAnimationFrame(resize);
  refresh();
  return card;
}

const LANGUAGES = ['bg', 'cs', 'da', 'de', 'el', 'en-GB', 'es', 'et', 'fi', 'fr', 'ga', 'hr', 'hu', 'it', 'lt', 'lv', 'mt', 'nl', 'no', 'pl', 'pt', 'ro', 'sk', 'sl', 'sv', 'tr', 'uk'];
const NON_LATIN = /^(bg|el|uk|ru|sr|mk|be|ka|hy|he|ar|zh|ja|ko|th|hi)\b/;
const languageName = Workspaces.languageName;
const languageCodes = () => h('datalist', {id: 'language-codes'},
  LANGUAGES.filter(code => code !== 'en-GB').map(code => h('option', {value: code}, languageName(code))));
const editorLink = (language, fresh) => Workspaces.editorLink(location.pathname, language, fresh);

/** Open a language's workspace, asking first when this browser already has work for it. */
async function openLanguage(language, {fresh = false} = {}) {
  if (fresh && Workspaces.read(Workspaces.key(PACKAGE.name, PACKAGE.source_commit, language))) {
    const choice = await dialog(`You already have a ${Workspaces.label(language, languageName(language))} translation here`, [
      h('p', {text: 'Continue it, or start over? Starting over removes the work saved in this browser for this language. Download its ZIP first if you might need it.'}),
    ], [['Cancel', null], ['Start over', 'fresh'], ['Continue', 'continue']]);
    if (!choice) return;
    fresh = choice === 'fresh';
  }
  location.href = editorLink(language, fresh);
}

function renderChooser(main) {
  main.replaceChildren();
  const saved = Workspaces.list(PACKAGE.name, PACKAGE.source_commit);
  const savedLanguages = new Set(saved.map(item => item.language));
  const percent = ({done, total}) => total ? Math.round(100 * done / total) + '%' : '';
  main.append(h('h1', {text: `Translate the ${MODELS.join(' and ')} user guides`}),
    h('p', {class: 'intro', text: `English version ${PACKAGE.source_version}. Choose a translation. Work is saved only in this browser on this computer: it isn't available from another computer or browser, and clearing your browser data deletes it. To move your work or send it to Sliger, download its ZIP.`}));

  main.append(h('h2', {text: 'Continue a translation saved in this browser'}));
  if (!saved.length) main.append(h('p', {class: 'intro', text: 'None yet.'}));
  for (const item of saved) {
    main.append(h('div', {class: 'choice'},
      h('div', {}, h('strong', {text: Workspaces.label(item.language, item.name)}),
        h('div', {class: 'hint', text: [item.summary ? `${item.summary.done} of ${item.summary.total} items (${percent(item.summary)})` : '',
          item.savedAt ? 'saved ' + new Date(item.savedAt).toLocaleString() : ''].filter(Boolean).join(' · ')})),
      h('div', {class: 'choice-actions'},
        h('button', {type: 'button', class: 'link', onclick: async () => {
          const ok = await dialog('Remove from this browser?', [h('p', {text: `This deletes the ${Workspaces.label(item.language, item.name)} work saved in this browser. Download its ZIP first if you need it.`})],
            [['Cancel', false], ['Remove', true]]);
          if (ok) { Workspaces.remove(PACKAGE.name, PACKAGE.source_commit, item.language); renderChooser(main); }
        }}, 'Remove'),
        h('a', {class: 'button primary', href: editorLink(item.language)}, 'Continue'))));
  }

  const memories = Object.entries(DATA.memories).filter(([language]) => !savedLanguages.has(language));
  if (memories.length) {
    main.append(h('h2', {text: 'Edit a translation Sliger already has'}),
      h('p', {class: 'intro', text: 'Starts from the approved translation; only new or changed English text is left to translate.'}));
    for (const [language, memory] of memories) {
      const coverage = progressOf(memory.entries);
      main.append(h('div', {class: 'choice'},
        h('div', {}, h('strong', {text: Workspaces.label(language, memory.language_name)}),
          h('div', {class: 'hint', text: `${coverage.done} of ${coverage.total} items translated (${percent(coverage)})`})),
        h('div', {class: 'choice-actions'}, h('a', {class: 'button primary', href: editorLink(language)}, 'Edit'))));
    }
  }

  main.append(h('h2', {text: 'Start a new translation'}));
  const input = h('input', {list: 'language-codes', autocomplete: 'off', spellcheck: 'false', placeholder: 'Language code, e.g. de', 'aria-label': 'Language code'});
  const name = h('span', {class: 'hint'}), error = h('div', {class: 'problems'});
  input.addEventListener('input', () => { name.textContent = languageName(input.value.trim()); error.textContent = ''; });
  const start = () => {
    const code = input.value.trim();
    if (!Workspaces.valid(code) || code === Workspaces.UNDETERMINED)
      return void (error.textContent = 'Enter a language code such as de, fr, it, es, nl or pl (not en).');
    openLanguage(code, {fresh: true});
  };
  input.addEventListener('keydown', event => { if (event.key === 'Enter') start(); });
  main.append(h('div', {class: 'choice'}, h('div', {}, input, ' ', name, error),
    h('div', {class: 'choice-actions'}, h('button', {type: 'button', class: 'primary', onclick: start}, 'Start'))), languageCodes());
  main.append(h('p', {class: 'intro'}, 'Have a ZIP from this editor? Use ', h('b', {}, 'Open ZIP…'), ' above: it opens as the translation for its language.'));
}

/** Give work migrated without a language its language: move it to that language's workspace. */
async function assignLanguage(code) {
  if (!Workspaces.valid(code) || code === Workspaces.UNDETERMINED) return false;
  const target = Workspaces.key(PACKAGE.name, PACKAGE.source_commit, code);
  if (Workspaces.read(target)) {
    await dialog('That language already has a translation here', [h('p', {text: `Continue or remove the existing ${Workspaces.label(code)} translation first (Translations…).`})], [['OK', true]]);
    return false;
  }
  state.job.target_language = code;
  state.job.target_language_name ||= languageName(code);
  localStorage.setItem(target, JSON.stringify({...state, savedAt: new Date().toISOString(), summary: progressOf(state.tm)}));
  localStorage.removeItem(STORAGE_KEY);
  location.href = editorLink(code);
  return true;
}

function renderProject(main) {
  const job = state.job;
  const field = (key, label, hint, control) => {
    control.id = 'job-' + key;
    control.value = job[key] || '';
    control.addEventListener('input', () => { job[key] = control.value.trim(); save(); });
    return [h('label', {for: control.id, text: label}), control, hint ? h('div', {class: 'hint', text: hint}) : null];
  };
  let languageField;
  if (LANGUAGE === Workspaces.UNDETERMINED) {
    const input = h('input', {list: 'language-codes', autocomplete: 'off', spellcheck: 'false', id: 'job-target_language'});
    languageField = [h('label', {for: input.id, text: 'Language code'}),
      h('div', {}, input, ' ', h('button', {type: 'button', onclick: () => assignLanguage(input.value.trim())}, 'Set language')),
      h('div', {class: 'hint', text: 'This work was saved before translations had their own language. Set its language once, for example de.'})];
  } else {
    languageField = [h('label', {text: 'Language'}), h('div', {class: 'fixed-value'}, Workspaces.label(LANGUAGE, job.target_language_name), ' ',
      h('a', {href: location.pathname}, 'Choose another translation')), null];
  }
  const fontWarning = h('div', {class: 'notice bad', hidden: !NON_LATIN.test(LANGUAGE || '')},
    'The manual typeface only covers Latin alphabets. This language will print in a substitute font: tell Sliger before publishing.');
  const all = [...UNITS.values()].filter(unit => unit.needs);
  const done = all.filter(unit => unitStatus(unit.english) === 'done').length;
  main.append(
    h('h1', {text: `Translate the ${MODELS.join(' and ')} user guides`}),
    h('p', {class: 'intro', text: `Version ${DATA.package.source_version}. Your work is saved automatically, only in this browser on this computer. Download the ZIP to move it to another computer or browser.`}),
    h('ol', {class: 'steps'},
      h('li', {}, 'Fill in the details below.'),
      h('li', {}, 'Work through the pages on the left. Type each translation under its English text. The preview on the right shows the real page as you type.'),
      h('li', {}, 'Keep highlighted parts such as ', h('span', {class: 'tok'}, '**E**'), ', ', h('span', {class: 'tok'}, "{{ fact('…') }}"), ', numbers and model names exactly as written. Click a chip to insert it.'),
      h('li', {}, 'Text shared by both manuals only needs translating once. Most S640 pages fill in from your S630 work.'),
      h('li', {}, h('b', {}, 'Download ZIP for Sliger'), ' regularly as a backup, and send the final ZIP to Sliger. ', h('b', {}, 'Create PDF'), ' makes a printable manual from your translation.')),
    h('div', {class: 'form'},
      ...languageField,
      ...field('target_language_name', 'Language name', 'In the language itself, for example Deutsch.', h('input', {})),
      ...field('translator', 'Translator', 'Name and company.', h('input', {})),
      ...field('reviewer', 'Reviewer', 'Native-language reviewer who checked terminology and technical meaning.', h('input', {})),
      ...field('notes', 'Notes for Sliger', 'Terminology questions, text intentionally left in English, layout concerns, or illustrations that need localized text.', h('textarea', {}))),
    languageCodes(), fontWarning,
    h('p', {class: 'intro', text: `Progress: ${done} of ${all.length} items translated.`}),
    h('p', {}, h('button', {type: 'button', class: 'primary', onclick: () => select(NAV[1].key)}, 'Start translating →')));
}

// ---------------------------------------------------------------- ZIP files
const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; table[n] = c >>> 0; }
  return table;
})();
function crc32(bytes) { let c = 0xFFFFFFFF; for (const b of bytes) c = CRC_TABLE[(c ^ b) & 0xFF] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; }

function makeZip(files) {
  const encoder = new TextEncoder(), parts = [], central = [], now = new Date();
  const time = (now.getHours() << 11) | (now.getMinutes() << 5) | (now.getSeconds() >> 1);
  const date = ((now.getFullYear() - 1980) << 9) | ((now.getMonth() + 1) << 5) | now.getDate();
  let offset = 0;
  for (const [name, content] of files) {
    const nameBytes = encoder.encode(name), data = typeof content === 'string' ? encoder.encode(content) : content, crc = crc32(data);
    const local = new DataView(new ArrayBuffer(30));
    [[0, 0x04034b50, 4], [4, 20, 2], [6, 0x0800, 2], [8, 0, 2], [10, time, 2], [12, date, 2], [14, crc, 4],
     [18, data.length, 4], [22, data.length, 4], [26, nameBytes.length, 2], [28, 0, 2]]
      .forEach(([at, value, size]) => size === 4 ? local.setUint32(at, value, true) : local.setUint16(at, value, true));
    const entry = new DataView(new ArrayBuffer(46));
    [[0, 0x02014b50, 4], [4, 20, 2], [6, 20, 2], [8, 0x0800, 2], [10, 0, 2], [12, time, 2], [14, date, 2], [16, crc, 4],
     [20, data.length, 4], [24, data.length, 4], [28, nameBytes.length, 2], [42, offset, 4]]
      .forEach(([at, value, size]) => size === 4 ? entry.setUint32(at, value, true) : entry.setUint16(at, value, true));
    parts.push(local, nameBytes, data);
    central.push(entry, nameBytes);
    offset += 30 + nameBytes.length + data.length;
  }
  const size = central.reduce((sum, part) => sum + part.byteLength, 0), end = new DataView(new ArrayBuffer(22));
  end.setUint32(0, 0x06054b50, true); end.setUint16(8, files.length, true); end.setUint16(10, files.length, true);
  end.setUint32(12, size, true); end.setUint32(16, offset, true);
  return new Blob([...parts, ...central, end], {type: 'application/zip'});
}

async function readZip(file) {
  const bytes = new Uint8Array(await file.arrayBuffer()), view = new DataView(bytes.buffer), files = {};
  let end = -1;
  for (let i = bytes.length - 22; i >= Math.max(0, bytes.length - 65557); i--) if (view.getUint32(i, true) === 0x06054b50) { end = i; break; }
  if (end < 0) throw new Error('This is not a ZIP file.');
  let position = view.getUint32(end + 16, true);
  for (let k = view.getUint16(end + 10, true); k > 0; k--) {
    if (view.getUint32(position, true) !== 0x02014b50) throw new Error('The ZIP file is damaged.');
    const method = view.getUint16(position + 10, true), size = view.getUint32(position + 20, true);
    const nameLength = view.getUint16(position + 28, true), extra = view.getUint16(position + 30, true), comment = view.getUint16(position + 32, true);
    const local = view.getUint32(position + 42, true);
    const name = new TextDecoder().decode(bytes.subarray(position + 46, position + 46 + nameLength)).replace(/\\/g, '/');
    position += 46 + nameLength + extra + comment;
    if (!/(^|\/)translation\/[^/].*[^/]$/.test(name)) continue;
    const start = local + 30 + view.getUint16(local + 26, true) + view.getUint16(local + 28, true);
    const data = bytes.subarray(start, start + size);
    if (method === 0) files[name] = data;
    else if (method === 8) files[name] = new Uint8Array(await new Response(new Blob([data]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).arrayBuffer());
    else throw new Error(`Unsupported compression for ${name}.`);
  }
  return files;
}

function packageFiles() {
  const root = DATA.package.name + '/', files = [];
  for (const [path, text] of Object.entries(DATA.files)) files.push([root + path, text]);
  const job = {};
  for (const key of Object.keys(DATA.job)) job[key] = state.job[key] ?? DATA.job[key];
  files.push([root + 'translation/job.json', JSON.stringify(job, null, 2) + '\n']);
  const strings = {};
  for (const [id, entry] of Object.entries(DATA.strings))
    strings[id] = {source: entry.source, translation: translation(entry.source) ?? (needsTranslation(entry.source) ? '' : entry.source), contexts: entry.contexts};
  files.push([root + 'translation/strings.json', JSON.stringify(strings, null, 2) + '\n']);
  for (const file of MD) files.push([root + file.file, translatedMarkdown(file)]);
  // Exact English → translation pairs: restores work precisely (including text intentionally
  // left unchanged) and can seed translation of later manual versions.
  const entries = Object.fromEntries(Object.keys(state.tm).filter(english => UNITS.has(english) && translation(english) != null)
    .sort().map(english => [english, state.tm[english]]));
  files.push([root + MEMORY_FILE, JSON.stringify({schema: 1, source_language: 'en', target_language: state.job.target_language || '', entries}, null, 2) + '\n']);
  return files;
}
const MEMORY_FILE = 'translation/translation-memory.json';

function downloadBlob(blob, name) {
  const link = h('a', {href: URL.createObjectURL(blob), download: name});
  document.body.append(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(link.href), 10000);
}

function summary() {
  const all = [...UNITS.values()].filter(unit => unit.needs);
  return {
    total: all.length,
    todo: all.filter(unit => unitStatus(unit.english) === 'todo').length,
    bad: all.filter(unit => unitStatus(unit.english) === 'bad'),
    layout: Object.values(previews).flatMap(preview => preview.issues.map(issue => `${preview.model} ${issue.message}`)),
  };
}

async function downloadPackage() {
  const status = summary(), language = state.job.target_language || 'xx';
  const notes = [];
  if (!state.job.target_language) notes.push('Add the language code under “Start here” before sending the final version.');
  if (status.todo) notes.push(`${plural(status.todo, 'item')} still to translate (fine for a backup).`);
  if (status.bad.length) notes.push(`${plural(status.bad.length, 'item')} with problems to fix (highlighted in red).`);
  downloadBlob(makeZip(packageFiles()), `${DATA.package.name}-${language}-translation.zip`);
  state.ui.lastDownload = new Date().toISOString();
  saveNow();
  await dialog('ZIP downloaded', [
    h('p', {}, 'Keep this file as a backup, or send it to Sliger when the translation is finished. Use “Open ZIP…” to continue from it on another computer or browser.'),
    notes.length ? h('ul', {}, notes.map(text => h('li', {text}))) : h('p', {text: 'Everything is translated.'}),
  ], [['OK', true]]);
}

async function openPackage(file) {
  let files;
  try { files = await readZip(file); }
  catch (error) { return dialog('Could not open the ZIP', [h('p', {text: error.message})], [['OK', true]]); }
  const stringsName = Object.keys(files).find(name => name.endsWith('translation/strings.json'));
  if (!stringsName) return dialog('Could not open the ZIP', [h('p', {text: 'It does not contain translation/strings.json from this translation package.'})], [['OK', true]]);
  const root = stringsName.slice(0, -'translation/strings.json'.length), decode = name => files[root + name] && new TextDecoder().decode(files[root + name]);
  const found = {}, skipped = [];
  let conflicts = 0;
  const put = (english, value) => {
    if (typeof value !== 'string' || !value.trim()) return;
    if (english in found && found[english] !== value) { conflicts++; return; }
    found[english] = value;
  };
  try {
    // A filled-in string counts even when identical to English: translators copy terms that stay unchanged.
    for (const entry of Object.values(JSON.parse(decode('translation/strings.json')))) put(entry.source, entry.translation);
  } catch (error) { skipped.push('translation/strings.json (not valid JSON)'); }
  for (const file of MD) {
    const text = decode(file.file);
    if (text == null) { skipped.push(file.file + ' (missing)'); continue; }
    let theirs;
    try { theirs = segmentMarkdown(text); } catch (error) { skipped.push(file.file); continue; }
    const ours = file.seg;
    const same = ours.lines.length === theirs.lines.length && ours.lines.every((parts, k) => parts.length === theirs.lines[k].length &&
      parts.every((part, j) => ('text' in part) === ('text' in theirs.lines[k][j]) && ('text' in part || part.fixed === theirs.lines[k][j].fixed)));
    if (!same) { skipped.push(file.file + ' (layout changed; copy its text in by hand)'); continue; }
    ours.lines.forEach((parts, k) => parts.forEach((part, j) => {
      if ('text' in part && theirs.lines[k][j].text !== part.text) put(part.text, theirs.lines[k][j].text);
    }));
  }
  try {
    // Written by this editor. The package files win (they may have been corrected by hand);
    // the memory adds what files cannot show, such as text intentionally kept in English.
    const memory = decode(MEMORY_FILE);
    if (memory) for (const [english, value] of Object.entries(JSON.parse(memory).entries || {}))
      if (UNITS.has(english) && !(english in found) && typeof value === 'string' && value.trim()) found[english] = value;
  } catch (error) { skipped.push(MEMORY_FILE + ' (not valid JSON)'); }
  let job = {};
  try { job = JSON.parse(decode('translation/job.json') || '{}'); } catch { /* keep current details */ }
  // A ZIP always opens as the translation for its own language, never into another one.
  const target = Workspaces.valid(job.target_language) ? job.target_language : (LANGUAGE || Workspaces.UNDETERMINED);
  const here = target === LANGUAGE;
  const targetKey = Workspaces.key(PACKAGE.name, PACKAGE.source_commit, target);
  const targetState = here ? state : (Workspaces.read(targetKey) || {job: {...DATA.job}, tm: {}, ui: {}});
  const existing = Object.keys(targetState.tm || {}).length;
  const label = Workspaces.label(target, job.target_language_name || targetState.job?.target_language_name);
  const proceed = await dialog('Open translation ZIP', [
    h('p', {text: `Found ${plural(Object.keys(found).length, 'translated item')} for the ${label} translation.`}),
    !here && LANGUAGE ? h('p', {text: `It opens as your ${label} translation, not the one you are working on now.`}) : null,
    existing ? h('p', {text: `This browser already has ${plural(existing, 'translated item')} for ${label}. Items in the ZIP replace matching ones; others are kept.`}) : null,
    conflicts ? h('p', {text: `${plural(conflicts, 'passage')} had different translations in different places; the first one was used.`}) : null,
    skipped.length ? h('div', {}, h('p', {text: 'Not imported:'}), h('pre', {text: skipped.join('\n')})) : null,
  ], [['Cancel', false], ['Import', true]]);
  if (!proceed) return;
  targetState.tm = {...(targetState.tm || {}), ...found};
  targetState.job = {...DATA.job, ...(targetState.job || {})};
  for (const key of Object.keys(DATA.job)) if (job[key]) targetState.job[key] = job[key];
  if (here) {
    saveNow();
    renderNav(); renderMain(); renderPreviews();
  } else {
    localStorage.setItem(targetKey, JSON.stringify({...targetState, ui: targetState.ui || {}, savedAt: new Date().toISOString(), summary: progressOf(targetState.tm)}));
    location.href = editorLink(target);
  }
}

// ---------------------------------------------------------------- PDF
async function createPdf() {
  await renderPreviews();
  const status = summary(), notes = [];
  if (status.todo) notes.push(`${plural(status.todo, 'item')} not translated yet will print in English.`);
  if (status.bad.length) notes.push(`${plural(status.bad.length, 'item')} have problems (red); check them before publishing.`);
  if (status.layout.length) notes.push(`Some pages do not fit (${[...new Set(status.layout)].slice(0, 4).join('; ')}). Shorten the text on those pages.`);
  const choice = await dialog('Create a PDF', [
    h('p', {}, 'Choose a manual. Your browser’s print window opens: set ', h('b', {}, 'Destination: Save as PDF'),
      ', and under More settings set ', h('b', {}, 'Margins: None'), ' and tick ', h('b', {}, 'Background graphics'),
      '. The page size (US Letter, landscape) is set automatically. Use Chrome or Edge for the most accurate result.'),
    notes.length ? h('div', {class: 'notice'}, h('ul', {}, notes.map(text => h('li', {text})))) : null,
  ], [['Cancel', null], ...MODELS.map(model => [`${model} PDF`, model])]);
  if (!choice) return;
  const preview = previews[choice];
  await preview.ready;
  if (previewMode !== 'translated') await setMode('translated');
  preview.show();
  preview.doc.title = `${choice} · ${translation('User guide') ?? 'User guide'} · ${DATA.package.source_versions[choice]} (${state.job.target_language || 'draft'})`;
  preview.frame.contentWindow.focus();
  preview.frame.contentWindow.print();
}

// ---------------------------------------------------------------- dialogs and help
function dialog(title, body, buttons) {
  const box = document.getElementById('dialog');
  return new Promise(resolve => {
    box.replaceChildren(h('div', {class: 'body'}, h('h2', {text: title}), body),
      h('div', {class: 'buttons'}, buttons.map(([label, value], k) =>
        h('button', {type: 'button', class: k === buttons.length - 1 ? 'primary' : null, onclick: () => { box.close(); resolve(value); }}, label))));
    box.onclose = () => resolve(null);
    box.showModal();
    box.querySelector('.buttons button:last-child').focus();
  });
}

function showHelp() {
  const terminology = DATA.files['terminology.md'] || '';
  dialog('How this works', [
    h('p', {}, 'This page contains the English text of both manuals. Nothing you type is uploaded: it is saved in this browser on this computer. To move to another computer, download the ZIP and open it there.'),
    h('ul', {},
      h('li', {}, 'Highlighted parts (', h('span', {class: 'tok'}, '**E**'), ', ', h('span', {class: 'tok'}, "{{ fact('…') }}"), ', numbers, model names, HTML tags) must stay exactly as written. You can move them within the sentence. Placeholders in ', h('span', {class: 'tok'}, '{{ }}'), ' insert approved measurements automatically.'),
      h('li', {}, 'Keep measurements, screw specifications, part numbers and decimal points unchanged. Translate color names, which appear as their own items.'),
      h('li', {}, 'Items marked “S630 only” or “S640 only” differ between the models; translate both.'),
      h('li', {}, 'A “fit” marker on a page means the translated text is too long for the page. Shorten it until the marker disappears.'),
      h('li', {}, 'Press Ctrl+Enter to jump to the next box.')),
    h('h2', {text: 'Terminology'}), h('pre', {text: terminology}),
    h('h2', {text: 'Full instructions'}), h('pre', {text: DATA.files['README.md'] || ''}),
  ], [['Close', true]]);
}

function setMode(mode) {
  previewMode = mode;
  for (const button of document.querySelectorAll('.toggle button')) button.classList.toggle('on', button.dataset.mode === mode);
  return renderPreviews();
}

// ---------------------------------------------------------------- start
async function start() {
  document.getElementById('package-name').textContent = `${DATA.package.name.replace(/-en$/, '')} · English source ${DATA.package.source_version}` +
    (LANGUAGE ? ' · ' + Workspaces.label(LANGUAGE, state.job.target_language_name) : '');
  document.getElementById('btn-open').addEventListener('click', () => document.getElementById('file-open').click());
  document.getElementById('file-open').addEventListener('change', event => { const file = event.target.files[0]; event.target.value = ''; if (file) openPackage(file); });
  document.getElementById('btn-translations').href = location.pathname;
  document.getElementById('btn-help').addEventListener('click', showHelp);
  if (!LANGUAGE) {  // Choose or start a translation; nothing to edit or preview yet.
    document.body.classList.add('choosing');
    renderChooser(document.getElementById('editor'));
    return;
  }
  document.getElementById('btn-download').addEventListener('click', downloadPackage);
  document.getElementById('btn-pdf').addEventListener('click', createPdf);
  for (const button of document.querySelectorAll('.toggle button')) button.addEventListener('click', () => setMode(button.dataset.mode));
  window.addEventListener('beforeunload', saveNow);
  window.addEventListener('resize', debounce(fitPreviews, 100));
  setSaved(Object.keys(state.tm).length ? 'Restored your saved work' : '');
  for (const model of MODELS) previews[model] = new Preview(model);
  fitPreviews();
  renderNav();
  renderMain();
  await Promise.all(Object.values(previews).map(preview => preview.ready));
  document.getElementById('preview-loading').remove();
  await renderPreviews();
  showPreviewFor();
}
// Used by scripts/translation_editor_check.py.
window.translationEditor = {state, UNITS, MD, previews, packageFiles, makeZip, renderPreviews, tokenRanges, tokenProblems, select, language: LANGUAGE};
start().catch(error => {
  console.error(error);
  document.getElementById('editor').prepend(h('div', {class: 'notice bad', text: 'The editor could not start: ' + error.message}));
});
