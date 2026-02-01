import React from "react";

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
  disabled?: boolean;
  style?: React.CSSProperties;
  variant?: "primary" | "secondary" | "danger";
}

const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  type = "button",
  disabled = false,
  style = {},
  variant = "primary",
}) => {
  const variantClass =
    variant === "primary" ? "btnPrimary" : variant === "danger" ? "btnDanger" : "";
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`btn ${variantClass}`}
      style={style}
    >
      {children}
    </button>
  );
};

export default Button;
