import { FormEvent, useState } from "react";
import { forgotPassword } from "../lib/api";


export function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const payload = await forgotPassword(email);
      setMessage(
        payload.reset_url
          ? `Reset link generated: ${payload.reset_url}`
          : "If an account exists for that email, a reset link has been prepared.",
      );
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to request reset.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="portal-shell">
      <section className="card">
        <p className="eyebrow">Password Reset</p>
        <h1>Reset your password</h1>
        <p className="supporting">Enter your email and we will prepare a reset link.</p>
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
          {error ? <div className="error-banner">{error}</div> : null}
          {message ? <div className="success-banner">{message}</div> : null}
          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? "Preparing..." : "Send reset link"}
          </button>
        </form>
        <a className="text-link" href="/login">
          Back to login
        </a>
      </section>
    </main>
  );
}
