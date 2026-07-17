import { useLocation, useNavigate } from "react-router-dom";

export default function PaySuccess() {
  const { state } = useLocation();
  const navigate = useNavigate();

  if (!state) {
    navigate("/wallet", { replace: true });
    return null;
  }

  const { transaction_id, amount_paise, status } = state;

  return (
    <div className="min-h-screen bg-ink px-4 py-10">
      <div className="mx-auto w-full max-w-[400px] text-center">
        <div className="mt-6 rounded-2xl bg-paper p-6 shadow-2xl">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-signal/10 text-signal">
            ✓
          </div>
          <p className="mt-4 font-display text-2xl font-semibold text-ink">
            Payment {status}
          </p>
          <p className="mt-1 font-mono text-3xl font-semibold text-ink">
            ₹{(amount_paise / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </p>
          <p className="mt-4 text-xs text-muted">
            Transaction ID: {transaction_id}
          </p>

          <button
            onClick={() => navigate("/wallet")}
            className="mt-6 w-full rounded-lg bg-signal py-2 font-semibold text-ink"
          >
            Back to wallet
          </button>
        </div>
      </div>
    </div>
  );
}