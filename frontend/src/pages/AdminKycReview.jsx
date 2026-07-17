import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function AdminKycReview() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [processingId, setProcessingId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPendingKyc();
  }, []);

  async function fetchPendingKyc() {
    setLoading(true);
    setError("");
    try {
      const response = await client.get("/compliance/admin/kyc/pending");
      setRecords(response.data.records || []);
    } catch (err) {
      const status = err.response?.status;
      const data = err.response?.data;

      if (status === 401) {
        setError("Your session has expired. Please log in again.");
      } else if (status === 403) {
        setError("You do not have permission to view this page.");
      } else {
        setError(data?.detail || "Failed to load pending KYC records.");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleApprove(record) {
    setProcessingId(record.id);
    try {
      await client.post(`/compliance/admin/kyc/${record.user_id}/approve`);
      setSuccessMessage(`KYC approved for ${record.legal_name}`);
      setRecords(records.filter((r) => r.id !== record.id));
      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (err) {
      const status = err.response?.status;
      const data = err.response?.data;

      if (status === 401) {
        setError("Your session has expired. Please log in again.");
      } else if (status === 403) {
        setError("You do not have permission to approve KYC.");
      } else if (status === 404) {
        setError("KYC record not found for this user.");
      } else {
        setError(data?.detail || "Failed to approve KYC.");
      }
      setProcessingId(null);
    }
  }

  async function handleReject(record) {
    setProcessingId(record.id);
    try {
      await client.post(`/compliance/admin/kyc/${record.user_id}/reject`);
      setSuccessMessage(`KYC rejected for ${record.legal_name}`);
      setRecords(records.filter((r) => r.id !== record.id));
      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (err) {
      const status = err.response?.status;
      const data = err.response?.data;

      if (status === 401) {
        setError("Your session has expired. Please log in again.");
      } else if (status === 403) {
        setError("You do not have permission to reject KYC.");
      } else if (status === 404) {
        setError("KYC record not found for this user.");
      } else {
        setError(data?.detail || "Failed to reject KYC.");
      }
      setProcessingId(null);
    }
  }

  return (
    <div className="min-h-screen bg-ink px-4 py-8">
      <div className="mx-auto w-full max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-semibold text-ink">KYC Review</h1>
            <button
              onClick={() => navigate("/wallet")}
              className="text-sm text-ink/60 hover:text-ink transition-colors"
            >
              ← Back
            </button>
          </div>
          <p className="text-sm text-ink/70 mt-2">
            Review and approve pending KYC applications
          </p>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="mb-4 rounded-lg bg-signal/20 border border-signal/40 p-4">
            <p className="text-sm text-signal">{successMessage}</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-4 rounded-lg bg-alert/10 border border-alert/30 p-4">
            <p className="text-sm text-alert">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="rounded-lg bg-paper p-6 animate-pulse"
              >
                <div className="h-8 w-40 bg-ink/10 rounded mb-4" />
                <div className="space-y-2">
                  <div className="h-4 w-3/4 bg-ink/10 rounded" />
                  <div className="h-4 w-1/2 bg-ink/10 rounded" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* No Records */}
        {!loading && records.length === 0 && !error && (
          <div className="rounded-lg bg-paper p-8 text-center">
            <p className="text-sm text-ink/60">No pending KYC applications</p>
          </div>
        )}

        {/* KYC Records */}
        {!loading && records.length > 0 && (
          <div className="space-y-4">
            {records.map((record) => (
              <div
                key={record.id}
                className="rounded-lg bg-paper p-6 border border-white/5"
              >
                <div className="mb-4 pb-4 border-b border-ink/10">
                  <h2 className="text-lg font-semibold text-ink">
                    {record.legal_name}
                  </h2>
                  <p className="text-xs text-ink/60 mt-1">
                    User ID: {record.user_id}
                  </p>
                  <p className="text-xs text-ink/60">
                    Submitted: {new Date(record.created_at).toLocaleDateString()}
                  </p>
                </div>

                <div className="space-y-3 mb-6">
                  <div className="flex justify-between">
                    <span className="text-sm text-ink/70">Aadhaar</span>
                    <span className="text-sm font-mono text-ink">
                      {record.aadhaar_number}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-ink/70">PAN</span>
                    <span className="text-sm font-mono text-ink">
                      {record.pan_number}
                    </span>
                  </div>
                  <div className="flex justify-between items-start">
                    <span className="text-sm text-ink/70">Document</span>
                    <a
                      href={record.document_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-signal hover:text-signal/80 transition-colors"
                    >
                      View Document →
                    </a>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => handleApprove(record)}
                    disabled={processingId === record.id}
                    className="flex-1 bg-signal text-ink hover:bg-signal/90 disabled:bg-muted disabled:cursor-not-allowed font-medium py-2 px-4 rounded-lg transition-colors text-sm"
                  >
                    {processingId === record.id ? "Processing..." : "Approve"}
                  </button>
                  <button
                    onClick={() => handleReject(record)}
                    disabled={processingId === record.id}
                    className="flex-1 bg-ink border border-white/10 text-paper hover:bg-ink/80 disabled:opacity-50 disabled:cursor-not-allowed font-medium py-2 px-4 rounded-lg transition-colors text-sm"
                  >
                    {processingId === record.id ? "Processing..." : "Reject"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
