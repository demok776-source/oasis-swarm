import { render, screen } from '@testing-library/react';
import Aerospace from '../page';

describe('Aerospace Page', () => {
  it('renders the Aerospace dashboard and mock telemetry', () => {
    render(<Aerospace />);
    
    expect(screen.getByText('Aerospace Telemetry Link')).toBeInTheDocument();
    expect(screen.getByText('Uplink Status')).toBeInTheDocument();
    
    // Check for ABORT MISSION button
    expect(screen.getByText('ABORT MISSION')).toBeInTheDocument();
  });
});
