import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function Wallet() {
  const [balance, setBalance] = useState(null);
  const [kycStatus, setKycStatus] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    client
      .get("/wallet/balance")
      .then((res) => setBalance(res.data))
      .catch(() => setError("Couldn't load your balance."));

    client
      .get("/compliance/kyc/status")
      .then((res) => setKycStatus(res.data.status))
      .catch(() => setKycStatus("unknown"));
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

        <div className="mt-4 rounded-2xl bg-paper p-6">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted">KYC Verification</p>
            <span className={`text-xs font-semibold px-2 py-1 rounded ${
              kycStatus === "verified"
                ? "bg-signal/20 text-signal"
                : kycStatus === "pending"
                ? "bg-white/10 text-ink/60"
                : "bg-alert/10 text-alert"
            }`}>
              {kycStatus === "verified" ? "Verified" : kycStatus === "pending" ? "Pending" : "Not Submitted"}
            </span>
          </div>
          <button
            onClick={() => navigate("/kyc")}
            className="w-full bg-signal text-ink hover:bg-signal/90 font-medium py-2 px-4 rounded-lg transition-colors text-sm"
          >
            {kycStatus === "verified" ? "Update KYC" : "Complete KYC"}
          </button>
        </div>
      </div>
    </div>
  );
}