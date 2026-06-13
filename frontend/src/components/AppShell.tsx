/** Authenticated chrome: brand header + user/logout, with the active step as children. */
import type { ReactNode } from "react";

import { useLogout } from "../hooks/useAuth";
import type { User } from "../types/auth";

export function AppShell({ user, children }: { user: User; children: ReactNode }) {
  const logout = useLogout();

  return (
    <div className="app">
      <header className="app__header">
        <h1 className="app__brand">Eureka</h1>
        <div className="app__user">
          <span>{user.email}</span>
          <button type="button" onClick={logout}>
            Log out
          </button>
        </div>
      </header>
      <main className="app__main">{children}</main>
    </div>
  );
}
