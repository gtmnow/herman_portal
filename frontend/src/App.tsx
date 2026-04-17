import { useMemo } from "react";
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
import { LoginPage } from "./pages/LoginPage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";


function getRoute(pathname: string) {
  if (pathname === "/forgot-password") {
    return "forgot-password";
  }
  if (pathname === "/reset-password") {
    return "reset-password";
  }
  return "login";
}


export function App() {
  const route = useMemo(() => getRoute(window.location.pathname), []);

  if (route === "forgot-password") {
    return <ForgotPasswordPage />;
  }

  if (route === "reset-password") {
    return <ResetPasswordPage />;
  }

  return <LoginPage />;
}
