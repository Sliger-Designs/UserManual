/* Translations saved in this browser: one workspace per translation package, English
 * version and target language. Shared by the translation editor and the site index, which
 * run on the same origin and therefore see the same saved work. */
const Workspaces = (() => {
  const PREFIX = 'sliger-translation:';
  const CODE = /^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$/;
  const UNDETERMINED = 'und';  // Work saved before workspaces existed, with no language set.
  const base = (pkg, commit) => `${PREFIX}${pkg}:${commit}`;
  const key = (pkg, commit, language) => `${base(pkg, commit)}:${language}`;
  const valid = language => language === UNDETERMINED || (CODE.test(language || '') && language !== 'en');

  function read(storageKey) {
    try { return JSON.parse(localStorage.getItem(storageKey)); } catch { return null; }
  }

  /** Saved workspaces for a package version, most recently saved first. */
  function list(pkg, commit) {
    const prefix = base(pkg, commit) + ':', found = [];
    for (let i = 0; i < localStorage.length; i++) {
      const storageKey = localStorage.key(i);
      if (!storageKey || !storageKey.startsWith(prefix)) continue;
      const language = storageKey.slice(prefix.length);
      const saved = valid(language) && read(storageKey);
      if (!saved || !saved.tm) continue;
      found.push({language, key: storageKey, savedAt: saved.savedAt || '', summary: saved.summary || null,
                  name: (saved.job && saved.job.target_language_name) || languageName(language)});
    }
    return found.sort((a, b) => b.savedAt.localeCompare(a.savedAt));
  }

  /** Move work saved under the pre-workspace key (no language) to its language's workspace. */
  function migrate(pkg, commit) {
    const legacy = base(pkg, commit), saved = read(legacy);
    if (!saved) return null;
    const language = valid(saved.job && saved.job.target_language) ? saved.job.target_language : UNDETERMINED;
    if (!localStorage.getItem(key(pkg, commit, language))) localStorage.setItem(key(pkg, commit, language), JSON.stringify(saved));
    localStorage.removeItem(legacy);
    return language;
  }

  function remove(pkg, commit, language) { localStorage.removeItem(key(pkg, commit, language)); }

  function languageName(code) {
    if (!code || code === UNDETERMINED) return '';
    try {
      const name = new Intl.DisplayNames([code], {type: 'language'}).of(code);
      return name && name !== code ? name.charAt(0).toLocaleUpperCase(code) + name.slice(1) : '';
    } catch { return ''; }
  }

  const label = (code, name) => code === UNDETERMINED ? 'Translation without a language' : `${name || languageName(code) || code} (${code})`;
  const editorLink = (href, language, fresh) => `${href}?lang=${encodeURIComponent(language)}${fresh ? '&fresh=1' : ''}`;

  return {CODE, UNDETERMINED, key, valid, read, list, migrate, remove, languageName, label, editorLink};
})();
