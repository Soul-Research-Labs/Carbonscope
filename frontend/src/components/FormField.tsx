"use client";

import {
  type InputHTMLAttributes,
  type ReactNode,
  type ReactElement,
  useId,
  isValidElement,
  cloneElement,
} from "react";

interface FormFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: string;
  children?: ReactNode;
}

export function FormField({
  label,
  error,
  hint,
  children,
  className = "",
  ...inputProps
}: FormFieldProps) {
  const id = useId();

  // When children are provided (e.g. <select>), inject the generated id
  // so the <label htmlFor> correctly associates with the child element.
  const renderedChildren = children
    ? isValidElement(children)
      ? cloneElement(children as ReactElement<{ id?: string }>, { id })
      : children
    : null;

  return (
    <div className="space-y-1">
      <label
        htmlFor={id}
        className="block text-sm font-medium text-[var(--foreground)]"
      >
        {label}
      </label>

      {renderedChildren ?? (
        <input
          id={id}
          className={`block w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 ${
            error
              ? "border-red-500 focus:ring-red-400"
              : "border-[var(--card-border)] focus:ring-[var(--primary)]"
          } ${className}`}
          aria-invalid={!!error}
          aria-describedby={
            error ? `${id}-error` : hint ? `${id}-hint` : undefined
          }
          {...inputProps}
        />
      )}

      {error && (
        <p id={`${id}-error`} className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
      {!error && hint && (
        <p id={`${id}-hint`} className="text-sm text-gray-500">
          {hint}
        </p>
      )}
    </div>
  );
}
