# Rythu Mitra

## Smart Farmer Decision Support Platform

Rythu Mitra is a farmer-focused decision-support platform designed to bring
multiple agricultural tools and information sources into a single application.

The platform is designed around one simple idea: instead of requiring farmers
to search across different sources, the application brings relevant information
together and helps turn it into practical daily decisions.

## Overview

Rythu Mitra combines:

- Crop recommendation using soil and environmental inputs
- Weather information and advisories
- Crop-health image analysis
- Market and price information
- Storage and sell-now comparisons
- Farm services and equipment information
- Government scheme information
- Farmer and buyer workflows
- English and Telugu accessibility

## Key Features

### Crop Recommendation

Farmers can provide soil and environmental parameters such as:

- Nitrogen (N)
- Phosphorus (P)
- Potassium (K)
- Temperature
- Humidity
- Soil pH
- Rainfall

The system uses a machine-learning model to produce a suitable crop
recommendation.

### Crop Health Analysis

Farmers can upload an image of a crop leaf for model-based image analysis.
The system returns a preliminary classification result and confidence
information where available.

### Market Intelligence

The platform provides market-related information and tools for comparing
potential selling outcomes.

The net-income calculation can take into account:

- Quantity
- Expected selling price
- Transport cost
- Other charges

### Storage vs Sell-Now

Farmers can compare an immediate selling option with a storage-and-later-selling
option using estimated costs and returns.

### Farm Services

The platform brings several farmer-support functions into one place,
including equipment-related services, crop listings, expert interaction, and
crop-damage reporting.

### Government Schemes

Relevant agricultural and government-support information can be presented
according to the farmer's profile and available data.

### Today's Action

The dashboard is designed to summarize relevant information into a simple
daily action or recommendation rather than requiring the farmer to interpret
multiple separate screens.

## Technology

The project uses a combination of web technologies and machine-learning
components.

| Area | Technology |
|---|---|
| Backend | Python / Flask |
| Frontend | HTML / CSS / JavaScript |
| Machine Learning | scikit-learn |
| Deep Learning | TensorFlow / Keras |
| Weather | OpenWeather API |
| Authentication | Session-based authentication with CSRF protection |

## Architecture

```text
Farmer
   |
   v
Login
   |
   v
Dashboard
   |
   +------ Crop Recommendation
   |
   +------ Disease Detection
   |
   +------ Market Intelligence
   |
   +------ Farm Services
   |
   +------ Government Schemes
   |
   v
Today's Action

rythu-mitra/
├── app.py
├── backend.py
├── train_model.py
├── requirements.txt
├── data/
├── static/
├── templates/
├── tests/
├── crop_model.pkl
├── plant_disease_model.h5
├── .gitignore
└── README.md
   |
   v
Farmer Decision
