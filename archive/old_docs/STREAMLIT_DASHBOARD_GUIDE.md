# Streamlit Dashboard Guide

## Launch Instructions

The dashboard is now running and accessible at:

- **Network URL**: http://192.168.1.64:8501
- **External URL**: http://102.22.186.236:8501

### To Launch Manually:

```bash
cd "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine"
source venv/bin/activate
streamlit run src/ui/streamlit_dashboard.py
```

---

## Features

### 1. Rwanda Flag Color Scheme
The dashboard uses Rwanda's national colors throughout:
- **Blue** (#00A1DE): Primary accent, metrics
- **Yellow** (#FAD201): Non-compliant events, warnings
- **Green** (#20AA47): Compliant events, success
- **Dark Blue** (#003DA5): Headers, dark elements

### 2. Three Operation Modes

#### Mode 1: Batch Analysis
- **Purpose**: Analyze multiple compliance events at once
- **Features**:
  - Upload CSV or use test data
  - Compliance distribution pie chart
  - Confidence distribution histogram
  - Summary statistics
  - Most uncertain predictions

#### Mode 2: Single Event Explanation
- **Purpose**: Deep dive into why a specific event was classified
- **Features**:
  - Select event by index
  - Full SHAP explanation
  - Top 15 features influencing decision
  - Visual waterfall plot
  - Feature contribution bar chart
  - Model reasoning breakdown

#### Mode 3: Custom Log Test
- **Purpose**: Test your own log messages
- **Features**:
  - Enter any log message
  - Real-time prediction
  - Confidence score
  - SHAP explanation
  - Feature contributions

---

## How to Use

### Batch Analysis Mode

1. Select "📊 Batch Analysis" from sidebar
2. Choose data source:
   - Use test data (default)
   - Upload your own CSV
3. Set number of samples (1-1000)
4. View results:
   - Metric cards showing totals
   - Pie chart of compliance distribution
   - Histogram of confidence levels
   - Table of most uncertain predictions

### Single Event Explanation Mode

1. Select "🔍 Single Event Explanation" from sidebar
2. Enter event index (0 to 15540 for test data)
3. View detailed explanation:
   - **Prediction**: Compliant or Non-Compliant
   - **Confidence**: Percentage confidence
   - **Top Features**: 15 most influential features
   - **SHAP Values**: Impact direction and strength
   - **Waterfall Plot**: Visual representation of decision
   - **Model Reasoning**: Base value + contributions

### Custom Log Test Mode

1. Select "💬 Custom Log Test" from sidebar
2. Choose a control ID or use default
3. Enter your log message in text area
4. Click "Analyze Log Message"
5. View prediction and explanation

---

## Understanding the Results

### Prediction Labels
- **COMPLIANT** (Green): Event follows security policies
- **NON-COMPLIANT** (Yellow): Event violates security policies

### Confidence Scores
- **High (>80%)**: Model is very confident
- **Medium (60-80%)**: Moderate confidence
- **Low (<60%)**: Uncertain prediction, needs review

### SHAP Values
- **Positive SHAP** (Red): Pushes toward NON-COMPLIANT
- **Negative SHAP** (Green): Pushes toward COMPLIANT
- **Larger absolute value**: Stronger influence

### Top Features

Features are ranked by absolute SHAP value:

1. **word:'keyword'** - TF-IDF features from log message
   - Example: word:'unauthorized' → strong signal for non-compliance

2. **control_id** - NIST control being monitored
   - Example: AC-3 (Access Control) vs AU-6 (Audit)

3. **control_family** - Control category
   - Example: SI-4 (System Monitoring) → higher risk

4. **framework** - Compliance framework
   - Example: MITRE ATT&CK → attack patterns

5. **temporal features** - Time-based patterns
   - hour_of_day: After-hours activity
   - business_hours: 0 (off-hours) → higher suspicion

---

## Example Scenarios

### Scenario 1: Detecting Data Exfiltration

**Log Message**:
```
Unauthorized wire transfer of $50000 to external account ACC789 denied by fraud detection system
```

**Expected Result**:
- Prediction: NON-COMPLIANT
- Confidence: >95%
- Top Features:
  1. word:'unauthorized' (+0.34)
  2. word:'denied' (+0.21)
  3. word:'fraud' (+0.19)

### Scenario 2: Normal Login

**Log Message**:
```
User login successful - authentication completed via SSO for employee_id_12345
```

**Expected Result**:
- Prediction: COMPLIANT
- Confidence: >90%
- Top Features:
  1. word:'successful' (-0.28)
  2. word:'completed' (-0.15)
  3. business_hours=1 (-0.12)

### Scenario 3: Suspicious After-Hours Activity

**Log Message**:
```
Database administrator accessed customer records at 2:30 AM - 500 records retrieved
```

**Expected Result**:
- Prediction: NON-COMPLIANT
- Confidence: 70-85%
- Top Features:
  1. hour_of_day=2 (+0.22)
  2. business_hours=0 (+0.18)
  3. control_id=AC-3 (+0.14)

---

## Metrics Cards

### Total Events
- Displays total number of events analyzed
- Blue gradient background

### Compliant Events
- Count and percentage of compliant events
- Green gradient (success)
- Target: ~75% in test data

### Non-Compliant Events
- Count and percentage of non-compliant events
- Yellow gradient (warning)
- Target: ~25% in test data

### Average Confidence
- Mean confidence across all predictions
- Blue gradient
- Expected: >85% for good model performance

---

## Troubleshooting

### Dashboard won't load
```bash
# Check if port 8501 is already in use
lsof -i :8501

# Kill existing process
kill -9 <PID>

# Restart dashboard
streamlit run src/ui/streamlit_dashboard.py
```

### Model loading error
```bash
# Verify model exists
ls -la results/models/xgboost_no_leakage/xgboost_model_no_leakage/

# Check model metrics
cat results/models/xgboost_no_leakage/metrics_no_leakage.json
```

### Data not found
```bash
# Verify test data exists
ls -la data/combined_compliance/compliance_events_test.csv

# Check data size
wc -l data/combined_compliance/compliance_events_test.csv
```

### SHAP explanation error
- Make sure the event data does NOT contain leaky features
- Leaky features: status_code, anomaly_label, severity
- These are automatically removed by the dashboard

---

## Performance Notes

### Loading Time
- **First load**: 10-15 seconds (model loading + SHAP initialization)
- **Subsequent predictions**: <1 second
- **Batch analysis (100 events)**: 2-3 seconds

### Memory Usage
- **Model**: ~50 MB
- **SHAP explainer**: ~100 MB
- **Total**: ~200-300 MB
- **Recommended RAM**: 2 GB minimum

### Optimization Tips

1. **For faster startup**: Pre-load model in background
2. **For large batches**: Process in chunks of 1000
3. **For better performance**: Install watchdog module:
   ```bash
   pip install watchdog
   ```

---

## Production Deployment

### Local Network Access
- Use Network URL: http://192.168.1.64:8501
- Accessible from devices on same network

### External Access
- Use External URL: http://102.22.186.236:8501
- Requires firewall configuration

### Cloud Deployment Options

#### Streamlit Cloud (Free)
```bash
# Deploy to Streamlit Cloud
# 1. Push code to GitHub
# 2. Connect repo at share.streamlit.io
# 3. Auto-deploy on push
```

#### Docker Container
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "src/ui/streamlit_dashboard.py"]
```

#### AWS/Azure/GCP
- Deploy as web service
- Use load balancer for high traffic
- Enable HTTPS with SSL certificate

---

## Security Considerations

### Authentication
- Add authentication for production use
- Consider Streamlit authentication libraries
- Integrate with SSO (SAML, OAuth)

### Data Privacy
- Ensure log data doesn't contain PII
- Redact sensitive information
- Use encryption for data transmission

### Access Control
- Restrict to authorized security analysts
- Log all user actions
- Monitor for misuse

---

## Support

### Files Reference
- **Dashboard**: `src/ui/streamlit_dashboard.py`
- **Model**: `results/models/xgboost_no_leakage/xgboost_model_no_leakage/`
- **Test Data**: `data/combined_compliance/compliance_events_test.csv`
- **CLI Version**: `explain_predictions_cli.py`

### Documentation
- **Model Status**: `FINAL_MODEL_STATUS.md`
- **Data Leakage Investigation**: `DATA_LEAKAGE_FINDINGS.md`
- **Installation**: `INSTALLATION.md`

### Testing
- **Adversarial Tests**: `test_adversarial_scenarios.py`
- **Data Leakage Proof**: `prove_data_leakage.py`
- **Quick Demo**: `demo_explainability.py`

---

## Next Steps

1. **Test the Dashboard**
   - Open in browser: http://192.168.1.64:8501
   - Try all three modes
   - Verify Rwanda colors display correctly

2. **Customize**
   - Add your own logo
   - Modify color scheme if needed
   - Add additional metrics

3. **Deploy to Production**
   - Set up authentication
   - Configure HTTPS
   - Monitor performance

4. **Integrate with SIEM**
   - Connect to log sources
   - Set up real-time alerts
   - Create automated workflows

---

**Dashboard Status**: ✅ RUNNING
**Access URL**: http://192.168.1.64:8501
**Model**: xgboost_no_leakage (99.09% accuracy)
**Features**: Full SHAP explainability + Rwanda flag colors

*Generated: October 29, 2025*
