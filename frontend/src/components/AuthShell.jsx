export default function AuthShell({ eyebrow, title, children, footer }) {
  return (
    <div className="min-h-screen bg-ink flex items-center justify-center px-4 py-10">
      {/* Phone-width frame — keeps every screen looking like a mobile
          app even when viewed in a regular desktop browser, which
          matters for screen-recording the demo. */}
      <div className="w-full max-w-[400px]">
        {/* Signature element: a name being redacted and replaced by an
            alias, shown before you've even logged in — the core idea
            of the product, made visible immediately. */}
        <div className="mb-6 rounded-xl border border-white/10 bg-white/[0.03] p-4">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-white/40">
            <span>Shown to merchant</span>
            <span className="text-signal">● verified</span>
          </div>
          <div className="mt-3 flex items-center gap-3">
            <div className="h-3 w-28 rounded-sm bg-redact" aria-hidden="true" />
            <span className="text-white/30">→</span>
            <span className="rounded-full border border-signal/40 bg-signal/10 px-3 py-1 font-mono text-xs text-signal">
              Guest_4F2A
            </span>
          </div>
        </div>

        <div className="rounded-2xl bg-paper p-6 shadow-2xl">
          <p className="font-mono text-[11px] uppercase tracking-widest text-signal">
            {eyebrow}
          </p>
          <h1 className="mt-1 font-display text-2xl font-semibold text-ink">
            {title}
          </h1>
          <div className="mt-6">{children}</div>
        </div>

        {footer && (
          <p className="mt-5 text-center text-sm text-white/50">{footer}</p>
        )}
      </div>
    </div>
  );
}