# vCard Database Viewer Design

## Overview
A comprehensive viewer for browsing, searching, and inspecting vCard databases with support for multiple views, filtering, and data quality analysis.

## Core Features

### 1. Multi-View Display Modes

#### Grid View (Photo-Centric)
```
┌─────────────────────────────────────────────────────────────┐
│ Contacts (3,847 total) | Grid View | [Search...] | [Filter] │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐│
│ │ [Photo] │ │ [Photo] │ │   JD    │ │ [Photo] │ │   SM    ││
│ │John Doe │ │Jane Smi │ │Unknown  │ │Bob John │ │Sarah Mi ││
│ │Google   │ │Apple    │ │------   │ │Microsoft│ │Meta     ││
│ │⭐⭐⭐⭐⭐│ │⭐⭐⭐⭐ │ │⭐⭐     │ │⭐⭐⭐⭐ │ │⭐⭐⭐   ││
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘│
│                                                              │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐│
│ │   MJ    │ │ [Photo] │ │   TC    │ │ [Photo] │ │   LD    ││
│ │Mike Jon │ │Lisa Che │ │Tom Clar │ │Amy Wong │ │Luke Dav ││
│ │Amazon   │ │Tesla    │ │------   │ │Uber     │ │Stripe   ││
│ │⭐⭐⭐   │ │⭐⭐⭐⭐⭐│ │⭐       │ │⭐⭐⭐   │ │⭐⭐⭐⭐ ││
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘│
│                                                              │
│ [← Previous] Page 1 of 770 [Next →]                         │
└─────────────────────────────────────────────────────────────┘
```

#### List View (Data-Dense)
```
┌─────────────────────────────────────────────────────────────┐
│ Contacts | List View | ▼ Sort: Last Name | [Search] [Filter]│
├─────────────────────────────────────────────────────────────┤
│ □ │Photo│ Name          │ Company    │ Email    │ Phone    │
├───┼─────┼───────────────┼────────────┼──────────┼──────────┤
│ □ │ 📷  │ Doe, John     │ Google LLC │ john@... │ +1-555...│
│ □ │ --  │ Smith, Jane   │ Apple Inc. │ jane@... │ +1-444...│
│ □ │ 📷  │ Johnson, Bob  │ Microsoft  │ bob@...  │ +1-333...│
│ □ │ --  │ Unknown       │ ------     │ unk@...  │ ------   │
│ □ │ 📷  │ Chen, Lisa    │ Tesla      │ lisa@... │ +1-222...│
│ □ │ --  │ Miller, Sarah │ Meta       │ sarah@.. │ +1-111...│
├───┴─────┴───────────────┴────────────┴──────────┴──────────┤
│ Selected: 0 | Showing 1-20 of 3,847 | [Load More]           │
└─────────────────────────────────────────────────────────────┘
```

#### Card View (Detailed)
```
┌─────────────────────────────────────────────────────────────┐
│ John Doe - Contact Details              [Edit] [Delete] [X] │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────┐  John Michael Doe                              │
│ │ [Photo] │  Senior Software Engineer                       │
│ │         │  Google LLC                                     │
│ └─────────┘  Mountain View, CA                              │
│                                                             │
│ 📧 Emails:                    📱 Phones:                    │
│   • john.doe@gmail.com         • +1-555-123-4567 (Mobile)  │
│   • jdoe@google.com (Work)     • +1-555-987-6543 (Work)    │
│                                                             │
│ 🏢 Address:                   🔗 Links:                     │
│   1600 Amphitheatre Pkwy      • linkedin.com/in/johndoe    │
│   Mountain View, CA 94043      • github.com/johndoe         │
│                                • twitter.com/johndoe         │
│ 📝 Notes:                                                   │
│   Met at Google I/O 2023. Interested in AI/ML projects.    │
│                                                             │
│ 📊 Metadata:                                                │
│   • Added: 2023-05-15         • Source: LinkedIn Import    │
│   • Modified: 2024-02-20      • Rating: ⭐⭐⭐⭐⭐ (92/100)  │
│   • Last Contact: 2024-03-01  • vCard Version: 4.0         │
│                                                             │
│ [← Previous Contact] [Next Contact →]                       │
└─────────────────────────────────────────────────────────────┘
```

### 2. Advanced Search & Filtering

