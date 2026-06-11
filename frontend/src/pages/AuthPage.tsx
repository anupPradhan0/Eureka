/** Login / register screen. */
import { useState, type FormEvent } from "react";

import { useLogin, useRegister } from "../hooks/useAuth";
import { ApiError } from "../api/client";

type Mode = "login" | "register";

export function AuthPage() {
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const login = useLogin();
  const register = useRegister();
  const active = mode === "login" ? login : register;

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    active.mutate({ email, password });
  };

  const errorMessage =
    active.error instanceof ApiError
      ? active.error.message
      : active.error
        ? "Something went wrong."
        : null;

  return (
    <div className="auth">
      <h1>openruki</h1>
      <p className="auth__tagline">
        Low-code, built into your self-hosted open-source apps.
      </p>

      <div className="auth__tabs">
        <button
          type="button"
          className={mode === "login" ? "is-active" : ""}
          onClick={() => setMode("login")}
        >
          Log in
        </button>
        <button
          type="button"
          className={mode === "register" ? "is-active" : ""}
          onClick={() => setMode("register")}
        >
          Register
        </button>
      </div>

      <form className="auth__form" onSubmit={onSubmit}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
          />
        </label>

        {errorMessage && <p className="auth__error">{errorMessage}</p>}

        <button type="submit" disabled={active.isPending}>
          {active.isPending
            ? "Please wait…"
            : mode === "login"
              ? "Log in"
              : "Create account"}
        </button>
      </form>
    </div>
  );
}
