import React from "react";

interface InputFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  placeholder?: string;
  required?: boolean;
}

const InputField: React.FC<InputFieldProps> = ({
  label,
  value,
  onChange,
  type = "text",
  placeholder = "",
  required = false,
}) => {
  return (
    <div style={{ marginBottom: "1rem" }}>
      <label style={{ display: "block", marginBottom: "0.25rem" }}>{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        style={{
          width: "100%",
          padding: "0.5rem",
          borderRadius: "4px",
          border: "1px solid #ccc",
        }}
      />
    </div>
  );
};

export default InputField;
