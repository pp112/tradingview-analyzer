import type { Meta, StoryObj } from "@storybook/react-vite";
import { useEffect, type ComponentProps } from "react";
import { SignalBindModal } from "./SignalBindModal";
import { useSignalsStore } from "../../store/useSignalsStore";
import { useSignalLinksStore } from "../../store/useSignalLinksStore";

const mockSignals = {
  "1h": [
    {
      symbol: "BTCUSDT",
      indicator: "rsi",
      indicator_value: 68.4,
      direction: "ВВЕРХ",
      vol_ratio: 1.31,
      correlation: 0.82,
      timeframe: "1h",
    },
    {
      symbol: "BTCUSDT",
      indicator: "ema_sma",
      indicator_value: 0.012,
      direction: "ВВЕРХ",
      vol_ratio: 1.14,
      correlation: 0.66,
      timeframe: "1h",
    },
  ],
} as const;

function SignalBindModalWithData(
  props: ComponentProps<typeof SignalBindModal>,
) {
  const setAllSignals = useSignalsStore((state) => state.setAllSignals);
  const setPositionLinks = useSignalLinksStore(
    (state) => state.setPositionLinks,
  );
  const setOrderLinks = useSignalLinksStore((state) => state.setOrderLinks);

  useEffect(() => {
    // @ts-expect-error mockSignals is readonly due to 'as const', but setAllSignals expects mutable type
    setAllSignals(mockSignals);
    setPositionLinks([]);
    setOrderLinks([]);
  }, [setAllSignals, setPositionLinks, setOrderLinks]);

  return <SignalBindModal {...props} />;
}

const meta: Meta<typeof SignalBindModal> = {
  title: "Components/SignalBindModal",
  component: SignalBindModal,
};

export default meta;
type Story = StoryObj<typeof SignalBindModal>;

export const Default: Story = {
  args: {
    symbol: "BTCUSDT",
    entityType: "position",
    direction: "ВВЕРХ",
    onClose: () => undefined,
  },
  render: (args) => <SignalBindModalWithData {...args} />,
};
