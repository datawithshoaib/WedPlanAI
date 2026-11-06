"use client";

import * as React from "react";

import { Button } from "@/components/ui/button";

type ButtonProps = React.ComponentProps<typeof Button>;

interface ConfirmButtonProps extends Omit<ButtonProps, "onClick"> {
  onConfirm: () => void;
  confirmLabel?: React.ReactNode;
}

/** A destructive button that needs a second click within a few seconds. */
export function ConfirmButton({
  onConfirm,
  confirmLabel = "Click again to confirm",
  children,
  ...props
}: ConfirmButtonProps) {
  const [armed, setArmed] = React.useState(false);

  React.useEffect(() => {
    if (!armed) return;
    const id = window.setTimeout(() => setArmed(false), 3500);
    return () => window.clearTimeout(id);
  }, [armed]);

  return (
    <Button
      {...props}
      variant={armed ? "destructive" : props.variant}
      onClick={() => {
        if (armed) {
          setArmed(false);
          onConfirm();
        } else {
          setArmed(true);
        }
      }}
      onBlur={() => setArmed(false)}
    >
      {armed ? confirmLabel : children}
    </Button>
  );
}
