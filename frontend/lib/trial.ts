// Helpers for the trial room: find the "# PROBLEM:" block and insert the coach's comments.

export const COACH_START = "# --- COACH (hint level {n}) ---";
export const COACH_END = "# --- END COACH ---";

const isProblemLine = (l: string) => /^\s*#\s*PROBLEM:/i.test(l);
const isCoachStart = (l: string) => /^\s*#\s*--- COACH/.test(l);
const isCoachEnd = (l: string) => /^\s*#\s*--- END COACH/.test(l);
const isComment = (l: string) => /^\s*#/.test(l);

/** The problem block: the `# PROBLEM:` line plus the comment lines right after it (not the coach block). */
export function findProblem(
  code: string,
): { start: number; end: number; text: string } | null {
  const lines = code.split("\n");
  const start = lines.findIndex(isProblemLine);
  if (start < 0) return null;
  let end = start;
  while (
    end + 1 < lines.length &&
    isComment(lines[end + 1]) &&
    !isCoachStart(lines[end + 1])
  )
    end++;
  return {
    start,
    end,
    text: lines
      .slice(start, end + 1)
      .join("\n")
      .trim(),
  };
}

/** Make sure every line is a comment, so the coach can never put runnable code in the editor. */
export function toComments(reply: string): string {
  return reply
    .split("\n")
    .filter((l) => !/^\s*TOPIC:/i.test(l))
    .map((l) => (l.trim() === "" ? "#" : isComment(l) ? l : `# ${l}`))
    .join("\n")
    .trim();
}

/** Put the coach block right under the problem block. An older coach block there is replaced. */
export function insertCoach(
  code: string,
  reply: string,
  level: number,
): string | null {
  const problem = findProblem(code);
  if (!problem) return null;
  const lines = code.split("\n");
  let after = problem.end + 1;
  if (after < lines.length && isCoachStart(lines[after])) {
    let e = after;
    while (e < lines.length && !isCoachEnd(lines[e])) e++;
    after = Math.min(e + 1, lines.length); // drop the old block including its end marker
    lines.splice(problem.end + 1, after - (problem.end + 1));
  }
  const block = [
    COACH_START.replace("{n}", String(level)),
    toComments(reply),
    COACH_END,
  ];
  lines.splice(problem.end + 1, 0, ...block);
  return lines.join("\n");
}

/** Hide the `TOPIC: ...` line Claude adds for the app. */
export const stripTopic = (text: string) =>
  text.replace(/^[ \t]*TOPIC:.*$/gim, "").trimEnd();

/** A drill as editor text: the task as comments, then the starter code. */
export function drillToEditor(d: {
  title: string;
  prompt: string;
  calls: string[];
  starter: string;
}): string {
  const task = d.prompt
    .replace(/^```.*$/gm, "")
    .split("\n")
    .map((l) => (l.trim() ? `# ${l}` : "#"))
    .join("\n")
    .replace(/(#\n)+/g, "#\n")
    .trim();
  const calls = d.calls.map((c) => `#   ${c}`).join("\n");
  return `# DRILL: ${d.title}\n${task}\n#\n# Press Check drill. It will call your function like this:\n${calls}\n\n${d.starter}\n`;
}

export const TRIAL_STARTER = `# PROBLEM: write what you are stuck on here, in your own words.
# Example: I have a dict of scores. I want the name with the highest score.

scores = {"asha": 7, "ravi": 9, "mina": 5}

print(scores)
`;
