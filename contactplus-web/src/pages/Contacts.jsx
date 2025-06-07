import React, { useState, useEffect } from 'react';
import { Container, Button, Pagination, Spinner, Alert } from 'react-bootstrap';
import { getContacts, searchContacts, deleteContact, exportDatabase } from '../services/api';
import ContactList from '../components/ContactList';
import ContactDetail from '../components/ContactDetail';
import SearchBar from '../components/SearchBar';

function Contacts() {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedContact, setSelectedContact] = useState(null);
  const [showDetail, setShowDetail] = useState(false);
  const [detailMode, setDetailMode] = useState('view');

  useEffect(() => {
    fetchContacts();
  }, [currentPage, searchQuery]);

  const fetchContacts = async () => {
    try {
      setLoading(true);
      let response;
      
      if (searchQuery) {
        response = await searchContacts(searchQuery, ['fn', 'email', 'phone', 'organization'], currentPage);
      } else {
        response = await getContacts(currentPage);
      }
      
      setContacts(response.data.contacts);
      setTotalPages(response.data.total_pages);
      setTotal(response.data.total);
      setError(null);
    } catch (err) {
      setError('Failed to load contacts');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    setCurrentPage(1);
  };

  const handleView = (contact) => {
    setSelectedContact(contact);
    setDetailMode('view');
    setShowDetail(true);
  };

  const handleEdit = (contact) => {
    setSelectedContact(contact);
    setDetailMode('edit');
    setShowDetail(true);
  };

  const handleDelete = async (contact) => {
    if (window.confirm(`Are you sure you want to delete ${contact.formatted_name}?`)) {
      try {
        await deleteContact(contact.contact_id);
        fetchContacts();
      } catch (err) {
        alert('Failed to delete contact');
      }
    }
  };

  const handleExport = async () => {
    try {
      const response = await exportDatabase();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `contactplus_export_${new Date().toISOString().split('T')[0]}.vcf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to export contacts');
    }
  };

  if (loading && !contacts.length) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </Container>
    );
  }

  return (
    <Container>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Contacts ({total})</h1>
        <Button variant="success" onClick={handleExport}>
          Export All Contacts
        </Button>
      </div>

      <SearchBar onSearch={handleSearch} />

      {error && <Alert variant="danger">{error}</Alert>}

      <ContactList
        contacts={contacts}
        onView={handleView}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      <Pagination className="justify-content-center">
        <Pagination.First
          onClick={() => setCurrentPage(1)}
          disabled={currentPage === 1}
        />
        <Pagination.Prev
          onClick={() => setCurrentPage(currentPage - 1)}
          disabled={currentPage === 1}
        />
        
        {[...Array(Math.min(5, totalPages))].map((_, idx) => {
          const pageNum = currentPage - 2 + idx;
          if (pageNum > 0 && pageNum <= totalPages) {
            return (
              <Pagination.Item
                key={pageNum}
                active={pageNum === currentPage}
                onClick={() => setCurrentPage(pageNum)}
              >
                {pageNum}
              </Pagination.Item>
            );
          }
          return null;
        })}
        
        <Pagination.Next
          onClick={() => setCurrentPage(currentPage + 1)}
          disabled={currentPage === totalPages}
        />
        <Pagination.Last
          onClick={() => setCurrentPage(totalPages)}
          disabled={currentPage === totalPages}
        />
      </Pagination>

      <ContactDetail
        contact={selectedContact}
        show={showDetail}
        onHide={() => setShowDetail(false)}
        onUpdate={fetchContacts}
        readOnly={detailMode === 'view'}
      />
    </Container>
  );
}

export default Contacts;