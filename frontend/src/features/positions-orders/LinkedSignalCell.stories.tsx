import type { Meta, StoryObj } from "@storybook/react-vite";
import type { PositionSignalLinkResponse } from "../../types/signalLinks";
import { LinkedSignalCell } from "./LinkedSignalCell";
import { useSignalLinksStore } from "../../store/useSignalLinksStore";

const mockLink: PositionSignalLinkResponse = {
  id: 123,
  symbol: "BTC/USDT",
  signal: {
    id: 1234,
    indicator: "emaSma",
    timeframe: "1h",
    value: 0.83,
    direction: "ВВЕРХ",
  },
  closeCondition: {
    id: 456,
    operator: ">=",
    targetValue: 50000,
  },
  createdAt: "2026-09-06T12:00:00",
};

const meta: Meta<typeof LinkedSignalCell> = {
  title: "Components/LinkedSignalCell",
  component: LinkedSignalCell,
  beforeEach: () => {
    useSignalLinksStore.getState().setCurrentValues(
      [
        {
          symbol: "BTC/USDT",
          indicator: "rsi",
          value: 0.91,
        },
      ],
      "1h",
    );
  },
};

export default meta;
type Story = StoryObj<typeof LinkedSignalCell>;

export const Default: Story = {
  args: {
    link: mockLink,
    onBindClick: () => {},
    onUnbindClick: () => {},
  },
};
