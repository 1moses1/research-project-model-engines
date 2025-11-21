# 🚀 Quick Start: Rwanda NCSA Compliance Dashboard

## Launch in 3 Steps

### Step 1: Activate Environment
```bash
cd "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine"
source venv/bin/activate
```

### Step 2: Launch Dashboard
```bash
./dashboard/run_dashboard.sh
```

### Step 3: Open Browser
```
Dashboard URL: http://localhost:8501
```

---

## 🎨 What to Expect

### Visual Design
- **Header**: Rwanda flag gradient (Blue → Green → Yellow)
- **Buttons**: Blue-to-green Rwanda gradient
- **Compliant Events**: Rwanda green cards
- **Non-compliant Events**: Red alert cards
- **Warnings**: Rwanda yellow cards
- **Sidebar**: Dark Rwanda blue

### Features
1. **Real-time Monitor**: Simulate log events with instant classification
2. **Single Log Analysis**: Analyze custom logs with SHAP explanations
3. **Historical Analysis**: View compliance trends over time
4. **Control Explorer**: Browse 50+ NIST/Rwanda controls

---

## 🔧 Troubleshooting

### Dashboard won't start?
```bash
# Ensure model exists
ls results/explainability/xgboost_model

# If not found:
python retrain_xgboost_with_shap.py
```

### Port already in use?
```bash
# Kill existing Streamlit
killall streamlit

# Retry
./dashboard/run_dashboard.sh
```

---

## 📖 Quick Tour

### 1. Try Real-time Monitor
- Select "Real-time Monitor" from sidebar
- Click "🔄 Simulate New Log Event"
- Watch predictions appear with Rwanda flag colors
- Click "🔍 Explain" to see SHAP analysis

### 2. Analyze Custom Log
- Select "Single Log Analysis"
- Enter: "User admin failed login from 192.168.1.100"
- Click "🔍 Analyze Log"
- View prediction with SHAP explanation

### 3. Browse Controls
- Select "Control Explorer"
- Browse 29 NIST + 21 Rwanda controls
- Filter by family (Access Control, Audit, etc.)
- View detailed control definitions

---

## 🇷🇼 Rwanda Flag Colors

- **Blue (#00A1DE)**: Peace & stability
- **Yellow (#FAD201)**: Economic development
- **Green (#00A651)**: Hope & prosperity

These colors are applied throughout:
- Headers, buttons, tabs
- Cards (green=compliant, yellow=warning)
- Progress bars, scrollbars
- Sidebar navigation

---

## ✅ Status

- ✅ Dashboard complete with Rwanda colors
- ✅ XGBoost integration (95.99% accuracy)
- ✅ SHAP explainability enabled
- ✅ 4 operational modes
- ✅ 50+ compliance controls
- ✅ Professional UI design

**Ready to use!** 🎉

---

For full documentation, see:
- `dashboard/README.md` - Complete user guide
- `DASHBOARD_GUIDE.md` - Technical documentation
- `RWANDA_COLORS_APPLIED.md` - Color scheme details
