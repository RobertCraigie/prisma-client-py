// TODO: spamming change theme button breaks this
// TODO: load shiki languages dynamically, instead of using two loops

const LANGUAGE_DETECT_RE = /\blang(?:uage)?-([\w-]+)\b/i;

function getLanguages() {
  // get all the languages required to load shiki with for the current page
  const languages = {};
  const blocks = document.querySelectorAll('pre code');

  blocks.forEach((element) => {
    match = LANGUAGE_DETECT_RE.exec(element.className);
    if (match) {
      const lang = match[1];

      for (var i = shiki.BUNDLED_LANGUAGES.length - 1; i >= 0; i--) {
        var language = shiki.BUNDLED_LANGUAGES[i];
        if (
          language.id == lang ||
          (language.aliases && language.aliases.includes(lang))
        ) {
          languages[lang] = language;
        }
      }
    }
  });

  return languages;
}

function highlightAll(dark) {
  const blocks = document.getElementsByClassName('highlight');
  const languages = getLanguages();
  const theme = dark ? 'github-dark' : 'github-light';
  console.debug(theme);

  shiki
    .getHighlighter({
      theme: theme,
      langs: Object.values(languages),
    })
    .then((highlighter) => {
      for (var i = blocks.length - 1; i >= 0; i--) {
        const root = blocks[i];

        if (!root.classList.contains('shiki')) {
          root.classList.add('shiki');
        }

        const elements = root.getElementsByTagName('code');

        for (var j = elements.length - 1; j >= 0; j--) {
          const element = elements[j];
          match = LANGUAGE_DETECT_RE.exec(element.className);

          if (match) {
            const lang = languages[match[1]];
            if (lang) {
              // strip leading and ending pre/code tags as we already have them
              let html = highlighter.codeToHtml(element.textContent, lang.id);
              html = html.replace(/<pre.*<code>/, '');
              html = html.replace(/<\/code><\/pre>/, '');
              element.innerHTML = html;
            }
          }
        }
      }
    });
}

function isDarkTheme() {
  let baseKey = '/.__palette';
  let raw = window.localStorage.getItem(baseKey);
  if (raw == null) {
    // this happens on ReadTheDocs as the theme storage keys use a different
    // naming schema, e.g. /en/stable/.__palette instead of just /.__palette.
    // Work around this by finding the first two parts of the path and
    // inserting that to the start of the key if the original key is not found
    let key = window.location.pathname.split('/').splice(0, 3).join('/');
    raw = window.localStorage.getItem(key + baseKey);
  }

  const data = JSON.parse(raw);

  if (data) {
    return data.color.scheme == 'slate';
  }

  return false;
}

// NOTE: we have to handle click events like this as both
// elements will not be available at the same time
document.body.addEventListener('click', (event) => {
  if (event.target.id == '__palette_1') {
    highlightAll(false);
  } else if (event.target.id == '__palette_2') {
    highlightAll(true);
  }
});

document$.subscribe(() => {
  highlightAll(isDarkTheme());
});
