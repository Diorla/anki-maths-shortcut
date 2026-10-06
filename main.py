"""Convert common math shortcuts to Unicode symbols in Anki's editor."""

import json
import re


REPLACEMENTS = {
    # Operators
    r"\times": "×",
    r"\cdot": "·",
    r"\div": "÷",
    r"\pm": "±",
    r"\mp": "∓",
    r"\neq": "≠",
    r"\ne": "≠",
    r"\approx": "≈",
    r"\equiv": "≡",
    r"\propto": "∝",
    r"\sim": "∼",
    r"\simeq": "≃",
    r"\cong": "≅",
    r"\leq": "≤",
    r"\le": "≤",
    r"\geq": "≥",
    r"\ge": "≥",
    r"\ll": "≪",
    r"\gg": "≫",
    # Arrows
    r"\rightarrow": "→",
    r"\to": "→",
    r"\leftarrow": "←",
    r"\gets": "←",
    r"\leftrightarrow": "↔",
    r"\iff": "⇔",
    r"\Rightarrow": "⇒",
    r"\Leftarrow": "⇐",
    r"\Leftrightarrow": "⇔",
    r"\uparrow": "↑",
    r"\downarrow": "↓",
    r"\updownarrow": "↕",
    r"\mapsto": "↦",
    # Greek — lowercase
    r"\alpha": "α",
    r"\beta": "β",
    r"\gamma": "γ",
    r"\delta": "δ",
    r"\epsilon": "ε",
    r"\varepsilon": "ϵ",
    r"\zeta": "ζ",
    r"\eta": "η",
    r"\theta": "θ",
    r"\vartheta": "ϑ",
    r"\iota": "ι",
    r"\kappa": "κ",
    r"\lambda": "λ",
    r"\mu": "μ",
    r"\nu": "ν",
    r"\xi": "ξ",
    r"\omicron": "ο",
    r"\pi": "π",
    r"\varpi": "ϖ",
    r"\rho": "ρ",
    r"\varrho": "ϱ",
    r"\sigma": "σ",
    r"\varsigma": "ς",
    r"\tau": "τ",
    r"\upsilon": "υ",
    r"\phi": "φ",
    r"\varphi": "ϕ",
    r"\chi": "χ",
    r"\psi": "ψ",
    r"\omega": "ω",
    # Greek — uppercase
    r"\Gamma": "Γ",
    r"\Delta": "Δ",
    r"\Theta": "Θ",
    r"\Lambda": "Λ",
    r"\Xi": "Ξ",
    r"\Pi": "Π",
    r"\Sigma": "Σ",
    r"\Phi": "Φ",
    r"\Psi": "Ψ",
    r"\Omega": "Ω",
    # Calculus
    r"\infinity": "∞",
    r"\infty": "∞",
    r"\partial": "∂",
    r"\nabla": "∇",
    r"\sum": "∑",
    r"\prod": "∏",
    r"\int": "∫",
    r"\iint": "∬",
    r"\iiint": "∭",
    r"\oint": "∮",
    r"\sqrt": "√",
    r"\cbrt": "∛",
    r"\fourthroot": "∜",
    # Sets / logic
    r"\in": "∈",
    r"\notin": "∉",
    r"\ni": "∋",
    r"\subset": "⊂",
    r"\subseteq": "⊆",
    r"\supset": "⊃",
    r"\supseteq": "⊇",
    r"\cup": "∪",
    r"\cap": "∩",
    r"\emptyset": "∅",
    r"\varnothing": "∅",
    r"\forall": "∀",
    r"\exists": "∃",
    r"\nexists": "∄",
    r"\therefore": "∴",
    r"\because": "∵",
    r"\land": "∧",
    r"\lor": "∨",
    r"\neg": "¬",
    r"\implies": "⇒",
    # Numbers / common constants
    r"\euler": "ℯ",
    r"\imaginary": "ℑ",
    r"\real": "ℜ",
    # Physics / units
    r"\degree": "°",
    r"\deg": "°",
    r"\angle": "∠",
    r"\perp": "⊥",
    r"\parallel": "∥",
    r"\prime": "′",
    r"\doubleprime": "″",
    # Common symbols
    r"\triangle": "△",
    r"\square": "□",
    r"\diamond": "◇",
    r"\star": "★",
    r"\bullet": "•",
    r"\dots": "…",
    r"\ldots": "…",
    r"\cdots": "⋯",
    r"\vdots": "⋮",
    r"\ddots": "⋱",
    # Existing shorthand
    ">=": "≥",
    "<=": "≤",
    "<->": "↔",
    "->": "→",
    "<-": "←",
    "!=": "≠",
    "+-": "±",
    "~=": "≈",
    "...": "…",
}


