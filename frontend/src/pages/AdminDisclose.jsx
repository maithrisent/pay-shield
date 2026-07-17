import { useState } from "react";
import client from "../api/client";

export default function AdminDisclose() {
  const [formData, setFormData] = useState({
    alias: "",
    reason: "",
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [disclosedIdentity, setDisclosedIdentity] = useState(null);

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setErrors({});
    setLoading(true);
    setDisclosedIdentity(null);

    try {
      const response = await client.post("/compliance/disclose", {
        alias: formData.alias,
        reason: formData.reason,
      });

      setDisclosedIdentity(response.data);
      setFormData({ alias: "", reason: "" });
    } catch (err) {
      const status = err.response?.status;
      const data = err.response?.data;

      if (status === 422) {
        // Validation error
        const validationErrors = {};
        if (data.detail && Array.isArray(data.detail)) {
          data.detail.forEach((detail) => {
            const field = detail.loc?.[1];
            if (field) {
              validationErrors[field] = detail.msg;
            }
          });
        }
        setErrors(validationErrors);
      } else if (status === 400) {
        setErrors({ general: data.detail || "Failed to disclose identity." });
      } else if (status === 401) {
        setErrors({ general: "Your session has expired. Please log in again." });
      } else if (status === 403) {
        setErrors({ general: "You do not have permission to perform this action." });
      } else if (status === 404) {
        setErrors({ general: "Alias not found or user has no verified KYC." });
      } else {
        setErrors({ general: "Something went wrong. Please try again." });
      }
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setDisclosedIdentity(null);
    setFormData({ alias: "", reason: "" });
    setErrors({});
  }

  return (
    <div className="min-h-screen bg-ink flex items-center justify-center px-4 py-8">
      <div className="bg-paper rounded-lg border border-white/5 p-8 max-w-md w-full">
        <h1 className="text-2xl font-semibold text-ink mb-2">Identity Disclosure</h1>
        <p className="text-sm text-ink/70 mb-6">
          Request user identity information. All actions are logged for audit purposes.
        </p>

        {disclosedIdentity ? (
          <div className="space-y-6">
            <div className="bg-signal/10 border border-signal/30 rounded-lg p-6">
              <h2 className="text-sm font-semibold text-ink mb-4">Disclosed Identity</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-ink mb-1">
                    Legal Name
                  </label>
                  <p className="text-sm font-mono bg-ink/30 border border-white/10 rounded px-3 py-2 text-paper">
                    {disclosedIdentity.legal_name}
                  </p>
                </div>

                <div>
                  <label className="block text-xs font-medium text-ink mb-1">
                    Aadhaar Number
                  </label>
                  <p className="text-sm font-mono bg-ink/30 border border-white/10 rounded px-3 py-2 text-paper">
                    {disclosedIdentity.aadhaar_number}
                  </p>
                </div>

                <div>
                  <label className="block text-xs font-medium text-ink mb-1">
                    PAN Number
                  </label>
                  <p className="text-sm font-mono bg-ink/30 border border-white/10 rounded px-3 py-2 text-paper">
                    {disclosedIdentity.pan_number}
                  </p>
                </div>
              </div>
            </div>

            <button
              onClick={handleReset}
              className="w-full bg-ink border border-white/10 text-paper hover:bg-ink/80 font-medium py-2 px-4 rounded-lg transition-colors text-sm"
            >
              Disclose Another
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {errors.general && (
              <div className="bg-alert/10 border border-alert/30 rounded-lg p-3">
                <p className="text-sm text-alert">{errors.general}</p>
              </div>
            )}

            <div>
              <label htmlFor="alias" className="block text-xs font-medium text-ink mb-1">
                Alias <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="alias"
                name="alias"
                value={formData.alias}
                onChange={handleChange}
                placeholder="e.g., @johndoe"
                className={`w-full px-3 py-2 text-sm border rounded-lg text-ink placeholder:text-ink/40 focus:outline-none focus:ring-2 focus:ring-offset-0 transition-all ${
                  errors.alias
                    ? "border-alert focus:ring-alert/40"
                    : "border-ink/10 focus:ring-signal/40"
                }`}
                disabled={loading}
              />
              {errors.alias && (
                <p className="text-xs text-alert mt-1">{errors.alias}</p>
              )}
            </div>

            <div>
              <label htmlFor="reason" className="block text-xs font-medium text-ink mb-1">
                Reason for Disclosure <span className="text-red-500">*</span>
              </label>
              <textarea
                id="reason"
                name="reason"
                value={formData.reason}
                onChange={handleChange}
                placeholder="Explain the reason for requesting this information"
                rows="3"
                className={`w-full px-3 py-2 text-sm border rounded-lg text-ink placeholder:text-ink/40 focus:outline-none focus:ring-2 focus:ring-offset-0 transition-all ${
                  errors.reason
                    ? "border-alert focus:ring-alert/40"
                    : "border-ink/10 focus:ring-signal/40"
                }`}
                disabled={loading}
              />
              {errors.reason && (
                <p className="text-xs text-alert mt-1">{errors.reason}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-signal text-ink hover:bg-signal/90 disabled:bg-muted disabled:cursor-not-allowed font-medium py-2 px-4 rounded-lg transition-colors text-sm"
            >
              {loading ? "Revealing..." : "Reveal Identity"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
