/** Authenticated landing screen — placeholder until the agent UI is built. */
import { useLogout } from "../hooks/useAuth";
import type { User } from "../types/auth";

export function HomePage({ user }: { user: User }) {
  const logout = useLogout();

  return (
    <div className="home">
      <header className="home__header">
        <h1>openruki</h1>
        <div className="home__user">
          <span>{user.email}</span>
          <button type="button" onClick={logout}>
            Log out
          </button>
        </div>
      </header>

      <main className="home__main">
        <p>You're logged in. The feature-builder UI will live here.</p>
      </main>
    </div>
  );
}
