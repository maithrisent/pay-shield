import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function KycUpload() {
  const [formData, setFormData] = useState({
    legal_name: "",
    aadhaar_number: "",
    pan_number: "",
    document_url: "",
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

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

    try {
      await client.post("/compliance/kyc/upload", {
        legal_name: formData.legal_name,
        aadhaar_number: formData.aadhaar_number,
        pan_number: formData.pan_number,
        document_url: formData.document_url,
      });

      setSuccess(true);
      setTimeout(() => {
        navigate("/wallet");
      }, 2000);
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
        setErrors({ general: data.detail || "Failed to upload KYC documents." });
      } else if (status === 401) {
        setErrors({ general: "Your session has expired. Please log in again." });
      } else {
        setErrors({ general: "Something went wrong. Please try again." });
      }
    } finally {
      setLoading(false);
    }
  }

  if (success) {
    return (
      <div className="min-h-screen bg-ink flex items-center justify-center px-4">
        <div className="bg-paper rounded-lg border border-white/5 p-8 max-w-md w-full text-center">
          <div className="w-12 h-12 bg-signal/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-6 h-6 text-signal"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-ink mb-2">
            KYC Submitted Successfully
          </h2>
          <p className="text-sm text-muted mb-6">
            Your KYC documents are under review. Redirecting to wallet...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-ink flex items-center justify-center px-4 py-8">
      <div className="bg-paper rounded-lg border border-white/5 p-8 max-w-md w-full">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-ink mb-1">Complete Your KYC</h1>
          <p className="text-sm text-ink/70">
            Provide your personal and identity information for verification.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Legal Name */}
          <div>
            <label htmlFor="legal_name" className="block text-sm text-ink mb-1.5">
              Legal Name
            </label>
            <input
              id="legal_name"
              name="legal_name"
              type="text"
              value={formData.legal_name}
              onChange={handleChange}
              placeholder="John Doe"
              required
              className={`w-full rounded-lg border px-4 py-2.5 text-ink placeholder:text-ink/40 focus:outline-none focus:ring-2 ${
                errors.legal_name
                  ? "border-alert focus:ring-alert/40"
                  : "border-ink/10 focus:ring-signal/40"
              }`}
            />
            {errors.legal_name && (
              <p className="text-xs text-alert mt-1">{errors.legal_name}</p>
            )}
          </div>

          {/* Aadhaar Number */}
          <div>
            <label htmlFor="aadhaar_number" className="block text-sm text-ink mb-1.5">
              Aadhaar Number
            </label>
            <input
              id="aadhaar_number"
              name="aadhaar_number"
              type="text"
              value={formData.aadhaar_number}
              onChange={handleChange}
              placeholder="123456789012"
              inputMode="numeric"
              required
              className={`w-full rounded-lg border px-4 py-2.5 font-mono text-ink placeholder:text-ink/40 focus:outline-none focus:ring-2 ${
                errors.aadhaar_number
                  ? "border-alert focus:ring-alert/40"
                  : "border-ink/10 focus:ring-signal/40"
              }`}
            />
            {errors.aadhaar_number && (
              <p className="text-xs text-alert mt-1">{errors.aadhaar_number}</p>
            )}
          </div>

          {/* PAN Number */}
          <div>
            <label htmlFor="pan_number" className="block text-sm text-ink mb-1.5">
              PAN Number
            </label>
            <input
              id="pan_number"
              name="pan_number"
              type="text"
              value={formData.pan_number}
              onChange={handleChange}
              placeholder="ABCDE1234F"
              className={`w-full rounded-lg border px-4 py-2.5 font-mono text-ink placeholder:text-ink/40 focus:outline-none focus:ring-2 ${
                errors.pan_number
                  ? "border-alert focus:ring-alert/40"
                  : "border-ink/10 focus:ring-signal/40"
              }`}
              required
            />
            {errors.pan_number && (
              <p className="text-xs text-alert mt-1">{errors.pan_number}</p>
            )}
          </div>

          {/* Document URL */}
          <div>
            <label htmlFor="document_url" className="block text-sm text-ink mb-1.5">
              Document URL
            </label>
            <input
              id="document_url"
              name="document_url"
              type="url"
              value={formData.document_url}
              onChange={handleChange}
              placeholder="https://..."
              required
              className={`w-full rounded-lg border px-4 py-2.5 text-ink placeholder:text-ink/40 focus:outline-none focus:ring-2 ${
                errors.document_url
                  ? "border-alert focus:ring-alert/40"
                  : "border-ink/10 focus:ring-signal/40"
              }`}
            />
            {errors.document_url && (
              <p className="text-xs text-alert mt-1">{errors.document_url}</p>
            )}
          </div>

          {/* General Error */}
          {errors.general && (
            <div className="bg-alert/10 border border-alert rounded-lg px-4 py-3">
              <p className="text-sm text-alert">{errors.general}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-signal text-ink hover:bg-signal/90 disabled:bg-muted disabled:cursor-not-allowed font-medium py-2 px-4 rounded-lg transition-colors text-sm"
          >
            {loading ? "Uploading..." : "Submit KYC"}
          </button>
        </form>

        <p className="text-xs text-muted text-center mt-6">
          Your information is encrypted and securely stored.
        </p>
      </div>
    </div>
  );
}
