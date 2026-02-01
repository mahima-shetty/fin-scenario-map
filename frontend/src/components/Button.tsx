import React from "react";

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
  disabled?: boolean;
  style?: React.CSSProperties;
}

const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  type = "button",
  disabled = false,
  style = {},
}) => {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      style={{
        padding: "0.5rem 1rem",
        borderRadius: "4px",
        border: "none",
        backgroundColor: disabled ? "#ccc" : "#007bff",
        color: "#fff",
        cursor: disabled ? "not-allowed" : "pointer",
        fontWeight: 600,
        ...style,
      }}
    >
      {children}
    </button>
  );
};

export default Button;
