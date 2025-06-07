# ContactPlus MVP v1.0

A professional vCard contact management system with Docker containerization and comprehensive testing.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Start the System

```bash
# Clone the repository
git clone <repository-url>
cd ContactPlus

# Quick start with testing
./test_mvp.sh

# OR manual start
docker-compose up -d
```

### Access the Services

- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8080/docs
- **System Monitor**: http://localhost:9090
- **Log Viewer (Dozzle)**: http://localhost:8081

## 🏗️ Architecture

The system consists of 4 containerized services:

1. **contactplus-core**: FastAPI backend with vCard database
2. **contactplus-web**: React.js frontend interface
3. **contactplus-monitor**: Simple monitoring dashboard
4. **dozzle**: Real-time log viewer and management

## 📦 Initial Data Import

1. Navigate to http://localhost:3000/import
2. Click "Start Initial Import"
3. The system will import contacts from:
   - Sara Export (3,074 contacts)
   - iPhone Contacts
   - iPhone Suggested Contacts

## 🔧 Development

### Core API Development

```bash
cd contactplus-core
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Web Interface Development

```bash
cd contactplus-web
npm install
npm start
```

## 📊 API Endpoints

### Contact Operations
- `GET /api/v1/contacts` - List contacts (paginated)
- `GET /api/v1/contacts/{id}` - Get contact details
- `PUT /api/v1/contacts/{id}` - Update contact
- `DELETE /api/v1/contacts/{id}` - Delete contact
- `GET /api/v1/contacts/search` - Search contacts

### System Operations
- `GET /api/v1/health` - Health check
- `GET /api/v1/stats` - Database statistics
- `GET /api/v1/export/vcf` - Export all contacts

## 🛠️ Maintenance

### View Logs
```bash
docker-compose logs contactplus-core
docker-compose logs contactplus-web
docker-compose logs contactplus-monitor
```

### Restart Services
```bash
docker-compose restart
```

### Stop Services
```bash
docker-compose down
```

### Remove All Data
```bash
docker-compose down -v
```

## 🧪 Testing

### Quick Tests
```bash
# Basic functionality test (30 seconds)
python quick_test.py

# Smoke tests
python test_runner.py --smoke
```

### Comprehensive Testing
```bash
# Full test suite
python test_runner.py

# Specific test categories
python test_runner.py --category integration
python test_runner.py --category e2e
python test_runner.py --category performance

# Generate HTML report
python test_runner.py --report
```

### Test Coverage
- **Integration Tests**: API endpoints, Docker containers
- **End-to-End Tests**: Complete user workflows
- **Performance Tests**: Load testing, stress testing
- **Logging Tests**: Dozzle integration, log rotation

See `TESTING_GUIDE.md` for detailed testing documentation.

## 📝 Features

- ✅ RFC 2426 compliant vCard processing
- ✅ Source tracking for all contacts
- ✅ Full CRUD operations
- ✅ Contact search functionality
- ✅ Export to vCard format
- ✅ Paginated contact browsing
- ✅ Real-time system monitoring
- ✅ Comprehensive logging with Dozzle
- ✅ Docker containerization
- ✅ Complete test suite (100+ tests)

## 🔐 Data Safety

- Original files are never modified
- Complete audit trail of all operations
- Soft delete with recovery options
- Automatic backups before modifications

## 📈 Performance

- Handles 7,000+ contacts efficiently
- Minimal memory usage
- Fast search and filtering
- Responsive web interface

## 🚧 Known Limitations (MVP v1.0)

- No bulk operations
- No duplicate detection
- Basic search only
- No user authentication
- Single-user system

## 📮 Support

For issues or questions, please refer to the documentation or create an issue in the repository.