import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/utils/cn";

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  footer?: ReactNode;
}

export function Card({
  className,
  title,
  description,
  footer,
  children,
  ...props
}: CardProps) {
  return (
    <div
      className={cn(
        "rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] shadow-[var(--shadow-sm)]",
        className,
      )}
      {...props}
    >
      {(title || description) && (
        <div className="border-b border-[var(--color-border)] px-5 py-4">
          {title && <h3 className="text-base font-semibold">{title}</h3>}
          {description && (
            <p className="mt-1 text-sm text-[var(--color-muted)]">
              {description}
            </p>
          )}
        </div>
      )}
      <div className="px-5 py-4">{children}</div>
      {footer && (
        <div className="border-t border-[var(--color-border)] px-5 py-4">
          {footer}
        </div>
      )}
    </div>
  );
}
