import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Spinner, Alert } from 'react-bootstrap';
import { getDatabaseStats, checkHealth } from '../services/api';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statsResponse, healthResponse] = await Promise.all([
        getDatabaseStats(),
        checkHealth()
      ]);
      setStats(statsResponse.data);
      setHealth(healthResponse.data);
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-5">
        <Alert variant="danger">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container>
      <h1 className="mb-4">Dashboard</h1>
      
      <Row className="mb-4">
        <Col md={3}>
          <Card>
            <Card.Body>
              <Card.Title>System Status</Card.Title>
              <Card.Text>
                <span className={`badge bg-${health?.status === 'healthy' ? 'success' : 'danger'}`}>
                  {health?.status || 'Unknown'}
                </span>
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={3}>
          <Card>
            <Card.Body>
              <Card.Title>Total Contacts</Card.Title>
              <Card.Text className="h3">
                {stats?.total_contacts || 0}
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={3}>
          <Card>
            <Card.Body>
              <Card.Title>Active Contacts</Card.Title>
              <Card.Text className="h3">
                {stats?.active_contacts || 0}
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={3}>
          <Card>
            <Card.Body>
              <Card.Title>Total Operations</Card.Title>
              <Card.Text className="h3">
                {stats?.total_operations || 0}
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {stats?.contacts_by_source && (
        <Row>
          <Col>
            <Card>
              <Card.Body>
                <Card.Title>Contacts by Source</Card.Title>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Source</th>
                      <th>Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(stats.contacts_by_source).map(([source, count]) => (
                      <tr key={source}>
                        <td>{source}</td>
                        <td>{count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </Container>
  );
}

export default Dashboard;