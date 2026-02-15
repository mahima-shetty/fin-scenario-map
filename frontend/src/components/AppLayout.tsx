import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import Button from "./Button";
import { getAuthState, signOut } from "../services/authStorage";

function Icon({ name }: { name: "dashboard" | "upload" | "create" | "history" | "login" }) {
  const common = { width: 18, height: 18, fill: "none", stroke: "currentColor", strokeWidth: 2 };
  switch (name) {
    case "dashboard":
      return (
        <svg {...common} viewBox="0 0 24 24" aria-hidden="true">
          <path d="M4 13h7V4H4v9Z" />
          <path d="M13 20h7V11h-7v9Z" />
          <path d="M13 4h7v5h-7V4Z" />
          <path d="M4 15h7v5H4v-5Z" />
        </svg>
      );
    case "upload":
      return (
        <svg {...common} viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 3v12" />
          <path d="M7 8l5-5 5 5" />
          <path d="M5 21h14" />
        </svg>
      );
    case "create":
      return (
        <svg {...common} viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 5v14" />
          <path d="M5 12h14" />
        </svg>
      );
    case "history":
      return (
        <svg {...common} viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 20a8 8 0 1 0 0-16 8 8 0 0 0 0 16z" />
          <path d="M12 6v6l4 2" />
        </svg>
      );
    case "login":
      return (
        <svg {...common} viewBox="0 0 24 24" aria-hidden="true">
          <path d="M10 17l5-5-5-5" />
          <path d="M15 12H3" />
          <path d="M21 3v18" />
        </svg>
      );
  }
}

export default function AppLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const auth = getAuthState();

  const title =
    location.pathname === "/"
      ? "Dashboard"
      : location.pathname.startsWith("/scenarios/upload")
        ? "Upload Scenario"
        : location.pathname.startsWith("/scenarios/new")
          ? "Create Scenario"
          : location.pathname === "/historical-cases"
            ? "Historical Cases"
            : location.pathname.startsWith("/admin")
              ? "Audit logs"
              : "Fin Scenario Map";

  return (
    <div className="appShell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brandMark" aria-hidden="true">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 19V9" />
              <path d="M9 19V5" />
              <path d="M14 19v-7" />
              <path d="M19 19V11" />
            </svg>
          </div>
          <div>
            <div className="brandTitle">Fin Scenario Map</div>
            <div className="brandSub">Bank-grade scenario analysis</div>
          </div>
        </div>

        <nav className="nav" aria-label="Primary navigation">
          <NavLink
            to="/"
            className={({ isActive }) => `navItem ${isActive ? "navItemActive" : ""}`}
            end
          >
            <Icon name="dashboard" />
            Dashboard
          </NavLink>

          <NavLink
            to="/scenarios/upload"
            className={({ isActive }) => `navItem ${isActive ? "navItemActive" : ""}`}
          >
            <Icon name="upload" />
            Upload
          </NavLink>

          <NavLink
            to="/scenarios/new"
            className={({ isActive }) => `navItem ${isActive ? "navItemActive" : ""}`}
          >
            <Icon name="create" />
            Create
          </NavLink>

          <NavLink
            to="/historical-cases"
            className={({ isActive }) => `navItem ${isActive ? "navItemActive" : ""}`}
          >
            <Icon name="history" />
            Historical Cases
          </NavLink>

          {auth.role === "admin" && (
            <NavLink
              to="/admin/audit-logs"
              className={({ isActive }) => `navItem ${isActive ? "navItemActive" : ""}`}
            >
              <Icon name="history" />
              Audit logs
            </NavLink>
          )}
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <div style={{ fontWeight: 750 }}>{title}</div>
            <div className="topbarTitle">Navy banking UI · secure workflow · audit-ready</div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            {auth.email ? <div className="badge">{auth.email}</div> : null}
            <div className="badge badgeOk">Environment: Local</div>
            <Button
              variant="secondary"
              onClick={() => {
                signOut();
                navigate("/login", { replace: true });
              }}
            >
              Sign out
            </Button>
          </div>
        </header>

        <div className="content container">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