def replace_shortcuts(text):
    """Replace shortcuts followed by a non-word character or end of text."""
    alternatives = []
    for shortcut in sorted(REPLACEMENTS, key=len, reverse=True):
        escaped = re.escape(shortcut)
        if shortcut.startswith("\\"):
            alternatives.append(r"(?<![A-Za-z0-9_\\])" + escaped)
        else:
            alternatives.append(escaped)

    pattern = re.compile(
        r"(?:" + "|".join(alternatives) + r")(?=$|[^A-Za-z0-9_])"
    )
    return pattern.sub(lambda match: REPLACEMENTS[match.group(0)], text)

_EDITOR_SCRIPT = r"""
(() => {
  if (window.__mathShortcutsInstalled) return;
  window.__mathShortcutsInstalled = true;
  window.__mathShortcutsMode = 'auto';
  window.__mathShortcutsLastField = null;

  const replacements = __REPLACEMENTS__;
  const shortcuts = Object.keys(replacements).sort((a, b) => b.length - a.length);
  const delimiter = /[\s\u00a0,.;:!?()[\]{}$]/;

  // Same matching rules as replace_shortcuts() on the Python side.
  const escapeRe = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const pattern = new RegExp(
    '(?:' +
      shortcuts
        .map(s => (s.startsWith('\\') ? '(?<![A-Za-z0-9_\\\\])' : '') + escapeRe(s))
        .join('|') +
      ')(?=$|[^A-Za-z0-9_])',
    'g'
  );
  const convertText = text => text.replace(pattern, m => replacements[m]);

  function fieldFromEvent(event) {
    const path = event.composedPath ? event.composedPath() : [];
    let target = path[0] || event.target;
    if (target && target.nodeType !== 1) target = target.parentElement;
    return target && target.closest ? target.closest('[contenteditable]') : null;
  }

  function selectionFor(field) {
    const root = field.getRootNode();
    return root && root.getSelection ? root.getSelection() : document.getSelection();
  }

  // Auto mode: convert as you type.
  function convertInput(event) {
    if (window.__mathShortcutsMode !== 'auto') return;
    if (event.inputType && !event.inputType.startsWith('insert')) return;

    const field = fieldFromEvent(event);
    if (!field) return;

    const selection = selectionFor(field);
    if (!selection || selection.rangeCount === 0) return;

    const node = selection.anchorNode;
    const offset = selection.anchorOffset;
    if (!node || node.nodeType !== Node.TEXT_NODE || !field.contains(node)) return;

    const text = node.data;
    const end = offset - 1;
    if (end < 0 || !delimiter.test(text.charAt(end))) return;

    const before = text.slice(0, end);
    for (const shortcut of shortcuts) {
      if (!before.endsWith(shortcut)) continue;

      if (shortcut.startsWith('\\')) {
        const preceding = before.charAt(before.length - shortcut.length - 1);
        if (/[A-Za-z0-9_\\]/.test(preceding)) continue;
      }

      const start = end - shortcut.length;
      const range = document.createRange();
      range.setStart(node, start);
      range.setEnd(node, offset);
      selection.removeAllRanges();
      selection.addRange(range);
      document.execCommand(
        'insertText', false, replacements[shortcut] + text.charAt(end)
      );
      return;
    }
  }

  // Manual mode: convert the selection, or the whole field if nothing is selected.
  window.__mathShortcutsConvertSelection = () => {
    const field = window.__mathShortcutsLastField;
    if (!field || !field.isConnected) return;

    const selection = selectionFor(field);
    if (!selection) return;

    let range;
    if (
      selection.rangeCount > 0 &&
      !selection.isCollapsed &&
      field.contains(selection.anchorNode)
    ) {
      range = selection.getRangeAt(0).cloneRange();
    } else {
      range = document.createRange();
      range.selectNodeContents(field);
    }

    // Collect the selected part of every text node (keeps bold/italic etc. intact).
    const parts = [];
    const add = node => {
      const start = node === range.startContainer ? range.startOffset : 0;
      const end = node === range.endContainer ? range.endOffset : node.data.length;
      if (end > start) parts.push({ node, start, end });
    };
    const ancestor = range.commonAncestorContainer;
    if (ancestor.nodeType === Node.TEXT_NODE) {
      add(ancestor);
    } else {
      const walker = document.createTreeWalker(ancestor, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) {
        if (range.intersectsNode(walker.currentNode)) add(walker.currentNode);
      }
    }

    field.focus();
    // Go backwards so earlier offsets stay valid after each replacement.
    for (const { node, start, end } of parts.reverse()) {
      const old = node.data.slice(start, end);
      const converted = convertText(old);
      if (converted === old) continue;
      const r = document.createRange();
      r.setStart(node, start);
      r.setEnd(node, end);
      selection.removeAllRanges();
      selection.addRange(r);
      document.execCommand('insertText', false, converted);
    }
  };

  // Remember the last focused field, since clicking a toolbar button moves focus.
  document.addEventListener('focusin', event => {
    const field = fieldFromEvent(event);
    if (field) window.__mathShortcutsLastField = field;
  }, true);

  document.addEventListener('input', convertInput, true);
})();
"""

