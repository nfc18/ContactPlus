import React, { useState, useEffect } from 'react';
import { Container, Card, Button, Alert, ProgressBar, Badge } from 'react-bootstrap';
import { importInitialDatabases, getImportStatus, getDatabaseStats } from '../services/api';

function Import() {
  const [importing, setImporting] = useState(false);
  const [importStatus, setImportStatus] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const [statusResponse, statsResponse] = await Promise.all([
        getImportStatus(),
        getDatabaseStats()
      ]);
      setImportStatus(statusResponse.data);
      setStats(statsResponse.data);
    } catch (err) {
      console.error('Failed to fetch status:', err);
    }
  };

  const handleImport = async () => {
    if (window.confirm('This will import all 3 source databases. Continue?')) {
      try {
        setImporting(true);
        setError(null);
        setSuccess(null);
        
        const response = await importInitialDatabases();
        
        setSuccess(`Successfully imported ${response.data.imported_contacts} contacts from ${response.data.database_name}`);
        fetchStatus();
      } catch (err) {
        setError('Import failed: ' + (err.response?.data?.detail || err.message));
      } finally {
        setImporting(false);
      }
    }
  };

  return (
    <Container>
      <h1 className="mb-4">Import Contacts</h1>

      {error && <Alert variant="danger" dismissible onClose={() => setError(null)}>{error}</Alert>}
      {success && <Alert variant="success" dismissible onClose={() => setSuccess(null)}>{success}</Alert>}

      <Card className="mb-4">
        <Card.Body>
          <Card.Title>One-Time Initial Import</Card.Title>
          <Card.Text>
            Import all contacts from the 3 source databases:
          </Card.Text>
          <ul>
            <li>Sara Export (3,074 contacts)</li>
            <li>iPhone Contacts</li>
            <li>iPhone Suggested Contacts</li>
          </ul>
          
          {stats && stats.total_contacts > 0 ? (
            <Alert variant="warning">
              <strong>Warning:</strong> Database already contains {stats.total_contacts} contacts.
              Initial import may have already been completed.
            </Alert>
          ) : (
            <Button
              variant="primary"
              size="lg"
              onClick={handleImport}
              disabled={importing}
            >
              {importing ? 'Importing...' : 'Start Initial Import'}
            </Button>
          )}
        </Card.Body>
      </Card>

      {importing && (
        <Card>
          <Card.Body>
            <Card.Title>Import Progress</Card.Title>
            <ProgressBar animated now={100} label="Processing..." />
          </Card.Body>
        </Card>
      )}

      {stats && stats.contacts_by_source && (
        <Card>
          <Card.Body>
            <Card.Title>Current Database Status</Card.Title>
            <p>Total Contacts: <strong>{stats.total_contacts}</strong></p>
            <p>Active Contacts: <strong>{stats.active_contacts}</strong></p>
            
            <h6>Contacts by Source:</h6>
            {Object.entries(stats.contacts_by_source).map(([source, count]) => (
              <div key={source} className="mb-2">
                <Badge bg="secondary" className="me-2">{source}</Badge>
                <span>{count} contacts</span>
              </div>
            ))}
          </Card.Body>
        </Card>
      )}
    </Container>
  );
}

export default Import;