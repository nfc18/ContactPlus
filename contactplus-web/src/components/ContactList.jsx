import React from 'react';
import { Table, Button, Badge } from 'react-bootstrap';

function ContactList({ contacts, onEdit, onDelete, onView }) {
  return (
    <Table striped bordered hover responsive>
      <thead>
        <tr>
          <th>Name</th>
          <th>Email(s)</th>
          <th>Phone(s)</th>
          <th>Organization</th>
          <th>Source</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {contacts.map((contact) => (
          <tr key={contact.contact_id}>
            <td>{contact.formatted_name}</td>
            <td>
              {contact.emails.map((email, idx) => (
                <div key={idx}>{email}</div>
              ))}
            </td>
            <td>
              {contact.phones.map((phone, idx) => (
                <div key={idx}>{phone}</div>
              ))}
            </td>
            <td>{contact.organization || '-'}</td>
            <td>
              <Badge bg="info">{contact.source_info.database_name}</Badge>
            </td>
            <td>
              <Button
                variant="primary"
                size="sm"
                className="me-1"
                onClick={() => onView(contact)}
              >
                View
              </Button>
              <Button
                variant="warning"
                size="sm"
                className="me-1"
                onClick={() => onEdit(contact)}
              >
                Edit
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => onDelete(contact)}
              >
                Delete
              </Button>
            </td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
}

export default ContactList;