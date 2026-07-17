import { useState } from "react";
import client from "../api/client";

export default function GetPaid() {
  const [phone, setPhone] = useState("");
  const [alias, setAlias] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleGenerate(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await client.post("/alias/generate", {
        counterparty_phone: phone,
      });
      setAlias(res.data.alias_string);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Couldn't generate an alias for that number."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleCopy() {
    navigator.clipboard.writeText(alias);
  }

  return (
    <div className="min-h-screen bg-ink px-4 py-10">
      <div className="mx-auto w-full max-w-[400px]">
        <p className="font-mono text-[11px] uppercase tracking-widest text-signal">
          Payshield
        </p>

        <div className="mt-6 rounded-2xl bg-paper p-6 shadow-2xl">
          <p className="font-display text-2xl font-semibold text-ink">Get paid</p>
          <p className="mt-1 text-sm text-muted">
            Share an alias instead of your phone number.
          </p>

          <form onSubmit={handleGenerate} className="mt-6">
            <label className="text-sm text-muted">Payer's phone number</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="mt-1 w-full rounded-lg border border-ink/10 px-3 py-2 text-ink"
              placeholder="9900000001"
              required
            />
            <button
              type="submit"
              disabled={loading}
              className="mt-4 w-full rounded-lg bg-signal py-2 font-semibold text-ink disabled:opacity-50"
            >
              {loading ? "Generating…" : "Generate alias"}
            </button>
          </form>

          {error && <p className="mt-4 text-sm text-alert">{error}</p>}

          {alias && (
            <div className="mt-6 rounded-xl border border-signal/40 bg-signal/10 p-4">
              <p className="text-[11px] uppercase tracking-wider text-muted">
                Share this alias
              </p>
              <div className="mt-2 flex items-center justify-between gap-2">
                <span className="font-mono text-sm text-ink">{alias}</span>
                <button
                  onClick={handleCopy}
                  className="text-xs text-signal hover:underline"
                >
                  Copy
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}