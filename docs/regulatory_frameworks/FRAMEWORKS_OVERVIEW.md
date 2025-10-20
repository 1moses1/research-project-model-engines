# Regulatory Frameworks Overview

## Rwanda Cybersecurity Standards

### 1. NCSA Minimum Cybersecurity Standards for Essential Service Providers (ESPs)
**Document**: `Minimum_Cybersecurity_Standards_for_ESPs.pdf`
**Introduced**: July 2023
**Coverage**: Essential Service Providers

**Key Requirements**:
- Risk assessments
- System integrity and access control measures
- Incident response capabilities
- Tiered approach based on criticality
- Regular compliance reviews

**Control Categories**:
1. Access Control (AC)
2. System Hardening
3. Vulnerability Management
4. Incident Response
5. Audit and Logging
6. Data Protection

---

### 2. Minimum Cybersecurity Standards for Public Institutions
**Document**: `Minimum_Cybersecurity_Standards_for_Public_Institutions.pdf`
**Scope**: Government agencies and public sector organizations

**Key Areas**:
- Asset management
- Security policies and procedures
- Personnel security
- Physical security
- Network security
- Business continuity

---

### 3. Minimum Cybersecurity Standards for Financial Sector
**Document**: `Minimum_Cybersecurity_Standards_for_the_Financial_Sector_.pdf`
**Scope**: Banks, insurance companies, payment processors

**Enhanced Requirements**:
- Transaction security
- Fraud detection
- Customer data protection
- Third-party risk management
- Regulatory reporting

---

### 4. Cyber Crimes Law
**Document**: `Cyber_Crimes_Law__2_.pdf`
**Purpose**: Legal framework for cybercrime prosecution

**Relevant Provisions**:
- Unauthorized access
- Data breach penalties
- Compliance obligations
- Evidence requirements

---

### 5. Law Establishing NCSA
**Document**: `Law_establishing_the__NCSA__1_.pdf`
**Purpose**: Mandate and authority of the National Cyber Security Authority

**Key Functions**:
- Standards development
- Compliance monitoring
- Incident coordination
- Capacity building

---

### 6. Directives on Cyber Security for Network and Information Systems
**Document**: `Directives_on_Cyber_Security_for_Network_and_Information_System.pdf`
**Scope**: Network operators and information system owners

**Technical Requirements**:
- Network segmentation
- Intrusion detection
- Security monitoring
- Backup and recovery

---

### 7. National Cyber Security Strategy 2024-2029
**Document**: `NCS_Rwanda-2024_2029.pdf`
**Purpose**: Strategic framework for Rwanda's cybersecurity development

**Pillars**:
1. Governance and policy
2. Critical infrastructure protection
3. Cybercrime response
4. Capacity development
5. International cooperation

---

## International Standards

### NIST SP 800-53 Rev 5
**Document**: `NIST.SP.800-53r5.pdf`
**Title**: Security and Privacy Controls for Information Systems and Organizations
**Publisher**: National Institute of Standards and Technology (USA)

**Control Families** (20 families, 1000+ controls):

#### Access Control (AC)
- AC-1: Policy and Procedures
- AC-2: Account Management
- AC-3: Access Enforcement
- AC-6: Least Privilege
- AC-17: Remote Access

#### Audit and Accountability (AU)
- AU-2: Event Logging
- AU-3: Content of Audit Records
- AU-6: Audit Review and Analysis
- AU-9: Protection of Audit Information
- AU-12: Audit Record Generation

#### Configuration Management (CM)
- CM-2: Baseline Configuration
- CM-6: Configuration Settings
- CM-7: Least Functionality
- CM-8: System Component Inventory

#### Contingency Planning (CP)
- CP-2: Contingency Plan
- CP-9: System Backup
- CP-10: System Recovery and Reconstitution

#### Identification and Authentication (IA)
- IA-2: User Identification and Authentication
- IA-4: Identifier Management
- IA-5: Authenticator Management

#### Incident Response (IR)
- IR-4: Incident Handling
- IR-5: Incident Monitoring
- IR-6: Incident Reporting
- IR-8: Incident Response Plan

