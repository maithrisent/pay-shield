import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function Wallet() {
  const [balance, setBalance] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    client
      .get("/wallet/balance")
      .then((res) => setBalance(res.data))
      .catch(() => setError("Couldn't load your balance."));
  }, []);

  function handleLogout() {
    localStorage.removeItem("payshield_token");
    navigate("/login");
  }

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
      </div>
    </div>
  );
}