#### Search Interface
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 Search Contacts                                          │
├─────────────────────────────────────────────────────────────┤
│ Query: [John engineer Google        ] [Search] [Clear]      │
│                                                             │
│ Quick Filters:                                              │
│ ☑ Has Photo  ☐ Has Phone  ☑ Has Email  ☐ Has Address      │
│ ☐ Duplicates ☐ Incomplete ☐ Recently Added ☐ VIP           │
│                                                             │
│ Advanced Filters:                    [+ Add Filter]         │
│ • Company contains "Google" OR "Alphabet"                   │
│ • Rating >= 80                                              │
│ • Added after 2023-01-01                                   │
│                                                             │
│ Sort by: [Relevance ▼] then [Last Name ▼]                  │
│                                                             │
│ Found 127 matches                    [Export] [Save Search] │
└─────────────────────────────────────────────────────────────┘
```

### 3. Data Quality Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│ Database Quality Report - contacts.vcf                      │
├─────────────────────────────────────────────────────────────┤
│ Overview:                                                   │
│ • Total Contacts: 3,847                                     │
│ • Unique Contacts: 3,421 (426 potential duplicates)        │
│ • Average Completeness: 67%                                 │
│ • Last Modified: 2024-12-15                                │
│                                                             │
│ Data Quality Issues:              Actions:                  │
│ ⚠️ 426 Potential Duplicates      [Review Duplicates]       │
│ ⚠️ 892 Missing Phone Numbers     [View Affected]           │
│ ⚠️ 234 Missing Email Addresses   [View Affected]           │
│ ⚠️ 1,203 No Photo                [View Affected]           │
│ ⚠️ 67 Invalid Email Formats      [Fix Automatically]       │
│ ⚠️ 145 Phone Numbers in Notes    [Extract & Fix]           │
│                                                             │
│ Field Coverage:                                   Usage:    │
│ Name:     ████████████████████ 98%   Photos:    ██░░ 31% │
│ Email:    ████████████░░░░░░░ 72%   Address:   ██░░ 23% │
│ Phone:    ████████░░░░░░░░░░░ 45%   Company:   ████ 67% │
│ Notes:    ██████░░░░░░░░░░░░░ 34%   Birthday:  █░░░ 12% │
│                                                             │
│ [Generate Full Report] [Export Issues CSV]                  │
└─────────────────────────────────────────────────────────────┘
```

### 4. Comparison View

```
┌─────────────────────────────────────────────────────────────┐
│ Database Comparison                                         │
├─────────────────────────────────────────────────────────────┤
│ Database A: iPhone_Contacts.vcf    | Stats:                │
│ Database B: LinkedIn_Export.vcf    | • A only: 1,234      │
│                                   | • B only: 2,103      │
│ ┌─────────────┬─────────────┐    | • Both: 510          │
│ │ A Only      │ Both        │    | • Total: 3,847       │
│ │ ┌─────┐     │ ┌─────┐     │    |                      │
│ │ │John │     │ │Jane │     │    | Overlap Analysis:    │
│ │ │Doe  │     │ │Smith│     │    | • By Email: 423      │
│ │ └─────┘     │ └─────┘     │    | • By Phone: 287      │
│ │             │             │    | • By Name: 510       │
│ │ 1,234       │ 510 contacts│    |                      │
│ │ contacts    │             │    | Quality Comparison:  │
│ │             │ ┌─────┐     │    | A Completeness: 72%  │
│ │ ┌─────┐     │ │Bob  │     │    | B Completeness: 84%  │
│ │ │Sarah│     │ │Jones│     │    |                      │
│ │ │Mill │     │ └─────┘     │    | [Merge Databases]    │
│ │ └─────┘     │ B Only      │    | [Export Unique]      │
│ │             │ 2,103       │    | [Export Overlap]     │
│ └─────────────┴─────────────┘    |                      │
└─────────────────────────────────────────────────────────────┘
```

### 5. Timeline View

```
┌─────────────────────────────────────────────────────────────┐
│ Contact Timeline                    [Month ▼] [2024 ▼]     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ December 2024                                               │
│ ├─ 15th: 45 contacts added (LinkedIn Import)               │
│ ├─ 12th: 23 contacts modified                              │
│ ├─ 10th: 12 contacts added (iPhone Sync)                   │
│ └─ 8th:  67 contacts merged                                │
│                                                             │
│ November 2024                                               │
│ ├─ 28th: 134 contacts added (Gmail Import)                 │
│ ├─ 20th: Email cleanup performed (89 contacts)             │
│ └─ 15th: 34 duplicates removed                             │
│                                                             │
│ October 2024                                                │
│ ├─ 31st: 256 contacts rated                                │
│ └─ 22nd: Initial import (2,341 contacts)                   │
│                                                             │
│ [Show Details] [Export Timeline]                            │
└─────────────────────────────────────────────────────────────┘
```

## Technical Implementation

### 1. Backend Architecture

```python
class VCardDatabaseViewer:
    def __init__(self, database_path):
        self.db = VCardDatabase(database_path)
        self.cache = ContactCache()
        self.search_engine = SearchEngine()
    
    def get_contacts_page(self, page=1, per_page=20, filters=None):
        """Get paginated contacts with optional filters"""
        query = self.db.query()
        
        if filters:
            query = self.apply_filters(query, filters)
        
        total = query.count()
        contacts = query.offset((page-1)*per_page).limit(per_page).all()
        
        return {
            'contacts': contacts,
            'total': total,
            'page': page,
            'pages': math.ceil(total/per_page)
        }
    
    def search_contacts(self, query_string, filters=None):
        """Full-text search across all contact fields"""
        results = self.search_engine.search(query_string)
        
        if filters:
            results = self.apply_filters(results, filters)
        
        return results
```

