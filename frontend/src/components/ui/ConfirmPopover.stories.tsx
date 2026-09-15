import type { Meta, StoryObj } from "@storybook/react-vite";
import { ConfirmPopover } from "./ConfirmPopover";


const meta: Meta<typeof ConfirmPopover> = {
  title: "Components/ConfirmPopover",
  component: ConfirmPopover,
};

export default meta;

type Story = StoryObj<typeof ConfirmPopover>;

export const Default: Story = {
  args: { 
    message: "Закрыть позицию?",
    onConfirm: () => {},
    onCancel: () => {},
  }
};
