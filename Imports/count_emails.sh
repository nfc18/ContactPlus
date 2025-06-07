#\!/bin/bash

awk '
/^BEGIN:VCARD/ { 
    email_count = 0
    contact_name = ""
    emails = ""
}
/^FN:/ { 
    contact_name = substr($0, 4)
}
/EMAIL/ { 
    email_count++
    split($0, parts, ":")
    if (length(parts) >= 2) {
        if (emails \!= "") {
            emails = emails ", "
        }
        emails = emails parts[2]
    }
}
/^END:VCARD/ { 
    if (email_count > 3) {
        if (contact_name == "") {
            contact_name = "Unknown"
        }
        print email_count "\t" contact_name "\t" emails
    }
}
' "$1" | sort -nr
