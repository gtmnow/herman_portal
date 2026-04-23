const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8010";
const SESSION_FETCH_OPTIONS: RequestInit = {
  credentials: "include",
};

export type BrandingPayload = {
  tenant_id?: string | null;
  logo_url?: string | null;
  welcome_message: string;
  portal_base_url?: string | null;
};

export type InvitationPreviewPayload = {
  status: string;
  email?: string | null;
  tenant_id?: string | null;
  logo_url?: string | null;
  welcome_message: string;
  error?: string | null;
};

export type PortalUserSummary = {
  email: string;
  user_id_hash: string;
  display_name?: string | null;
  tenant_id?: string | null;
};

export type AppDescriptor = {
  app_key: string;
  label: string;
  description: string;
  enabled: boolean;
  launch_mode: string;
  requires_mfa?: boolean | null;
};


export async function login(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    ...SESSION_FETCH_OPTIONS,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(typeof payload.detail === "string" ? payload.detail : "Unable to log in.");
  }

  return payload as { status: string; redirect_path: string; user: PortalUserSummary };
}


export function getTenantQueryValue(searchParams = new URLSearchParams(window.location.search)) {
  return searchParams.get("tenant_id") ?? searchParams.get("tenant");
}


export function buildTenantAwarePath(
  pathname: string,
  tenantValue?: string | null,
  key: "tenant" | "tenant_id" = "tenant",
) {
  if (!tenantValue) {
    return pathname;
  }

  const params = new URLSearchParams();
  params.set(key, tenantValue);
  return `${pathname}?${params.toString()}`;
}


export async function fetchBranding(tenantId?: string | null, tenantParamName: "tenant" | "tenant_id" = "tenant") {
  const params = new URLSearchParams();
  if (tenantId) {
    params.set(tenantParamName, tenantId);
  }

  const response = await fetch(`${API_BASE_URL}/api/auth/branding${params.toString() ? `?${params}` : ""}`, SESSION_FETCH_OPTIONS);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(typeof payload.detail === "string" ? payload.detail : "Unable to load branding.");
  }

  return payload as BrandingPayload;
}


export async function fetchInvitation(token: string) {
  const params = new URLSearchParams({ token });
  const response = await fetch(`${API_BASE_URL}/api/auth/invite?${params}`, SESSION_FETCH_OPTIONS);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(typeof payload.detail === "string" ? payload.detail : "Unable to load invitation.");
  }

  return payload as InvitationPreviewPayload;
}


export async function acceptInvitation(token: string, newPassword: string) {
  const response = await fetch(`${API_BASE_URL}/api/auth/accept-invite`, {
    method: "POST",
    ...SESSION_FETCH_OPTIONS,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password: newPassword }),
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(typeof payload.detail === "string" ? payload.detail : "Unable to accept invitation.");
  }

  return payload as { launch_token: string; redirect_url: string };
}


export async function forgotPassword(email: string) {
  const response = await fetch(`${API_BASE_URL}/api/auth/forgot-password`, {
    method: "POST",
    ...SESSION_FETCH_OPTIONS,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(typeof payload.detail === "string" ? payload.detail : "Unable to request reset.");
  }

  return payload as { status: string; reset_url?: string | null };
}


export async function resetPassword(token: string, newPassword: string) {
  const response = await fetch(`${API_BASE_URL}/api/auth/reset-password`, {
    method: "POST",
    ...SESSION_FETCH_OPTIONS,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password: newPassword }),
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(typeof payload.detail === "string" ? payload.detail : "Unable to reset password.");
  }

  return payload as { status: string };
}


export async function changePassword(email: string, currentPassword: string, newPassword: string) {
  const response = await fetch(`${API_BASE_URL}/api/auth/change-password`, {
    method: "POST",
    ...SESSION_FETCH_OPTIONS,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email,
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(typeof payload.detail === "string" ? payload.detail : "Unable to change password.");
  }

  return payload as { status: string };
}


export async function fetchApps() {
  const response = await fetch(`${API_BASE_URL}/api/auth/apps`, SESSION_FETCH_OPTIONS);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(typeof payload.detail === "string" ? payload.detail : "Unable to load apps.");
  }

  return payload as { user: PortalUserSummary; apps: AppDescriptor[] };
}


export async function launchPrompt() {
  const response = await fetch(`${API_BASE_URL}/api/auth/launch/prompt`, {
    method: "POST",
    ...SESSION_FETCH_OPTIONS,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(typeof payload.detail === "string" ? payload.detail : "Unable to launch Herman Prompt.");
  }

  return payload as { launch_token: string; redirect_url: string };
}


export async function logout() {
  const response = await fetch(`${API_BASE_URL}/api/auth/logout`, {
    method: "POST",
    ...SESSION_FETCH_OPTIONS,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(typeof payload.detail === "string" ? payload.detail : "Unable to log out.");
  }

  return payload as { status: string };
}
