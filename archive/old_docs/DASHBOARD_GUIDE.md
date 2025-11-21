# Rwanda NCSA Compliance Monitoring Dashboard

Real-time compliance monitoring dashboard with AI-powered log classification and SHAP-based explainability.

## Features

### 1. Real-time Monitor
- **Live log simulation**: Simulate log events from test data
- **Real-time classification**: Instant compliance/non-compliance prediction
- **Alert system**: Automatic alerts for non-compliant events
- **Severity tracking**: Critical, high, and medium severity classifications
- **Metrics overview**: Compliance rate, total logs, critical alerts

### 2. Single Log Analysis
- **Custom log input**: Analyze any log message manually
- **SHAP explanations**: See which features influenced the prediction
- **Feature impact visualization**: Interactive charts showing feature contributions
- **Confidence scores**: Model confidence for each prediction

### 3. Historical Analysis
- **Compliance trends**: Track compliance rate over time
- **Control breakdown**: Identify which controls have most violations
- **Severity distribution**: Pie charts showing severity levels
- **Time-based analytics**: Hourly and daily compliance patterns

### 4. Control Explorer
- **NIST SP 800-53 controls**: Browse all 29 NIST controls
- **Rwanda NCSA controls**: Browse all 21 Rwanda controls
- **Family filtering**: Filter controls by family (Access Control, Audit, etc.)
- **Control details**: View definitions, log indicators, and mappings

## Installation

### Prerequisites
- Python 3.10+
- Trained XGBoost model with SHAP explanations

### Quick Start

```bash
# 1. Install dependencies
pip install -r dashboard/requirements.txt

# 2. Make launch script executable
chmod +x dashboard/run_dashboard.sh

# 3. Launch dashboard
./dashboard/run_dashboard.sh
```

The dashboard will open automatically at http://localhost:8501

## Dashboard Architecture

```
dashboard/
├── compliance_monitor.py     # Main dashboard application
├── requirements.txt          # Dashboard dependencies
└── run_dashboard.sh         # Launch script

ComplianceDashboard Class:
├── __init__()               # Load models and initialize state
├── render_header()          # Dashboard header
├── render_sidebar()         # Control panel sidebar
├── render_metrics_overview() # Metrics cards
├── render_realtime_monitor() # Real-time monitoring view
├── render_single_log_analysis() # Single log analysis view
├── render_historical_analysis() # Historical analytics view
└── render_control_explorer() # Control reference view
```

## Usage Guide

### Real-time Monitor

1. **Start monitoring**:
   - Click "🔄 Simulate New Log Event" to analyze logs
   - Adjust "# Events" to simulate multiple logs at once
   - Enable "Auto-refresh" in sidebar for continuous monitoring

2. **View predictions**:
   - Recent predictions appear in timeline format
   - ✅ Green cards = Compliant
   - ⚠️ Red cards = Non-compliant
   - Click "🔍 Explain" to see SHAP analysis

3. **Monitor metrics**:
   - Top cards show: Total logs, Compliant, Non-compliant, Critical alerts
   - Sidebar shows session statistics

### Single Log Analysis

1. **Enter log details**:
   - Paste log message in text area
   - Enter source IP and user (optional)
   - Click "🔍 Analyze Log"

2. **Review results**:
   - Prediction (Compliant/Non-compliant)
   - Confidence score
   - Top contributing features
   - Feature impact visualization

3. **Interpret SHAP values**:
   - **Positive SHAP values** → Push toward non-compliant
   - **Negative SHAP values** → Push toward compliant
   - Larger absolute values = stronger influence

### Historical Analysis

1. **View compliance trends**:
   - Line chart shows compliance rate over time
   - Orange dashed line = 75% target

2. **Analyze violations**:
   - Bar chart shows top 10 controls with violations
   - Pie charts show severity distribution

3. **Export data** (coming soon):
   - Download compliance reports
   - Export predictions to CSV

### Control Explorer

1. **Browse controls**:
   - Filter by family (Access Control, Audit, etc.)
   - View all NIST SP 800-53 and Rwanda NCSA controls

2. **View control details**:
   - Select control from dropdown
   - See definition, log indicators, NIST mappings

## Technical Details

### Model Integration
- **Classifier**: XGBoost (95.99% accuracy, 98.54% recall)
- **Explainer**: SHAP TreeExplainer for fast, exact explanations
- **Features**: 1003 features (1000 TF-IDF + 3 metadata)

