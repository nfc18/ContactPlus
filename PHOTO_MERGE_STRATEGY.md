# Contact Photo Merge Strategy

## Overview
Contact photos require special handling during merge due to quality variations, duplicates, and storage considerations.

## 1. Photo Quality Assessment

### 1.1 Quality Metrics
1. **Resolution** (pixels)
   - High: >500x500
   - Medium: 200-500
   - Low: <200x200

2. **File Size** (indicates quality)
   - Large: >100KB (usually high quality)
   - Medium: 20-100KB
   - Small: <20KB (often thumbnails)

3. **Format Quality**
   - Best: JPEG high quality, PNG
   - Good: JPEG medium quality
   - Poor: JPEG low quality, heavily compressed

4. **Image Characteristics**
   - Professional photo (good lighting, background)
   - Casual photo (selfie, cropped from group)
   - Avatar/Logo (company logos, cartoon avatars)
   - Generic (default silhouettes)

## 2. Photo Selection Algorithm

### 2.1 Priority Rules (Highest to Lowest)
1. **Professional headshot** from Sara's database
2. **High-resolution photo** (>500x500) from any source
3. **Recent photo** from iPhone Contacts (if metadata available)
4. **Larger file size** when resolution is similar
5. **Any photo** over no photo
6. **Skip generic avatars** (gray silhouettes, initials)

### 2.2 Decision Matrix
```
| Scenario | Sara DB | iPhone Contacts | iPhone Suggested | Action |
|----------|---------|-----------------|------------------|---------|
| Photo in one source only | ✓ | ✗ | ✗ | Use Sara's |
| Different photos | HQ Photo | LQ Photo | ✗ | Use Sara's |
| Different photos | LQ Photo | HQ Photo | ✗ | Use iPhone's |
| Same person, different times | Older | Newer | ✗ | Use newer |
| Company logo vs personal | Logo | Personal | ✗ | Use personal |
```

## 3. Photo Comparison Methods

### 3.1 Duplicate Detection
1. **Exact match**: Compare hash (MD5/SHA)
2. **Visual similarity**: Perceptual hashing
3. **Metadata check**: EXIF data comparison

### 3.2 Quality Comparison
```python
def photo_quality_score(photo):
    score = 0
    
    # Resolution (40 points)
    if width >= 500 and height >= 500:
        score += 40
    elif width >= 200 and height >= 200:
        score += 20
    else:
        score += 5
    
    # File size (30 points)
    if file_size > 100_000:  # >100KB
        score += 30
    elif file_size > 20_000:  # >20KB
        score += 15
    
    # Format (20 points)
    if format in ['PNG', 'JPEG-HQ']:
        score += 20
    elif format == 'JPEG-MQ':
        score += 10
    
    # Type (10 points)
    if is_professional_photo():
        score += 10
    elif not is_generic_avatar():
        score += 5
    
    return score
```

## 4. Special Cases

### 4.1 Multiple Good Photos
When contact has multiple high-quality photos:
- **Option 1**: Keep primary + store alternates in custom field
- **Option 2**: Let user choose during manual review
- **Option 3**: Keep most recent based on metadata

### 4.2 Company Logos vs Personal Photos
- Prefer personal photos for individuals
- Keep company logos only for company contacts
- Flag for review if unclear (e.g., CEO with company logo)

### 4.3 Group Photos
- Avoid cropped faces from group photos (usually low quality)
- Flag for manual review if it's the only photo available

## 5. Storage Optimization

### 5.1 Compression Strategy
- Keep original if <200KB
- Compress if >200KB while maintaining quality
- Target: 100-150KB per photo
- Maintain aspect ratio and minimum 300x300

### 5.2 Format Standardization
- Convert all to JPEG for compatibility
- Keep PNG only for logos/graphics with transparency
- Remove redundant metadata (EXIF location data, camera info)

## 6. Implementation Process

### 6.1 Photo Extraction
```
1. Extract all photos from contacts
2. Calculate quality score for each
3. Group by contact match
4. Apply selection algorithm
```

### 6.2 Decision Log
For each photo decision, log:
- Source database
- Original size/resolution
- Quality score
- Decision made
- Reason

### 6.3 Manual Review Triggers
Flag for review when:
- Multiple high-quality photos (score difference <10)
- Only low-quality options available
- Company logo vs personal photo conflict
- Significant visual difference in photos of same person

## 7. Privacy Considerations

### 7.1 Metadata Removal
- Strip GPS coordinates
- Remove camera/device information
- Keep only essential metadata (date taken if available)

### 7.2 Consent Considerations
- Professional photos (likely consented)
- Social media photos (check usage rights)
- Company directory photos (usually approved)

## 8. Expected Outcomes

From ~7,076 contacts:
- Contacts with photos: ~2,000-2,500
- Unique photos after merge: ~1,800-2,200
- Photos needing review: ~50-100
- Storage saved: ~20-30% through optimization

## 9. Review Interface for Photos

```
PHOTO SELECTION NEEDED
━━━━━━━━━━━━━━━━━━━━━
Contact: John Smith

Option 1 (Sara DB):          Option 2 (iPhone):
[Photo Display]              [Photo Display]
Resolution: 600x600          Resolution: 400x400
Size: 125KB                  Size: 45KB
Type: Professional           Type: Casual
Score: 95/100               Score: 70/100

[USE OPTION 1] [USE OPTION 2] [KEEP BOTH] [SKIP ALL]
```

## 10. Post-Merge Photo Tasks

1. **Verification**: Ensure each contact has max 1 primary photo
2. **Optimization**: Compress oversized photos
3. **Backup**: Keep original photos in backup
4. **Report**: Generate photo merge statistics