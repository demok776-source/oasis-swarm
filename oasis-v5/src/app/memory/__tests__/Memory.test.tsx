import { render, screen } from '@testing-library/react';
import Memory from '../page';

// Mock fetch for telemetry data
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({ db_size_kb: 1024, contacts_count: 50, events_count: 100 }),
  })
) as jest.Mock;

describe('Memory Page', () => {
  it('renders the Memory Fabric dashboard', async () => {
    render(<Memory />);
    
    expect(screen.getByText('Memory Fabric (Vector & Relation)')).toBeInTheDocument();
    expect(screen.getByText('SQL Relational Storage')).toBeInTheDocument();
    expect(screen.getByText('Qdrant Vector Store')).toBeInTheDocument();
    
    // Wait for telemetry mock to populate
    expect(await screen.findByText('1024 KB')).toBeInTheDocument();
    expect(await screen.findByText('50')).toBeInTheDocument();
    expect(await screen.findByText('100')).toBeInTheDocument();
  });
});
