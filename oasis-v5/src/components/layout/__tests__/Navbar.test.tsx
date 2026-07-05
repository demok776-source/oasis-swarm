import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Navbar from '../Navbar';

// Mock next/link to render a simple anchor tag
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => {
    return <a href={href}>{children}</a>;
  };
});

describe('Navbar Component', () => {
  it('renders the OASIS_CORE logo', () => {
    render(<Navbar />);
    expect(screen.getByText('OASIS_CORE')).toBeInTheDocument();
  });

  it('renders navigation links', () => {
    render(<Navbar />);
    expect(screen.getByText('Memory')).toBeInTheDocument();
    expect(screen.getByText('Compute')).toBeInTheDocument();
    expect(screen.getByText('Aerospace')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('triggers initialization sequence when System Init is clicked', async () => {
    render(<Navbar />);
    
    const initBtn = screen.getByText('System Init');
    expect(initBtn).toBeInTheDocument();

    fireEvent.click(initBtn);

    // Button text should change
    expect(screen.getByText('Booting...')).toBeInTheDocument();
    
    // Toast should appear
    expect(screen.getByText('Initializing 13-Module Core...')).toBeInTheDocument();
    
    // After 3 seconds (we can mock timers to speed it up)
    // For simplicity, we just assert the immediate state change here
  });
});