### 2. Frontend Components

#### React-based Web Interface
```javascript
const ContactViewer = () => {
    const [view, setView] = useState('grid');
    const [contacts, setContacts] = useState([]);
    const [filters, setFilters] = useState({});
    
    const ViewComponents = {
        grid: GridView,
        list: ListView,
        card: CardView,
        timeline: TimelineView
    };
    
    const CurrentView = ViewComponents[view];
    
    return (
        <div className="contact-viewer">
            <ViewSelector value={view} onChange={setView} />
            <FilterBar filters={filters} onChange={setFilters} />
            <CurrentView 
                contacts={contacts}
                onContactSelect={handleContactSelect}
            />
        </div>
    );
};
```

#### Electron Desktop App
```javascript
// main.js - Electron main process
const { app, BrowserWindow } = require('electron');

function createWindow() {
    const win = new BrowserWindow({
        width: 1400,
        height: 900,
        webPreferences: {
            nodeIntegration: true
        }
    });
    
    win.loadFile('index.html');
    
    // Native file handling
    win.webContents.on('will-navigate', (event, url) => {
        if (url.endsWith('.vcf')) {
            event.preventDefault();
            loadVCardFile(url);
        }
    });
}
```

### 3. Performance Optimization

#### Lazy Loading & Virtualization
```javascript
const VirtualizedContactList = () => {
    return (
        <VirtualList
            height={800}
            itemCount={contacts.length}
            itemSize={80}
            renderItem={({ index, style }) => (
                <ContactRow 
                    contact={contacts[index]} 
                    style={style}
                />
            )}
        />
    );
};
```

#### Search Index
```python
class SearchIndex:
    def __init__(self):
        self.index = Whoosh.create_index(schema=ContactSchema)
    
    def build_index(self, contacts):
        """Build search index for fast queries"""
        writer = self.index.writer()
        for contact in contacts:
            writer.add_document(
                id=contact.id,
                name=contact.name,
                email=' '.join(contact.emails),
                phone=' '.join(contact.phones),
                company=contact.company,
                notes=contact.notes
            )
        writer.commit()
```

## UI/UX Features

### 1. Keyboard Navigation
- `j/k` - Navigate up/down
- `Enter` - Open contact details
- `/` - Focus search
- `g` then `g` - Go to grid view
- `g` then `l` - Go to list view
- `?` - Show keyboard shortcuts

### 2. Bulk Operations
```
┌─────────────────────────────────────────────────────────────┐
│ 23 contacts selected          [Select All] [Clear]          │
├─────────────────────────────────────────────────────────────┤
│ Bulk Actions:                                               │
│ [Export Selected] [Delete] [Add Tag] [Merge] [Rate]         │
└─────────────────────────────────────────────────────────────┘
```

### 3. Quick Actions Menu
- Right-click on any contact
- Quick edit fields
- Copy contact info
- Send email
- Add to favorites

### 4. Smart Grouping
```
Group by: [Company ▼]

▼ Google (127 contacts)
  • John Doe
  • Jane Smith
  • Bob Johnson

▼ Apple (89 contacts)
  • Lisa Chen
  • Mike Davis

▼ No Company (1,245 contacts)
  • Sarah Miller
  • Tom Wilson
```

## Export Capabilities

### 1. Multiple Formats
- vCard 3.0/4.0
- CSV with custom fields
- JSON for APIs
- PDF contact sheets
- Excel with formatting

### 2. Smart Export Options
```python
def export_contacts(contacts, format='vcard', options={}):
    """Export with intelligent options"""
    if format == 'vcard':
        # Option to split large files
        if options.get('split_size'):
            return export_vcard_split(contacts, options['split_size'])
        
        # Option to exclude fields
        if options.get('exclude_fields'):
            contacts = filter_fields(contacts, options['exclude_fields'])
    
    return exporters[format](contacts, options)
```

## Integration Features

### 1. Live Sync
- Watch file changes
- Auto-reload on external modifications
- Conflict detection

### 2. External Tools
- Open in native contacts app
- Send to CRM
- Share via email
- Print contact cards

## Mobile Companion App

### Progressive Web App
- Responsive design
- Offline support
- Camera for business cards
- Share contacts via QR

## Recommended Implementation

### Phase 1: Core Viewer
1. Build data layer with SQLite cache
2. Implement basic grid/list views
3. Add search and filtering
4. Create contact detail view

### Phase 2: Advanced Features
1. Add timeline view
2. Implement quality dashboard
3. Build comparison tools
4. Add bulk operations

### Phase 3: Polish
1. Keyboard navigation
2. Export options
3. Performance optimization
4. Mobile support

The viewer provides comprehensive browsing capabilities while maintaining performance with large databases through virtualization and smart caching.