import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Pay() {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [amount, setAmount] = useState("");
  const navigate = useNavigate();

  function handleContinue(e) {
    e.preventDefault();
    const amountPaise = Math.round(parseFloat(amount) * 100);
    navigate("/pay/confirm", { state: { phoneNumber, amountPaise } });
  }

  return (
    <div className="min-h-screen bg-ink px-4 py-10">
      <div className="mx-auto w-full max-w-[400px]">
        <p className="font-mono text-[11px] uppercase tracking-widest text-signal">
          Payshield
        </p>

        <div className="mt-6 rounded-2xl bg-paper p-6 shadow-2xl">
          <p className="font-display text-2xl font-semibold text-ink">Send money</p>

          <form onSubmit={handleContinue} className="mt-6">
            <label className="text-sm text-muted">Recipient's phone number</label>
            <input
              type="tel"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              className="mt-1 w-full rounded-lg border border-ink/10 px-3 py-2 text-ink"
              placeholder="9900000002"
              required
            />

            <label className="mt-4 block text-sm text-muted">Amount (₹)</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="mt-1 w-full rounded-lg border border-ink/10 px-3 py-2 text-ink"
              placeholder="100.00"
              required
            />

            <button
              type="submit"
              className="mt-6 w-full rounded-lg bg-signal py-2 font-semibold text-ink"
            >
              Continue
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}