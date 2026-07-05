import { render, screen, fireEvent } from '@testing-library/react';
import Settings from '../page';
import { useStore } from '@/store/useStore';

jest.mock('@/store/useStore', () => ({
  useStore: jest.fn(),
}));

describe('Settings Page', () => {
  beforeEach(() => {
    (useStore as unknown as jest.Mock).mockReturnValue({
      apiKey: '',
      setApiKey: jest.fn(),
      simulationMode: true,
      setSimulationMode: jest.fn(),
    });
  });

  it('renders the Neural Net Authentication section', () => {
    render(<Settings />);
    expect(screen.getByText(/Neural Net Authentication/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText('sk-...')).toBeInTheDocument();
  });

  it('calls setApiKey when the save button is clicked', () => {
    const mockSetApiKey = jest.fn();
    (useStore as unknown as jest.Mock).mockReturnValue({
      apiKey: '',
      setApiKey: mockSetApiKey,
      simulationMode: true,
      setSimulationMode: jest.fn(),
    });

    render(<Settings />);
    
    const input = screen.getByPlaceholderText('sk-...');
    fireEvent.change(input, { target: { value: 'sk-12345' } });
    
    const saveButton = screen.getByText('Save');
    fireEvent.click(saveButton);

    expect(mockSetApiKey).toHaveBeenCalledWith('sk-12345');
    expect(screen.getByText('Saved')).toBeInTheDocument();
  });
});
