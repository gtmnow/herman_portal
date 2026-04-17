import { FormEvent, useState } from "react";
import { changePassword } from "../lib/api";


export function ChangePasswordPage() {
  const [email, setEmail] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    if (newPassword !== confirmPassword) {
      setError("New passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await changePassword(email, currentPassword, newPassword);
      setSuccess("Your password has been changed.");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to change password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="portal-shell">
      <section className="card">
        <p className="eyebrow">Account Security</p>
        <h1>Change your password</h1>
        <p className="supporting">
          For the temporary portal, confirm your current password before choosing a new one.
        </p>
        <form className="stack" onSubmit={handleSubmit}>
          <label className="field">
            <span>Email</span>
            <input
              autoComplete="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              required
            />
          </label>
          <label className="field">
            <span>Current password</span>
            <input
              autoComplete="current-password"
              type="password"
              value={currentPassword}
              onChange={(event) => setCurrentPassword(event.target.value)}
              placeholder="Enter your current password"
              required
            />
          </label>
          <label className="field">
            <span>New password</span>
            <input
              autoComplete="new-password"
              type="password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              placeholder="Enter a new password"
              required
            />
          </label>
          <label className="field">
            <span>Confirm new password</span>
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
            {loading ? "Saving..." : "Change password"}
          </button>
        </form>
        <a className="text-link" href="/login">
          Back to login
        </a>
      </section>
    </main>
  );
}
