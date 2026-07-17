import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Send, QrCode, History, User, Home, ArrowDownToLine, Gift, Zap } from "lucide-react";
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
    <div className="min-h-screen bg-ink pb-24">
      {/* Top bar */}
      <div className="flex items-center justify-between px-5 pt-8 pb-2">
        <p className="font-display text-lg font-semibold text-paper">
          Payshield
        </p>
        <button
          onClick={handleLogout}
          className="flex h-8 w-8 items-center justify-center rounded-full bg-white/5 text-white/60 hover:text-white"
        >
          <User size={16} />
        </button>
      </div>

      <div className="mx-auto w-full max-w-[400px] px-4">
        {/* Balance card */}
        <div className="mt-4 rounded-3xl bg-paper p-6 shadow-2xl">
          <p className="text-sm text-muted">Your balance</p>

          {error && <p className="mt-4 text-sm text-alert">{error}</p>}

          {!error && balance === null && (
            <div className="mt-3 h-10 w-40 animate-pulse rounded-lg bg-ink/10" />
          )}

          {balance !== null && (
            <p className="mt-2 font-mono text-4xl font-semibold text-ink">
              ₹
              {balance.balance_rupees.toLocaleString("en-IN", {
                minimumFractionDigits: 2,
              })}
            </p>
          )}

          {/* Quick actions — GPay-style circular buttons */}
          <div className="mt-6 flex justify-between px-2">
            <QuickAction
              icon={<Send size={20} />}
              label="Send"
              onClick={() => navigate("/pay")}
              primary
            />
            <QuickAction
              icon={<ArrowDownToLine size={20} />}
              label="Get paid"
              onClick={() => navigate("/get-paid")}
            />
            <QuickAction
              icon={<QrCode size={20} />}
              label="Scan"
              onClick={() => navigate("/scan")}
            />
            <QuickAction
              icon={<History size={20} />}
              label="Activity"
              onClick={() => navigate("/activity")}
            />
          </div>
          <div className="mt-4 flex gap-3 overflow-x-auto pb-1">
          <OvalBadge
    icon={<Gift size={13} />}
    label="Rewards"
    sublabel="2 new"
    tone="signal"
    onClick={() => navigate("/rewards")}
  />
  <OvalBadge
    icon={<Zap size={13} />}
    label="Lite mode"
    sublabel="Enabled"
    tone="default"
    onClick={() => navigate("/lite")}
  />
</div>
        </div>

        {/* Alias identity reminder — reinforces the privacy pitch */}
        <div className="mt-5 rounded-2xl border border-signal/20 bg-signal/5 px-4 py-3">
          <p className="text-xs text-signal">
            Your alias is active. Contacts only see your masked identity when
            you pay.
          </p>
        </div>
      </div>

      {/* Bottom nav */}
      <nav className="fixed inset-x-0 bottom-0 border-t border-white/10 bg-ink/95 backdrop-blur">
        <div className="mx-auto flex max-w-[400px] items-center justify-around py-3">
          <NavItem icon={<Home size={20} />} label="Home" active />
          <NavItem icon={<QrCode size={20} />} label="Scan" />
          <NavItem icon={<History size={20} />} label="Activity" />
          <NavItem icon={<User size={20} />} label="Profile" />
        </div>
      </nav>
    </div>
  );
}

function QuickAction({ icon, label, onClick, primary }) {
  return (
    <button
      onClick={onClick}
      className="flex flex-col items-center gap-2"
    >
      <span
        className={
          "flex h-12 w-12 items-center justify-center rounded-full transition " +
          (primary
            ? "bg-signal text-ink"
            : "bg-ink/5 text-ink hover:bg-ink/10")
        }
      >
        {icon}
      </span>
      <span className="text-[11px] font-medium text-muted">{label}</span>
    </button>
  );
}

function NavItem({ icon, label, active }) {
  return (
    <button
      className={
        "flex flex-col items-center gap-1 " +
        (active ? "text-signal" : "text-white/40 hover:text-white/70")
      }
    >
      {icon}
      <span className="text-[10px] font-medium">{label}</span>
    </button>
  );
}

function OvalBadge({ icon, label, sublabel, tone = "default", onClick }) {
  const tones = {
    default: "bg-ink/5 text-ink",
    signal: "bg-signal/10 text-signal border border-signal/30",
    paper: "bg-paper text-ink",
  };

  return (
    <button
      onClick={onClick}
      className={
        "flex items-center gap-2 rounded-full px-4 py-2 transition hover:brightness-95 " +
        tones[tone]
      }
    >
      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-white/10">
        {icon}
      </span>
      <span className="flex flex-col items-start leading-tight">
        <span className="text-xs font-semibold">{label}</span>
        {sublabel && (
          <span className="text-[10px] opacity-70">{sublabel}</span>
        )}
      </span>
    </button>
  );
}