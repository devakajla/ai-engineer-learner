/** Learner logo: an "L" built as rising steps (learning step by step) with a spark at the top. */
export function LogoMark({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden className="logo-mark">
      <defs>
        <linearGradient id="learner-g" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#34d399" />
          <stop offset="1" stopColor="#047857" />
        </linearGradient>
      </defs>
      <rect width="32" height="32" rx="8" fill="url(#learner-g)" />
      {/* the L: a vertical stem that ends in two rising steps */}
      <path
        d="M9 7.5v16h5.5v-3.5H19v-3.5h4"
        fill="none"
        stroke="#fff"
        strokeWidth="2.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* spark: the "aha" moment */}
      <path d="M22.5 7l.9 2.2 2.2.9-2.2.9-.9 2.2-.9-2.2-2.2-.9 2.2-.9z" fill="#fff" />
    </svg>
  );
}

export default function Logo() {
  return (
    <span className="logo">
      <LogoMark />
      <span className="logo-word">
        Learn<span>er</span>
      </span>
    </span>
  );
}