### Performance
- **Prediction speed**: ~50ms per log
- **SHAP calculation**: ~200ms per explanation
- **Dashboard refresh**: Configurable (1-60 seconds)

### Data Flow

```
User Input (Log Message)
    ↓
Feature Engineering (TF-IDF + Metadata)
    ↓
XGBoost Prediction (Compliant/Non-compliant)
    ↓
SHAP Explanation (Feature contributions)
    ↓
Dashboard Visualization
```

### Session State Management

Streamlit session state stores:
- `classifier`: Loaded XGBoost model
- `explainer`: Loaded SHAP explainer
- `test_df`: Test data for simulation
- `prediction_history`: List of all predictions
- `alert_count`: Count of non-compliant alerts

## SHAP Interpretation Guide

### Global Feature Importance
- Shows which features matter most across all predictions
- Based on mean absolute SHAP value
- Top 20 features displayed

### Force Plot
- Shows how features push prediction toward one class
- **Red bars**: Push toward non-compliant
- **Blue bars**: Push toward compliant
- Bar length = strength of contribution

### Dependence Plot
- Shows relationship between feature value and SHAP value
- Linear relationship = simple feature impact
- Non-linear = complex interactions

## Customization

### Change Port
Edit `dashboard/run_dashboard.sh`:
```bash
--server.port 8080  # Change from 8501 to 8080
```

### Change Theme
Edit `dashboard/run_dashboard.sh`:
```bash
--theme.primaryColor "#ff0000"  # Change colors
--theme.backgroundColor "#000000"
```

### Add Custom Controls
Edit `src/data_pipeline/control_mapper.py`:
```python
self.controls['CUSTOM-1'] = {
    'name': 'Custom Control',
    'family': 'Custom Family',
    ...
}
```

## Troubleshooting

### Error: "XGBoost model not found"
**Solution**: Run model training first
```bash
python retrain_xgboost_with_shap.py
```

### Error: "ModuleNotFoundError: No module named 'streamlit'"
**Solution**: Install dependencies
```bash
pip install -r dashboard/requirements.txt
```

### Dashboard won't start
**Solution**: Check if port 8501 is available
```bash
lsof -i :8501  # Check port usage
killall streamlit  # Kill existing Streamlit processes
```

### Slow performance
**Solution**:
- Reduce auto-refresh interval
- Clear prediction history
- Limit simulation batch size

## Deployment

### Local Development
```bash
./dashboard/run_dashboard.sh
```

### Production Deployment

**Option 1: Streamlit Cloud**
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Deploy from repository

**Option 2: Docker**
```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "dashboard/compliance_monitor.py"]
```

**Option 3: Server with Nginx**
```bash
# Run Streamlit
streamlit run dashboard/compliance_monitor.py --server.port 8501

# Configure Nginx reverse proxy
# /etc/nginx/sites-available/compliance-monitor
server {
    listen 80;
    server_name compliance.rwanda-ncsa.gov.rw;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Security Considerations

### Authentication
Add authentication for production:
```python
# Option 1: Simple password
password = st.text_input("Password", type="password")
if password != "your_secure_password":
    st.stop()

# Option 2: OAuth (recommended)
# Use streamlit-authenticator package
```

### Data Privacy
- Don't log sensitive user data
- Sanitize log messages before display
- Use HTTPS in production
- Implement role-based access control

### API Security
- Add API key authentication
- Rate limiting for predictions
- Input validation and sanitization

## Performance Optimization

### Caching
Already implemented:
- Model loaded once per session
- SHAP explainer cached
- Test data cached

### Future Optimizations
- [ ] Batch prediction API
- [ ] Redis cache for predictions
- [ ] Background job queue
- [ ] Database for prediction history

## Roadmap

### Phase 1 (Current)
- ✅ Real-time monitoring
- ✅ Single log analysis
- ✅ Historical analytics
- ✅ Control explorer

### Phase 2 (Next)
- [ ] Export compliance reports (PDF, CSV)
- [ ] Email alerts for critical violations
- [ ] Custom alert thresholds
- [ ] User management

### Phase 3 (Future)
- [ ] API integration
- [ ] Database backend
- [ ] Multi-tenant support
- [ ] Advanced analytics (anomaly detection)

## Support

For issues or questions:
1. Check this guide
2. Review `TROUBLESHOOTING.md`
3. Contact: Moise Iradukunda (CMU)

## License

MIT License - See LICENSE file for details

---

**Rwanda NCSA Compliance Monitor**
Powered by XGBoost + SHAP
Built with Streamlit
October 2025
