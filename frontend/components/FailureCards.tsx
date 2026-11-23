import { Failure } from "@/lib/api";

const TITLE: Record<Failure["kind"], string> = {
  assertion: "Wrong result",
  exception: "Your code crashed",
  syntax: "Python cannot read your code",
  import: "Tests cannot find your function",
};

export default function FailureCards({ failures }: { failures?: Failure[] }) {
  if (!failures?.length) return null;
  return (
    <>
      {failures.map((f, i) => (
        <div className="fail" key={i}>
          <div className="fail-title">
            {TITLE[f.kind]} <span className="muted">· {f.test}</span>
          </div>
          {f.message && (
            <div className="fail-row">
              <b>{f.kind === "assertion" ? "Check" : f.exc_type}</b>
              <span>{f.message}</span>
            </div>
          )}
          {f.expected !== null && (
            <div className="fail-row">
              <b>Expected</b>
              <code>{f.expected}</code>
            </div>
          )}
          {f.got !== null && (
            <div className="fail-row">
              <b>You got</b>
              <code>{f.got}</code>
            </div>
          )}
          {f.line !== null && (
            <div className="fail-row">
              <b>Your code</b>
              <span>
                line {f.line}: <code>{f.source}</code>
              </span>
            </div>
          )}
          {f.hint && <div className="fail-hint">{f.hint}</div>}
        </div>
      ))}
    </>
  );
}
