import { useEffect, useState } from "react";
import { PortalCard } from "../components/PortalCard";
import {
  launchAdmin,
  buildTenantAwarePath,
  fetchApps,
  fetchBranding,
  getTenantQueryValue,
  launchPrompt,
  logout,
  requestAdminMfa,
  verifyAdminMfa,
  type AppDescriptor,
  type AdminMfaRequestResponse,
  type BrandingPayload,
} from "../lib/api";

const DEFAULT_WELCOME_MESSAGE = "Choose a Herman app to continue.";

export function AppsPage() {
  const searchParams = new URLSearchParams(window.location.search);
  const tenantId = getTenantQueryValue(searchParams);
  const tenantParamName = searchParams.get("tenant") ? "tenant" : "tenant_id";
  const [apps, setApps] = useState<AppDescriptor[]>([]);
  const [loading, setLoading] = useState(true);
  const [launchingPrompt, setLaunchingPrompt] = useState(false);
  const [requestingAdminMfa, setRequestingAdminMfa] = useState(false);
  const [verifyingAdminMfa, setVerifyingAdminMfa] = useState(false);
  const [launchingAdmin, setLaunchingAdmin] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);
  const [adminCode, setAdminCode] = useState("");
  const [adminMfaState, setAdminMfaState] = useState<AdminMfaRequestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [adminMessage, setAdminMessage] = useState<string | null>(null);
  const [branding, setBranding] = useState<BrandingPayload>({
    welcome_message: DEFAULT_WELCOME_MESSAGE,
    logo_url: null,
    tenant_id: tenantId,
    portal_base_url: null,
  });

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const appsPayload = await fetchApps();
        if (cancelled) {
          return;
        }

        setApps(appsPayload.apps);

        const brandingPayload = await fetchBranding(
          tenantId ?? appsPayload.user.tenant_id ?? undefined,
          tenantParamName,
        ).catch(() => null);
        if (!cancelled && brandingPayload) {
          setBranding(brandingPayload);
        }
      } catch (loadError) {
        if (!cancelled) {
          const message = loadError instanceof Error ? loadError.message : "Unable to load apps.";
          if (message === "Authentication required.") {
            window.location.href = buildTenantAwarePath("/login", tenantId, tenantParamName);
            return;
          }
          setError(message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, [tenantId, tenantParamName]);

  async function handlePromptLaunch() {
    setLaunchingPrompt(true);
    setError(null);
    try {
      const payload = await launchPrompt();
      window.location.href = payload.redirect_url;
    } catch (launchError) {
      setError(launchError instanceof Error ? launchError.message : "Unable to launch Herman Prompt.");
    } finally {
      setLaunchingPrompt(false);
    }
  }

  async function handleAdminMfaRequest() {
    setRequestingAdminMfa(true);
    setError(null);
    setAdminMessage(null);
    setAdminCode("");
    try {
      const payload = await requestAdminMfa();
      setAdminMfaState(payload);
      setAdminMessage("We sent a verification code to your email. Enter it below to continue into Herman Admin.");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to send Admin verification code.");
    } finally {
      setRequestingAdminMfa(false);
    }
  }

  async function handleAdminVerifyAndLaunch() {
    setVerifyingAdminMfa(true);
    setError(null);
    setAdminMessage(null);
    try {
      await verifyAdminMfa(adminCode);
      setLaunchingAdmin(true);
      const payload = await launchAdmin();
      window.location.href = payload.redirect_url;
    } catch (verifyError) {
      setError(verifyError instanceof Error ? verifyError.message : "Unable to launch Herman Admin.");
    } finally {
      setVerifyingAdminMfa(false);
      setLaunchingAdmin(false);
    }
  }

  async function handleLogout() {
    setLoggingOut(true);
    setError(null);
    try {
      await logout();
      window.location.href = buildTenantAwarePath("/login", tenantId, tenantParamName);
    } catch (logoutError) {
      setError(logoutError instanceof Error ? logoutError.message : "Unable to log out.");
    } finally {
      setLoggingOut(false);
    }
  }

  return (
    <PortalCard
      eyebrow="Available Apps"
      title={branding.welcome_message}
      supporting="Your portal session is active. Choose where you want to go next."
      logoUrl={branding.logo_url}
    >
      <div className="stack">
        {loading ? <p className="supporting">Loading your available apps.</p> : null}
        {error ? <div className="error-banner">{error}</div> : null}
        {!loading ? (
          <div className="apps-grid">
            {apps.map((app) => (
              <section className="app-tile" key={app.app_key}>
                <div className="app-tile-copy">
                  <h2>{app.label}</h2>
                  <p>{app.description}</p>
                </div>
                {app.app_key === "herman_prompt" ? (
                  <button
                    className="primary-button"
                    type="button"
                    onClick={handlePromptLaunch}
                    disabled={!app.enabled || launchingPrompt}
                  >
                    {launchingPrompt ? "Opening..." : "Open Herman Prompt"}
                  </button>
                ) : app.enabled ? (
                  <div className="stack compact-stack">
                    {!adminMfaState ? (
                      <button
                        className="secondary-button"
                        type="button"
                        onClick={handleAdminMfaRequest}
                        disabled={requestingAdminMfa}
                      >
                        {requestingAdminMfa ? "Sending code..." : "Open Herman Admin"}
                      </button>
                    ) : (
                      <>
                        {adminMessage ? <div className="success-banner">{adminMessage}</div> : null}
                        {adminMfaState.dev_code ? (
                          <div className="success-banner">
                            Dev verification code: <strong>{adminMfaState.dev_code}</strong>
                          </div>
                        ) : null}
                        <label className="field">
                          <span>Verification code</span>
                          <input
                            inputMode="numeric"
                            pattern="[0-9]*"
                            value={adminCode}
                            onChange={(event) => setAdminCode(event.target.value)}
                            placeholder="Enter the email code"
                            required
                          />
                        </label>
                        <div className="app-actions-row">
                          <button
                            className="primary-button"
                            type="button"
                            onClick={handleAdminVerifyAndLaunch}
                            disabled={!adminCode.trim() || verifyingAdminMfa || launchingAdmin}
                          >
                            {verifyingAdminMfa || launchingAdmin ? "Launching..." : "Verify and launch"}
                          </button>
                          <button
                            className="text-button"
                            type="button"
                            onClick={handleAdminMfaRequest}
                            disabled={requestingAdminMfa}
                          >
                            {requestingAdminMfa ? "Resending..." : "Resend code"}
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                ) : (
                  <button className="secondary-button" type="button" disabled>
                    Not available
                  </button>
                )}
              </section>
            ))}
          </div>
        ) : null}
        <button className="text-button" type="button" onClick={handleLogout} disabled={loggingOut}>
          {loggingOut ? "Signing out..." : "Sign out"}
        </button>
      </div>
    </PortalCard>
  );
}
