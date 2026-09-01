import type { Meta, StoryObj } from "@storybook/react-vite";
import type { PositionSignalLinkResponse } from "../../types/signalLinks";
import { LinkedSignalCell } from "./LinkedSignalCell";

const mockLink: PositionSignalLinkResponse = {
  id: 123,
  symbol: "BTC/USDT",
  signal: {
    id: 1234,
    indicator: "rsi",
    timeframe: "1h",
    value: 0.83,
    direction: "ВВЕРХ",
  },
  close_condition: {
    id: 456,
    operator: ">=",
    target_value: 50000,
  },
};

const meta: Meta<typeof LinkedSignalCell> = {
  title: "Components/LinkedSignalCell",
  component: LinkedSignalCell,
};

export default meta;
type Story = StoryObj<typeof LinkedSignalCell>;

export const Default: Story = {
  args: { link: mockLink }
};
