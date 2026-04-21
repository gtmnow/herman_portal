import { FormEvent, useEffect, useMemo, useState } from "react";
import { PortalCard } from "../components/PortalCard";
import {
  acceptInvitation,
  buildTenantAwarePath,
  fetchInvitation,
  getTenantQueryValue,
  type InvitationPreviewPayload,
} from "../lib/api";

const DEFAULT_INVITE_STATE: InvitationPreviewPayload = {
  status: "loading",
  email: null,
  tenant_id: null,
  logo_url: null,
  welcome_message: "Welcome to Herman Prompt. Please login to begin.",
  error: null,
};

export function InvitePage() {
  const searchParams = useMemo(() => new URLSearchParams(window.location.search), []);
  const token = useMemo(() => searchParams.get("token") ?? "", [searchParams]);
  const tenantId = getTenantQueryValue(searchParams);
  const tenantParamName = searchParams.get("tenant") ? "tenant" : "tenant_id";
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [invitation, setInvitation] = useState<InvitationPreviewPayload>(DEFAULT_INVITE_STATE);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    if (!token) {
      setInvitation({
        ...DEFAULT_INVITE_STATE,
        status: "invalid",
        error: "Missing invitation token.",
      });
      return undefined;
    }

    fetchInvitation(token)
      .then((payload) => {
        if (!cancelled) {
          setInvitation(payload);
        }
      })
      .catch((loadError) => {
        if (!cancelled) {
          setInvitation({
            ...DEFAULT_INVITE_STATE,
            status: "invalid",
            error: loadError instanceof Error ? loadError.message : "Unable to load invitation.",
          });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    if (!token) {
      setError("Missing invitation token.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      const payload = await acceptInvitation(token, password);
      window.location.href = payload.redirect_url;
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to accept invitation.");
    } finally {
      setLoading(false);
    }
  }

  const isLoading = invitation.status === "loading";
  const invalidState = !isLoading && invitation.status !== "ready";

  return (
    <PortalCard
      eyebrow="Invitation"
      title={invitation.welcome_message}
      supporting={
        isLoading
          ? "Checking your invitation and loading the correct tenant branding."
          : invalidState
          ? "This invitation cannot be used. If you expected access, ask your admin for a new invite."
          : "Set your initial password to activate your portal access and continue into Herman Prompt."
      }
      logoUrl={invitation.logo_url}
    >
      {invitation.email ? <p className="invite-email">Invited email: {invitation.email}</p> : null}
      {invitation.error ? <div className="error-banner">{invitation.error}</div> : null}
      {isLoading ? (
        <div className="supporting">Loading invitation details...</div>
      ) : invalidState ? (
        <a
          className="text-link"
          href={buildTenantAwarePath("/login", tenantId ?? invitation.tenant_id, tenantParamName)}
        >
          Back to login
        </a>
      ) : (
        <>
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
            <button className="primary-button" type="submit" disabled={loading}>
              {loading ? "Activating..." : "Set password and continue"}
            </button>
          </form>
          <a
            className="text-link"
            href={buildTenantAwarePath("/login", tenantId ?? invitation.tenant_id, tenantParamName)}
          >
            Back to login
          </a>
        </>
      )}
    </PortalCard>
  );
}
