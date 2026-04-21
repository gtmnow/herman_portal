import { FormEvent, useEffect, useState } from "react";
import { PortalCard } from "../components/PortalCard";
import { buildTenantAwarePath, fetchBranding, getTenantQueryValue, type BrandingPayload, login } from "../lib/api";

const DEFAULT_WELCOME_MESSAGE = "Welcome to Herman Prompt. Please login to begin.";

export function LoginPage() {
  const searchParams = new URLSearchParams(window.location.search);
  const tenantId = getTenantQueryValue(searchParams);
  const tenantParamName = searchParams.get("tenant") ? "tenant" : "tenant_id";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [branding, setBranding] = useState<BrandingPayload>({
    welcome_message: DEFAULT_WELCOME_MESSAGE,
    logo_url: null,
    tenant_id: tenantId,
    portal_base_url: null,
  });

  useEffect(() => {
    let cancelled = false;

    fetchBranding(tenantId, tenantParamName)
      .then((payload) => {
        if (!cancelled) {
          setBranding(payload);
        }
      })
      .catch(() => undefined);

    return () => {
      cancelled = true;
    };
  }, [tenantId, tenantParamName]);

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
    <PortalCard
      title={branding.welcome_message}
      supporting={
        tenantId
          ? "Tenant branding is being applied from the shared admin config."
          : "Use your email and password to access the Herman Prompt workspace."
      }
      logoUrl={branding.logo_url}
    >
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
          <a className="text-link" href={buildTenantAwarePath("/forgot-password", tenantId, tenantParamName)}>
            Forgot your password?
          </a>
          <a className="text-link" href={buildTenantAwarePath("/change-password", tenantId, tenantParamName)}>
            Change password
          </a>
        </div>
    </PortalCard>
  );
}
