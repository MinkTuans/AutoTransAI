// @vitest-environment jsdom
import React from 'react';
import { afterEach, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import StudioSection from './StudioSection';
afterEach(cleanup);
it('preserves draft and component identity through collapse', () => {
  const view = open => <StudioSection id="review" title="Duyệt" open={open} onToggle={() => {}}><input aria-label="Bản dịch" defaultValue="Ban đầu" /></StudioSection>;
  const { rerender } = render(view(true));
  const input = screen.getByRole('textbox');
  fireEvent.change(input, { target: { value: 'Đã sửa' } });
  input.focus();
  rerender(view(false));
  expect(screen.queryByRole('textbox')).toBeNull();
  expect(input.isConnected).toBe(true);
  rerender(view(true));
  expect(screen.getByRole('textbox')).toBe(input);
  expect(input.value).toBe('Đã sửa');
});
it('links a native toggle button to a hidden labelled panel', () => {
  const toggle = vi.fn();
  render(<StudioSection id="setup" title="Nhập" summary="Tùy chọn đang bật" open={false} onToggle={toggle}><input /></StudioSection>);
  const button = screen.getByRole('button', { name: /Nhập/ });
  expect(button.type).toBe('button');
  expect(button.getAttribute('aria-expanded')).toBe('false');
  const panel = document.getElementById(button.getAttribute('aria-controls'));
  expect(panel.hidden).toBe(true);
  expect(panel.getAttribute('aria-labelledby')).toBe(button.id);
  expect(screen.getByText('Tùy chọn đang bật')).toBeTruthy();
  fireEvent.click(button);
  expect(toggle).toHaveBeenCalledWith(true);
});
