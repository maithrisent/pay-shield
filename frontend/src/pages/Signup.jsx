import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import client from "../api/client";
import AuthShell from "../components/AuthShell";

export default function Signup() {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await client.post("/auth/signup", {
        phone_number: phoneNumber,
      });
      localStorage.setItem("payshield_token", res.data.token);
      navigate("/wallet");
    } catch (err) {
      if (err.response?.status === 409) {
        setError("An account with this number already exists.");
      } else {
        setError("Something went wrong. Try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell
      eyebrow="Get started"
      title="Create your account"
      footer={
        <>
          Already have an account?{" "}
          <Link to="/login" className="text-signal hover:underline">
            Log in
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="phone" className="block text-sm text-muted mb-1.5">
            Phone number
          </label>
          <input
            id="phone"
            type="tel"
            inputMode="numeric"
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            placeholder="9900000001"
            required
            className="w-full rounded-lg border border-black/10 bg-white px-4 py-2.5 font-mono text-ink placeholder:text-muted/60 focus:outline-none focus:ring-2 focus:ring-signal"
          />
        </div>
        {error && <p className="text-sm text-alert">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-ink py-2.5 font-medium text-paper transition hover:bg-signal disabled:opacity-50"
        >
          {loading ? "Creating account…" : "Create account"}
        </button>
      </form>
    </AuthShell>
  );
}