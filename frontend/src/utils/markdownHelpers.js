/**
 * Markdown helpers (RC1.3)
 *
 * The AI Mentor sometimes emits math expressions wrapped in LaTeX delimiters
 * ($...$, $$...$$, \(...\), \[...\]) because Gemini defaults to LaTeX-style
 * math even when we ask for plain markdown. We don't have a KaTeX renderer
 * wired up, so leaving the raw delimiters in the output looks ugly.
 *
 * `stripMathDelimiters` unwraps the delimiters and leaves the inner
 * expression readable inline (`n log n`, `O(1)`, `x^2 + 1`). Backticks and
 * code fences are preserved untouched.
 */
export function stripMathDelimiters(input) {
  if (!input) return '';
  const text = String(input);

  // Preserve code fences and inline code from any transformation.
  const placeholders = [];
  let idx = 0;
  const preserved = text
    .replace(/```[\s\S]*?```/g, (match) => {
      placeholders.push(match);
      return `__PREPOS_CODE_${idx++}__`;
    })
    .replace(/`[^`\n]+`/g, (match) => {
      placeholders.push(match);
      return `__PREPOS_CODE_${idx++}__`;
    });

  // Order matters: block delimiters first.
  let out = preserved
    // \[ ... \]  (block)
    .replace(/\\\[([\s\S]+?)\\\]/g, (_, inner) => `\n\n${inner.trim()}\n\n`)
    // $$ ... $$  (block)
    .replace(/\$\$([\s\S]+?)\$\$/g, (_, inner) => `\n\n${inner.trim()}\n\n`)
    // \( ... \)  (inline)
    .replace(/\\\(([^\n]+?)\\\)/g, (_, inner) => inner.trim())
    // $ ... $   (inline). Guard: don't match currency (e.g. "$5 or $10").
    .replace(/(^|[^\d])\$([^\n$][^\n$]*?)\$(?![\d])/g, (m, prefix, inner) => `${prefix}${inner.trim()}`);

  // Restore preserved code blocks.
  out = out.replace(/__PREPOS_CODE_(\d+)__/g, (_, i) => placeholders[Number(i)] || '');

  return out;
}
