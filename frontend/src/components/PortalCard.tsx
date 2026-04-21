import { PropsWithChildren } from "react";
import defaultLogo from "../../assets/logo.png";

type PortalCardProps = PropsWithChildren<{
  eyebrow?: string;
  title: string;
  supporting?: string;
  logoUrl?: string | null;
}>;

export function PortalCard({ eyebrow, title, supporting, logoUrl, children }: PortalCardProps) {
  return (
    <main className="portal-shell">
      <section className="card">
        <img className="portal-logo" src={logoUrl ?? defaultLogo} alt="Herman Prompt" />
        {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
        <h1>{title}</h1>
        {supporting ? <p className="supporting">{supporting}</p> : null}
        {children}
      </section>
    </main>
  );
}
