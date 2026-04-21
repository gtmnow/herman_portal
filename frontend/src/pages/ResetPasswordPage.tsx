import { FormEvent, useMemo, useState } from "react";
import { PortalCard } from "../components/PortalCard";
import { buildTenantAwarePath, getTenantQueryValue, resetPassword } from "../lib/api";


export function ResetPasswordPage() {
  const token = useMemo(() => new URLSearchParams(window.location.search).get("token") ?? "", []);
  const searchParams = new URLSearchParams(window.location.search);
  const tenantId = getTenantQueryValue(searchParams);
  const tenantParamName = searchParams.get("tenant") ? "tenant" : "tenant_id";
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    if (!token) {
      setError("Missing reset token.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await resetPassword(token, password);
      setSuccess("Your password has been reset. You can return to login now.");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to reset password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <PortalCard
      eyebrow="Password Reset"
      title="Create a new password"
      supporting="Choose a new password for your Herman Portal account."
    >
        <form className="stack" onSubmit={handleSubmit}>
          <label className="field">
            <span>New password</span>
            <input
              autoComplete="new-password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter a new password"
              required
            />
          </label>
          <label className="field">
            <span>Confirm password</span>
            <input
              autoComplete="new-password"
              type="password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              placeholder="Confirm your new password"
              required
            />
          </label>
          {error ? <div className="error-banner">{error}</div> : null}
          {success ? <div className="success-banner">{success}</div> : null}
          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? "Resetting..." : "Reset password"}
          </button>
        </form>
        <a className="text-link" href={buildTenantAwarePath("/login", tenantId, tenantParamName)}>
          Back to login
        </a>
    </PortalCard>
  );
}
