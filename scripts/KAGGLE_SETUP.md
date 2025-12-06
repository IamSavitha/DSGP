# Kaggle API Setup Guide

## Option 1: Set Up Kaggle API (If You Want to Use Kaggle Datasets)

### Step 1: Get Your Kaggle API Credentials

1. **Go to Kaggle**: https://www.kaggle.com/
2. **Sign in** or create an account
3. **Go to Account Settings**: 
   - Click your profile picture (top right)
   - Click "Account"
   - Scroll down to "API" section
4. **Create API Token**:
   - Click "Create New Token"
   - This downloads a file called `kaggle.json`

### Step 2: Create the Kaggle Directory and File

**On macOS/Linux:**
```bash
# Create the .kaggle directory (if it doesn't exist)
mkdir -p ~/.kaggle

# Move the downloaded kaggle.json file to ~/.kaggle/
mv ~/Downloads/kaggle.json ~/.kaggle/kaggle.json

# Set proper permissions (required by Kaggle API)
chmod 600 ~/.kaggle/kaggle.json
```

**On Windows:**
```powershell
# Create the .kaggle directory
mkdir C:\Users\YourUsername\.kaggle

# Copy the downloaded kaggle.json file to C:\Users\YourUsername\.kaggle\
copy Downloads\kaggle.json C:\Users\YourUsername\.kaggle\kaggle.json
```

### Step 3: Verify the File Exists

```bash
# Check if file exists
ls -la ~/.kaggle/kaggle.json

# View contents (should show your username and key)
cat ~/.kaggle/kaggle.json
```

The file should look like:
```json
{"username":"your-username","key":"your-api-key-here"}
```

### Step 4: Install Kaggle Package

```bash
pip install kaggle pandas
```

---

## Option 2: Use the Script WITHOUT Kaggle (Recommended for Now)

**Good news!** The seeding script works perfectly fine **without Kaggle**. It generates realistic sample data automatically.

### Just Run the Script:

```bash
# The script will generate realistic data without needing Kaggle
python3 scripts/seed_travel_data.py
```

The script includes:
- ✅ Real airline codes and names
- ✅ Major US airports with realistic routes
- ✅ Popular hotel chains
- ✅ Real car makes and models
- ✅ Realistic pricing calculations

**You don't need Kaggle for this!** The script generates all the data you need.

---

## Option 3: Manual Data Entry (If You Have Specific Data)

If you have CSV files or other data sources, you can modify the script to load them:

```python
import pandas as pd

def load_custom_data(csv_file):
    """Load data from your own CSV file."""
    df = pd.read_csv(csv_file)
    # Process and seed data
    return df
```

---

## Troubleshooting

### Issue: "No module named 'kaggle'"
**Solution**: Install it: `pip install kaggle pandas`

### Issue: "403 Forbidden" when using Kaggle API
**Solution**: 
- Check your API token is valid
- Ensure `kaggle.json` has correct permissions (600)
- Verify your Kaggle account is active

### Issue: "File not found: ~/.kaggle/kaggle.json"
**Solution**: 
- Create the directory: `mkdir -p ~/.kaggle`
- Download API token from Kaggle
- Place it in `~/.kaggle/kaggle.json`

---

## Recommendation

**For now, just use the script without Kaggle!** It generates plenty of realistic data (100 flights, 50 hotels, 75 cars) without needing any external data sources.

You can always add Kaggle integration later if you want more data or specific datasets.

