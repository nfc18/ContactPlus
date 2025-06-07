import React, { useState } from 'react';
import { Form, InputGroup, Button } from 'react-bootstrap';

function SearchBar({ onSearch, placeholder = "Search contacts..." }) {
  const [query, setQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  const handleClear = () => {
    setQuery('');
    onSearch('');
  };

  return (
    <Form onSubmit={handleSearch}>
      <InputGroup className="mb-3">
        <Form.Control
          type="text"
          placeholder={placeholder}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <Button variant="primary" type="submit">
          Search
        </Button>
        {query && (
          <Button variant="secondary" onClick={handleClear}>
            Clear
          </Button>
        )}
      </InputGroup>
    </Form>
  );
}

export default SearchBar;