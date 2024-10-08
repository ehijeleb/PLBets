# Premier League Betting Prediction App

This project is a full-stack web application that allows users to predict Premier League match outcomes and generate betting tips. The frontend is built using **Next.js** with **Tailwind CSS**, and the backend is powered by **Flask**.

## Table of Contents

- [Project Overview](#project-overview)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Frontend (Next.js) Setup](#frontend-nextjs-setup)
- [Backend (Flask) Setup](#backend-flask-setup)
- [Running the Project Locally](#running-the-project-locally)
- [Deployment](#deployment)

## Project Overview

The Premier League Betting Prediction App allows users to:
1. Predict the outcome of Premier League matches based on historical data.
2. Generate betting tips for the match, including win-loss records and average goals scored for both teams.

## Technologies Used

### Frontend
- **Next.js** (React Framework)
- **Tailwind CSS** (Styling)

### Backend
- **Flask** (Python-based web framework)
- **Pandas** (For data handling and manipulation)
- **Scikit-learn** (Machine learning for match prediction)

### Other Tools
- **PostCSS** and **Autoprefixer** for CSS processing
- **Vercel** for Next.js deployment
- **Render** for Flask deployment (backend)



### Description of Key Files and Folders

- **backend/plbets/**: Contains all the backend logic, including data loading, model training, and prediction logic.
  - `__init__.py`: Initializes the Flask app.
  - `model.py`: Handles the machine learning model (RandomForestClassifier) for predictions.
  - `data_loader.py`: Responsible for loading and preprocessing match data from CSV files.
  - `predictor.py`: Contains logic for generating match predictions and betting tips.
  
- **backend/app.py**: Entry point for the Flask app. Manages API routes for predictions and tips.

- **frontend/app/**: Contains the main Next.js app components and pages.
  - `layout.js`: Defines the layout and imports global styles for the application.
  - `page.js`: The main page component that interacts with the backend API to get predictions and betting tips.
  - `globals.css`: Defines the global styles using Tailwind CSS.

- **frontend/public/**: Contains static assets like images and icons.

- **tailwind.config.js**: Configuration file for Tailwind CSS.

- **postcss.config.js**: Configuration file for PostCSS, necessary for processing Tailwind CSS.

- **package.json**: Contains dependencies and scripts for the Next.js frontend.



## Getting Started

To run the project locally, you’ll need to set up both the **backend** and the **frontend**.

### Prerequisites

Make sure you have the following installed:

- **Python** (version 3.7 or higher)
- **Node.js** (version 14 or higher)
- **npm** (Node package manager)

## Frontend (Next.js) Setup

1. Navigate to the `frontend/` directory:
```
cd frontend
```
2. Install the dependencies
```
npm install
```
3.Run the development server
```
npm run dev 
```

The frontend should now be running on http://localhost:3000.

## Backend (Flask) Setup

1. Navigate to the `backend/` directory:
```
cd backend
```
2. Install dependencies
```
pip install -r requirements.txt
```
3. Run the flask development server
```
flask run
```
The backend should now be running on http://127.0.0.1:5000.

### Running the project locally

Once both the frontend and backend are set up and running, you can interact with the application by visiting the frontend at http://localhost:3000. The frontend will send API requests back to the flask backend to get match predictions and betting tips

##Deployment 

The application is fully deployed with the following services:
- **Frontend**: Deployed using **Vercel**. You can access it [here](https://pl-bets.vercel.app/)
- **Backend**: Deployed using **Render**. You can access it [here](https://plbets.onrender.com/)

The frontend communicates with the backend via API calls to deliver real-time predictions and betting tips for Premier League Matches