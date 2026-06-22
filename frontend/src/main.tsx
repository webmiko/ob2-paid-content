import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./App";
import "./index.css";
import { setupPwa } from "./pwa";
import { scheduleSplashDismiss } from "./splash";

if (import.meta.env.PROD) {
  setupPwa();
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

scheduleSplashDismiss();
