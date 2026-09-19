import React, { useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

type ConfirmPopoverProps = {
  anchorRef: React.RefObject<HTMLElement | null>;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
};

export function ConfirmPopover({
  anchorRef,
  message,
  confirmLabel = "Да",
  cancelLabel = "Отмена",
  onConfirm,
  onCancel,
}: ConfirmPopoverProps) {
  const popoverRef = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState<{ top: number; left: number } | null>(null);

  useLayoutEffect(() => {
    const anchor = anchorRef.current;
    if (!anchor) {
      setPos(null);
      return;
    }

    const anchorRect = anchor.getBoundingClientRect();

    setPos({
      top: anchorRect.bottom - anchorRect.height / 2,
      left: anchorRect.left - 9,
    });
  }, [anchorRef]);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      const target = e.target as Node;
      const popover = popoverRef.current;
      const anchor = anchorRef.current;
      if (popover && !popover.contains(target) && !anchor?.contains(target)) {
        onCancel();
      }
    };
    document.addEventListener("mousedown", handleClick, true);
    return () => document.removeEventListener("mousedown", handleClick, true);
  }, [onCancel, anchorRef]);

  return createPortal(
    <div
      className="po-modal-confirm-popover"
      ref={popoverRef}
      style={{
        top: pos?.top ?? 0,
        left: pos?.left ?? 0,
        visibility: pos ? "visible" : "hidden",
      }}
    >
      <p className="po-modal-confirm-popover-text">{message}</p>
      <div className="po-modal-confirm-popover-actions">
        <button
          className="po-modal-confirm-popover-btn confirm"
          onClick={onConfirm}
        >
          {confirmLabel}
        </button>
        <button
          className="po-modal-confirm-popover-btn cancel"
          onClick={onCancel}
        >
          {cancelLabel}
        </button>
      </div>
    </div>,
    document.body,
  );
}