MODE_BUTTON_ID = "math_shortcuts_mode"


def _get_config():
    from aqt import mw

    config = mw.addonManager.getConfig(__name__) or {}
    if config.get("mode") not in ("auto", "manual"):
        config["mode"] = "auto"
    return config


def _apply_mode(editor, mode):
    """Push the mode to the page and sync the toggle button's highlight."""
    editor.web.eval(
        f"""
        window.__mathShortcutsMode = {json.dumps(mode)};
        (() => {{
          const b = document.getElementById({json.dumps(MODE_BUTTON_ID)});
          if (b) b.classList.toggle('highlighted', {'true' if mode == 'auto' else 'false'});
        }})();
        """
    )


def on_editor_did_load_note(editor):
    script = _EDITOR_SCRIPT.replace(
        "__REPLACEMENTS__", json.dumps(REPLACEMENTS, ensure_ascii=True)
    )
    editor.web.eval(script)
    _apply_mode(editor, _get_config()["mode"])


def _convert_selection(editor):
    editor.web.eval(
        "window.__mathShortcutsConvertSelection && window.__mathShortcutsConvertSelection();"
    )


def _toggle_mode(editor):
    from aqt import mw

    config = _get_config()
    config["mode"] = "manual" if config["mode"] == "auto" else "auto"
    mw.addonManager.writeConfig(__name__, config)
    _apply_mode(editor, config["mode"])


def on_editor_did_init_buttons(buttons, editor):
    buttons.append(
        editor.addButton(
            icon=None,
            cmd="math_shortcuts_convert",
            func=_convert_selection,
            tip="Convert math shortcuts in selection (Ctrl+Shift+M)",
            label="Σ",
            keys="Ctrl+Shift+M",
        )
    )
    buttons.append(
        editor.addButton(
            icon=None,
            cmd="math_shortcuts_toggle",
            func=_toggle_mode,
            tip="Highlighted: convert automatically while typing. Off: manual (use Σ).",
            label="Auto",
            id=MODE_BUTTON_ID,
            toggleable=True,
        )
    )


def install():
    from aqt import gui_hooks

    gui_hooks.editor_did_load_note.append(on_editor_did_load_note)
    gui_hooks.editor_did_init_buttons.append(on_editor_did_init_buttons)