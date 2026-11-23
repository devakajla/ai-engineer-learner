"use client";

import { useMemo, useRef, useState } from "react";
import ReactMarkdown, { defaultUrlTransform } from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";
import { API } from "@/lib/api";
import Icon from "./Icon";

/** A code block with a copy button. */
function CodeBlock({ lines, ...props }: React.ComponentProps<"pre"> & { lines?: LineAttrs }) {
  const ref = useRef<HTMLPreElement>(null);
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(ref.current?.innerText ?? "");
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {}
  };
  return (
    <div className="code-block" {...lines}>
      <button className="copy-btn" onClick={copy} title="Copy code">
        <Icon name={copied ? "check" : "copy"} size={13} />
        {copied ? "Copied" : "Copy"}
      </button>
      <pre ref={ref} {...props} />
    </div>
  );
}

type HastNode = {
  type: string;
  value?: string;
  children?: HastNode[];
  position?: { start: { line: number }; end: { line: number } };
};

type LineAttrs = { "data-l1"?: number; "data-l2"?: number };

/** Source line range of a node, as data attributes. The lesson page reads them to tell Claude which lines were selected. */
const lineAttrs = (node?: HastNode): LineAttrs =>
  node?.position ? { "data-l1": node.position.start.line, "data-l2": node.position.end.line } : {};

const textOf = (n?: HastNode): string =>
  n?.type === "text" ? (n.value ?? "") : (n?.children ?? []).map(textOf).join("");

/** "Common mistakes!" -> "common-mistakes", used as the heading id so a doubt can scroll back to it. */
export const headingId = (text: string) =>
  text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

export type Heading = { id: string; text: string };

type StarProps = {
  /** When given, ## and ### headings get a star button to mark a doubt at that spot. */
  onStar?: (heading: Heading) => void;
  /** Heading ids that already have an open doubt (their star is shown filled). */
  starred?: Set<string>;
};

/** Renders lesson / quiz / Claude Markdown with GitHub tables and code highlighting. */
export default function Markdown({
  text,
  inline = false,
  onStar,
  starred,
}: { text: string; inline?: boolean } & StarProps) {
  // Memoised so headings are not remounted on every render of the page.
  const components = useMemo(() => {
    if (inline) return undefined;
    const heading =
      (Tag: "h2" | "h3") =>
      ({ node, children, ...p }: React.ComponentProps<"h2"> & { node?: HastNode }) => {
        const label = textOf(node);
        const id = headingId(label);
        const on = starred?.has(id);
        return (
          <Tag id={id} className={onStar ? "star-heading" : undefined} {...lineAttrs(node)} {...p}>
            {children}
            {onStar && (
              <button
                className={`heading-star ${on ? "on" : ""}`}
                onClick={() => onStar({ id, text: label })}
                title={on ? "You have a doubt here — add another" : "Mark a doubt here to revise later"}
              >
                <Icon name="star" size={16} filled={on} />
              </button>
            )}
          </Tag>
        );
      };
    const block =
      <T extends "p" | "li" | "blockquote" | "table">(Tag: T) =>
      ({ node, ...p }: React.ComponentProps<T> & { node?: HastNode }) => {
        const El = Tag as React.ElementType;
        return <El {...lineAttrs(node)} {...p} />;
      };
    return {
      pre: ({ node, ...p }: { node?: HastNode } & React.ComponentProps<"pre">) => (
        <CodeBlock lines={lineAttrs(node)} {...p} />
      ),
      h2: heading("h2"),
      h3: heading("h3"),
      p: block("p"),
      li: block("li"),
      blockquote: block("blockquote"),
      table: block("table"),
      // Chat screenshots are stored as "/api/chat/image/<name>"; the API lives on another origin.
      img: ({ node, src, alt, ...p }: React.ComponentProps<"img"> & { node?: HastNode }) => {
        const url = typeof src === "string" && src.startsWith("/api/") ? API + src : src;
        // eslint-disable-next-line @next/next/no-img-element
        return <img className="md-img" src={url} alt={alt ?? ""} loading="lazy" {...p} />;
      },
    };
  }, [inline, onStar, starred]);

  return (
    <div className={inline ? "md inline-md" : "md"}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[[rehypeHighlight, { detect: false }]]}
        components={components}
        urlTransform={(url) => (url.startsWith("blob:") ? url : defaultUrlTransform(url))}
      >
        {text}
      </ReactMarkdown>
    </div>
  );
}
