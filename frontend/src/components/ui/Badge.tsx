import type { ReactNode } from "react";

type BadgeVariant = "bull" | "bear" | "volume";

type BadgeProps = {
  variant: BadgeVariant;
  children: ReactNode;
};

export function Badge({ variant, children }: BadgeProps) {
  return <span className={`badge badge-${variant}`}>{children}</span>;
}
