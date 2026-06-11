/** Top-level routing between the auth screen and the authenticated app. */
import { AuthPage } from "./pages/AuthPage";
import { HomePage } from "./pages/HomePage";
import { useCurrentUser } from "./hooks/useAuth";

export default function App() {
  const { data: user, isLoading } = useCurrentUser();

  if (isLoading) {
    return <div className="app-loading">Loading…</div>;
  }

  return user ? <HomePage user={user} /> : <AuthPage />;
}
