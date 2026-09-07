import type { Meta, StoryObj } from "@storybook/react-vite";
import { PositionRow } from "./PositionRow";


const meta: Meta<typeof PositionRow> = {
  title: "Components/PositionRow",
  component: PositionRow,
}

export default meta;
type Story = StoryObj<typeof PositionRow>;

export const Default: Story = {
  args: {
    position: {
      symbol: "BTC/USDT",
      display_symbol: "BTC/USDT",
      side: "long",
      pnl: 20,
      pnlPct: 10,
    },
    index: 1,
  }
}