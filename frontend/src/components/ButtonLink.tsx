import React from "react";
import { Link } from "react-router-dom";

type ButtonVariant = "primary" | "secondary" | "danger";

function variantClass(variant: ButtonVariant) {
  return variant === "primary"
    ? "btnPrimary"
    : variant === "danger"
    ? "btnDanger"
    : "";
}

export default function ButtonLink({
  to,
  children,
  variant = "primary",
  disabled = false,
  style,
}: {
  to: string;
  children: React.ReactNode;
  variant?: ButtonVariant;
  disabled?: boolean;
  style?: React.CSSProperties;
}) {
  const className = `btn ${variantClass(variant)}`;

  if (disabled) {
    return (
      <span
        className={className}
        style={{
          ...style,
          opacity: 0.55,
          cursor: "not-allowed",
          display: "inline-flex",
        }}
        aria-disabled="true"
      >
        {children}
      </span>
    );
  }

  return (
    <Link
      to={to}
      className={className}
      style={{ ...style, display: "inline-flex", alignItems: "center" }}
    >
      {children}
    </Link>
  );
}
