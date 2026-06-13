/**
 * Onboarding step resolver. Gates the user through, in order:
 *   not authenticated -> AuthPage
 *   no AI config      -> ConfigPage
 *   no repository     -> RepoImportPage
 *   ready             -> RepoSummaryPage
 */
import { AppShell } from "./components/AppShell";
import { AuthPage } from "./pages/AuthPage";
import { ConfigPage } from "./pages/ConfigPage";
import { RepoImportPage } from "./pages/RepoImportPage";
import { RepoSummaryPage } from "./pages/RepoSummaryPage";
import { useCurrentUser } from "./hooks/useAuth";
import { useAiConfigStatus } from "./hooks/useAiConfig";
import { useCurrentRepository } from "./hooks/useRepository";
import type { User } from "./types/auth";

export default function App() {
  const { data: user, isLoading } = useCurrentUser();

  if (isLoading) return <div className="app-loading">Loading…</div>;
  if (!user) return <AuthPage />;
  return <OnboardingFlow user={user} />;
}

/** Mounted only when authenticated, so the gated queries always carry a token. */
function OnboardingFlow({ user }: { user: User }) {
  const aiConfig = useAiConfigStatus();
  const repository = useCurrentRepository();

  function renderStep() {
    if (aiConfig.isLoading || repository.isLoading) {
      return <div className="app-loading">Loading…</div>;
    }
    if (!aiConfig.data?.configured) return <ConfigPage />;
    if (!repository.data) return <RepoImportPage />;
    return <RepoSummaryPage repo={repository.data} />;
  }

  return <AppShell user={user}>{renderStep()}</AppShell>;
}
