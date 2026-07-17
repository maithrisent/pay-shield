return (
  <div className="min-h-screen bg-ink px-4 py-10">
    <div className="mx-auto w-full max-w-[400px]">
      <div className="flex items-center justify-between">
        <p className="font-mono text-[11px] uppercase tracking-widest text-signal">
          Payshield
        </p>
        <button
          onClick={handleLogout}
          className="text-xs text-white/50 hover:text-white"
        >
          Log out
        </button>
      </div>

      <div className="mt-6 rounded-2xl bg-paper p-6 shadow-2xl">
        <p className="text-sm text-muted">Your balance</p>

        {error && <p className="mt-4 text-sm text-alert">{error}</p>}

        {!error && balance === null && (
          <p className="mt-4 font-mono text-3xl text-ink/30">Loading…</p>
        )}

        {balance !== null && (
          <p className="mt-2 font-mono text-4xl font-semibold text-ink">
            ₹
            {balance.balance_rupees.toLocaleString("en-IN", {
              minimumFractionDigits: 2,
            })}
          </p>
        )}
      </div>

      {/* Action buttons */}
      <div className="mt-6 flex gap-3">
        <button
          onClick={() => navigate("/get-paid")}
          className="flex-1 rounded-lg border border-signal/40 py-2 text-sm font-semibold text-signal"
        >
          Get paid
        </button>
        <button
          onClick={() => navigate("/pay")}
          className="flex-1 rounded-lg bg-signal py-2 text-sm font-semibold text-ink"
        >
          Send money
        </button>
      </div>
    </div>
  </div>
);