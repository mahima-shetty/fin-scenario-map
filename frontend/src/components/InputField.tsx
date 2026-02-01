import React from "react";

interface InputFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  placeholder?: string;
  required?: boolean;
  helperText?: string;
}

const InputField: React.FC<InputFieldProps> = ({
  label,
  value,
  onChange,
  type = "text",
  placeholder = "",
  required = false,
  helperText,
}) => {
  return (
    <div>
      <label className="fieldLabel">
        {label}
        {required ? " *" : ""}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        className="input"
      />
      {helperText ? <div className="helper">{helperText}</div> : null}
    </div>
  );
};

export default InputField;
