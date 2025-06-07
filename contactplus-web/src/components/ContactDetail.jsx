import React, { useState } from 'react';
import { Modal, Form, Button, Badge, Alert } from 'react-bootstrap';
import { updateContact } from '../services/api';

function ContactDetail({ contact, show, onHide, onUpdate, readOnly = false }) {
  const [formData, setFormData] = useState({
    fn: contact?.formatted_name || '',
    emails: contact?.emails || [],
    phones: contact?.phones || [],
    organization: contact?.organization || '',
    title: contact?.title || '',
    notes: contact?.notes || ''
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  if (!contact) return null;

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleArrayChange = (field, index, value) => {
    const newArray = [...formData[field]];
    newArray[index] = value;
    setFormData(prev => ({ ...prev, [field]: newArray }));
  };

  const addArrayItem = (field) => {
    setFormData(prev => ({ ...prev, [field]: [...prev[field], ''] }));
  };

  const removeArrayItem = (field, index) => {
    const newArray = formData[field].filter((_, i) => i !== index);
    setFormData(prev => ({ ...prev, [field]: newArray }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      await updateContact(contact.contact_id, formData);
      onUpdate();
      onHide();
    } catch (err) {
      setError('Failed to update contact');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>
          {readOnly ? 'Contact Details' : 'Edit Contact'}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {error && <Alert variant="danger">{error}</Alert>}
        
        <Form>
          <Form.Group className="mb-3">
            <Form.Label>Name</Form.Label>
            <Form.Control
              type="text"
              value={formData.fn}
              onChange={(e) => handleChange('fn', e.target.value)}
              disabled={readOnly}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Email Addresses</Form.Label>
            {formData.emails.map((email, index) => (
              <div key={index} className="d-flex mb-2">
                <Form.Control
                  type="email"
                  value={email}
                  onChange={(e) => handleArrayChange('emails', index, e.target.value)}
                  disabled={readOnly}
                />
                {!readOnly && (
                  <Button
                    variant="danger"
                    size="sm"
                    className="ms-2"
                    onClick={() => removeArrayItem('emails', index)}
                  >
                    Remove
                  </Button>
                )}
              </div>
            ))}
            {!readOnly && (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => addArrayItem('emails')}
              >
                Add Email
              </Button>
            )}
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Phone Numbers</Form.Label>
            {formData.phones.map((phone, index) => (
              <div key={index} className="d-flex mb-2">
                <Form.Control
                  type="tel"
                  value={phone}
                  onChange={(e) => handleArrayChange('phones', index, e.target.value)}
                  disabled={readOnly}
                />
                {!readOnly && (
                  <Button
                    variant="danger"
                    size="sm"
                    className="ms-2"
                    onClick={() => removeArrayItem('phones', index)}
                  >
                    Remove
                  </Button>
                )}
              </div>
            ))}
            {!readOnly && (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => addArrayItem('phones')}
              >
                Add Phone
              </Button>
            )}
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Organization</Form.Label>
            <Form.Control
              type="text"
              value={formData.organization}
              onChange={(e) => handleChange('organization', e.target.value)}
              disabled={readOnly}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Title</Form.Label>
            <Form.Control
              type="text"
              value={formData.title}
              onChange={(e) => handleChange('title', e.target.value)}
              disabled={readOnly}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Notes</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              disabled={readOnly}
            />
          </Form.Group>

          <hr />
          
          <div>
            <strong>Source Information:</strong>
            <p className="mb-1">Database: <Badge bg="info">{contact.source_info.database_name}</Badge></p>
            <p className="mb-1">Import Time: {new Date(contact.source_info.import_timestamp).toLocaleString()}</p>
            <p className="mb-1">Version: {contact.version}</p>
          </div>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
        {!readOnly && (
          <Button variant="primary" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        )}
      </Modal.Footer>
    </Modal>
  );
}

export default ContactDetail;