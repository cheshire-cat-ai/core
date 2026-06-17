# Data Directory

This folder stores all application data including database and files.
Plugin folders should only contain code and static files.

## Directory Structure

```
data/
├── sqlite/                # Database storage
├── uploads/               # Uploaded files
│     └── {user-hash}/     # Per-user private directories
```



