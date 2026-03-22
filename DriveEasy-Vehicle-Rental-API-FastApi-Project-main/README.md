# 🚗 DriveEasy Car Rental API

A complete backend system built using **FastAPI** for managing a car rental service.  
This project covers **CRUD operations, booking workflow, validation, search, sorting, and pagination**.

---

## 📌 Features

### ✅ Core Features
- Get all cars and car details
- Add, update, and delete cars (CRUD)
- Rental booking system
- Return workflow (car availability update)

### ✅ Business Logic
- Prevent duplicate car entries
- Prevent deletion of cars with active rentals
- Automatic cost calculation with:
  - Discounts (7+ days → 15%, 15+ days → 25%)
  - Insurance charges
  - Driver charges

### ✅ Advanced Features
- Filtering cars by type, brand, fuel type, price, availability
- Search cars (model, brand, type)
- Search rentals (customer name)
- Sorting (cars & rentals)
- Pagination (cars & rentals)
- Combined browsing API

---

## 🛠️ Tech Stack

- **Backend:** FastAPI
- **Language:** Python
- **Validation:** Pydantic
- **Server:** Uvicorn

---## 🧠 Key Concepts Implemented

- REST API design
- Pydantic validation
- Helper functions
- Business logic enforcement
- Route ordering in FastAPI
- Query parameters handling
- Pagination logic


## 📂 Project Structure
