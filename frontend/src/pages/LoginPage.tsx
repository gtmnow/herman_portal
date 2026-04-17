import { FormEvent, useState } from "react";
import logo from "../../assets/logo.png";
import { login } from "../lib/api";


export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = await login(email, password);
      window.location.href = payload.redirect_url;
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to log in.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="portal-shell">
      <section className="card">
        <img className="portal-logo" src={logo} alt="Herman Prompt" />
        <h1>Welcome to Herman Prompt. Please login to begin.</h1>
        <p className="supporting">
          Use your email and password to access the Herman Prompt workspace.
        </p>
        <form className="stack" onSubmit={handleSubmit}>
          <label className="field">
            <span>Email</span>
            <input
              autoComplete="email"
              name="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              required
            />
          </label>
          <label className="field">
            <span>Password</span>
            <input
              autoComplete="current-password"
              name="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
              required
            />
          </label>
          {error ? <div className="error-banner">{error}</div> : null}
          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
        <div className="link-stack">
          <a className="text-link" href="/forgot-password">
            Forgot your password?
          </a>
          <a className="text-link" href="/change-password">
            Change password
          </a>
        </div>
      </section>
    </main>
  );
}
