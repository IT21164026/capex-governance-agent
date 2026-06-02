# Capex Governance Agent

A finance risk and control analytics project built using Python, Pandas, Streamlit, and Power BI.  
This project detects capex governance exceptions such as missing approvals, budget overruns, project delays, low ROI, missing supporting documents, and capitalization review requirements.

---

## Business Problem

Capital expenditure projects require strong governance because poor monitoring can lead to budget overruns, delayed project completion, weak ROI, missing approvals, incorrect capitalization treatment, and audit findings.

Finance, audit, and management teams often need a structured way to identify high-risk capex projects before issues become material. This project solves that problem by creating a rule-based governance analytics engine and an interactive review agent.

---

## Solution Overview

The Capex Governance Agent reviews simulated capex project data and automatically identifies control exceptions. It calculates risk scores, assigns risk levels, generates recommended management actions, and provides audit-style observations through a Streamlit interface.

The solution helps users:

- Monitor capex approvals
- Identify budget overruns
- Review low ROI projects
- Detect delayed projects
- Flag missing supporting documents
- Highlight capitalization review requirements
- Prioritize finance and audit follow-up actions

---

## Architecture

```text
Simulated Capex Data
        ↓
Python Data Generation
        ↓
Capex Governance Exception Engine
        ↓
Processed Risk and Exception Tables
        ↓
Streamlit Capex Agent
        ↓
Power BI Governance Dashboard