#### Maintenance (MA)
- MA-2: Controlled Maintenance
- MA-4: Nonlocal Maintenance

#### Media Protection (MP)
- MP-2: Media Access
- MP-6: Media Sanitization

#### Physical and Environmental Protection (PE)
- PE-2: Physical Access Authorizations
- PE-3: Physical Access Control

#### Planning (PL)
- PL-2: System Security and Privacy Plans
- PL-4: Rules of Behavior

#### Risk Assessment (RA)
- RA-3: Risk Assessment
- RA-5: Vulnerability Monitoring and Scanning

#### System and Communications Protection (SC)
- SC-7: Boundary Protection
- SC-8: Transmission Confidentiality and Integrity
- SC-12: Cryptographic Key Establishment

#### System and Information Integrity (SI)
- SI-2: Flaw Remediation
- SI-3: Malicious Code Protection
- SI-4: System Monitoring
- SI-7: Software, Firmware, and Information Integrity

#### System and Services Acquisition (SA)
- SA-4: Acquisition Process
- SA-9: External System Services

---

## Control Mapping Strategy

### Rwanda to NIST Mapping

| Rwanda Control Category | NIST Control Family | Priority |
|------------------------|---------------------|----------|
| Access Control | AC (Access Control) | High |
| Audit and Logging | AU (Audit and Accountability) | High |
| Incident Response | IR (Incident Response) | High |
| System Hardening | CM (Configuration Management), SC (System and Communications Protection) | High |
| Vulnerability Management | RA (Risk Assessment), SI (System and Information Integrity) | High |
| Data Protection | MP (Media Protection), SC (System and Communications Protection) | Medium |
| Business Continuity | CP (Contingency Planning) | Medium |
| Physical Security | PE (Physical and Environmental Protection) | Low |

### Control Abstraction for ML Training

Each control will be represented in the dataset with:

```json
{
  "control_id": "AC-2",
  "control_name": "Account Management",
  "framework": "NIST-800-53",
  "rwanda_mapping": "Access Control - User Account Management",
  "description": "Organization manages system accounts",
  "log_indicators": [
    "user creation",
    "account modification",
    "privilege escalation",
    "account deletion"
  ],
  "compliance_criteria": {
    "must_have": ["audit trail", "authorization", "review"],
    "frequency": "continuous",
    "retention": "90 days"
  }
}
```

---

## Synthetic Dataset Construction

### Event Types by Framework

**Rwanda NCSA Events**:
1. Access control violations
2. Failed authentication attempts
3. Unauthorized privilege escalation
4. Missing audit logs
5. Unpatched vulnerabilities
6. Incident response delays

**NIST 800-53 Events**:
1. Configuration drift (CM-6)
2. Unauthorized remote access (AC-17)
3. Missing system backups (CP-9)
4. Malicious code detection (SI-3)
5. Boundary protection violations (SC-7)

### Compliance Labels

- **Compliant**: Event matches control requirements
- **Non-compliant**: Event violates control requirements
- **Anomalous**: Deviation from normal patterns requiring investigation

---

## Dataset Schema

```python
{
    "event_id": str,
    "timestamp": datetime,
    "user_id": str,
    "action": str,
    "resource": str,
    "source_ip": str,
    "status_code": int,
    "control_id": str,  # e.g., "AC-2", "AU-6"
    "framework": str,   # "NIST-800-53" or "Rwanda-NCSA"
    "control_category": str,
    "compliance_status": str,  # "compliant", "non-compliant"
    "anomaly_label": str,      # "normal", "anomalous"
    "severity": str,           # "low", "medium", "high", "critical"
    "log_template": str,
    "raw_message": str
}
```

---

## References

1. Rwanda NCSA. (2023). Minimum Cybersecurity Standards for Essential Service Providers.
2. NIST. (2020). SP 800-53 Rev. 5: Security and Privacy Controls for Information Systems and Organizations.
3. Rwanda National Cyber Security Strategy 2024-2029.
4. Law N° 012/2023 establishing the National Cyber Security Authority.

---

**Last Updated**: October 2025
**Maintained By**: Moise Iradukunda - CMU Research Project
