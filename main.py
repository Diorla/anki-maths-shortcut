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

  const replacements = __REPLACEMENTS__;
  const shortcuts = Object.keys(replacements).sort((a, b) => b.length - a.length);
  const delimiter = /[\s\u00a0,.;:!?()[\]{}$]/;

  function convertInput(event) {
    if (event.inputType && !event.inputType.startsWith('insert')) return;

    const path = event.composedPath ? event.composedPath() : [];
    let target = path[0] || event.target;
    if (target && target.nodeType !== 1) target = target.parentElement;
    const field = target && target.closest && target.closest('[contenteditable]');
    if (!field) return;

    const root = field.getRootNode();
    const selection =
      root && root.getSelection ? root.getSelection() : document.getSelection();
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
      range.setEnd(node, offset); // shortcut + the delimiter just typed
      selection.removeAllRanges();
      selection.addRange(range);
      document.execCommand(
        'insertText', false, replacements[shortcut] + text.charAt(end)
      );
      return;
    }
  }

  document.addEventListener('input', convertInput, true);
})();
"""


def on_editor_did_load_note(editor):
    script = _EDITOR_SCRIPT.replace(
        "__REPLACEMENTS__", json.dumps(REPLACEMENTS, ensure_ascii=True)
    )
    editor.web.eval(script)


def install():
    from aqt import gui_hooks

    gui_hooks.editor_did_load_note.append(on_editor_did_load_note)