import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import client from "../api/client";

export default function PayConfirm() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!state) {
    navigate("/pay", { replace: true });
    return null;
  }

  const { aliasString, amountPaise } = state;

  async function handleConfirm() {
    setError("");
    setLoading(true);
    try {
      const res = await client.post("/transactions/pay-by-alias", {
        alias_string: aliasString,
        amount_paise: amountPaise,
      });
      navigate("/pay/success", { state: res.data });
    } catch (err) {
      setError(err.response?.data?.detail || "Payment failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-ink px-4 py-10">
      <div className="mx-auto w-full max-w-[400px]">
        <p className="font-mono text-[11px] uppercase tracking-widest text-signal">
          Confirm payment
        </p>

        <div className="mt-6 rounded-2xl bg-paper p-6 shadow-2xl">
          <p className="text-sm text-muted">Paying</p>
          <p className="mt-1 font-mono text-lg text-ink">{aliasString}</p>

          <p className="mt-4 text-sm text-muted">Amount</p>
          <p className="mt-1 font-mono text-3xl font-semibold text-ink">
            ₹{(amountPaise / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </p>

          <p className="mt-4 text-xs text-white/40">
            You won't see this person's name — that's the point. Double-check the
            alias before confirming.
          </p>

          {error && <p className="mt-4 text-sm text-alert">{error}</p>}

          <button
            onClick={handleConfirm}
            disabled={loading}
            className="mt-6 w-full rounded-lg bg-signal py-2 font-semibold text-ink disabled:opacity-50"
          >
            {loading ? "Sending…" : "Confirm and pay"}
          </button>
        </div>
      </div>
    </div>
  );
}