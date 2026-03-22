from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="DriveEasy Vehicle Rental API",
    description="A complete FastAPI backend for vehicle rental system with CRUD, booking workflow, search, sorting and pagination.",
    version="1.0.0"
)


# MODELS


class RentalRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    car_id: int = Field(..., gt=0)
    days: int = Field(..., gt=0, le=30)
    license_number: str = Field(..., min_length=8)
    insurance: bool = False
    driver_required: bool = False


class NewCar(BaseModel):
    model: str = Field(..., min_length=2)
    brand: str = Field(..., min_length=2)
    type: str = Field(..., min_length=2)
    price_per_day: int = Field(..., gt=0)
    fuel_type: str = Field(..., min_length=2)
    is_available: bool = True



# DATA


cars = [
    {"id": 1, "model": "Swift", "brand": "Maruti", "type": "Hatchback", "price_per_day": 1500, "fuel_type": "Petrol", "is_available": True},
    {"id": 2, "model": "City", "brand": "Honda", "type": "Sedan", "price_per_day": 2500, "fuel_type": "Petrol", "is_available": True},
    {"id": 3, "model": "Creta", "brand": "Hyundai", "type": "SUV", "price_per_day": 3000, "fuel_type": "Diesel", "is_available": True},
    {"id": 4, "model": "Fortuner", "brand": "Toyota", "type": "SUV", "price_per_day": 6000, "fuel_type": "Diesel", "is_available": False},
    {"id": 5, "model": "Nexon", "brand": "Tata", "type": "SUV", "price_per_day": 2800, "fuel_type": "Electric", "is_available": True},
    {"id": 6, "model": "Baleno", "brand": "Maruti", "type": "Hatchback", "price_per_day": 1800, "fuel_type": "Petrol", "is_available": True},
]

rentals = []
rental_counter = 1


# HELPER FUNCTIONS


def find_car(car_id):
    return next((c for c in cars if c["id"] == car_id), None)


def calculate_rental_cost(price, days, insurance, driver):
    base = price * days

    discount = 0
    if days >= 15:
        discount = 0.25 * base
    elif days >= 7:
        discount = 0.15 * base

    insurance_cost = 500 * days if insurance else 0
    driver_cost = 800 * days if driver else 0

    total = base - discount + insurance_cost + driver_cost

    return {
        "base_cost": base,
        "discount": discount,
        "insurance_cost": insurance_cost,
        "driver_cost": driver_cost,
        "total_cost": total
    }




@app.get("/")
def home():
    return {"message": "Welcome to DriveEasy Car Rentals"}


@app.get("/cars")
def get_cars():
    available = len([c for c in cars if c["is_available"]])
    return {"cars": cars, "total": len(cars), "available_count": available}


@app.get("/cars/summary")
def summary():
    types = {}
    fuel = {}

    for c in cars:
        types[c["type"]] = types.get(c["type"], 0) + 1
        fuel[c["fuel_type"]] = fuel.get(c["fuel_type"], 0) + 1

    cheapest = min(cars, key=lambda x: x["price_per_day"])
    expensive = max(cars, key=lambda x: x["price_per_day"])

    return {
        "total": len(cars),
        "available": len([c for c in cars if c["is_available"]]),
        "type_breakdown": types,
        "fuel_breakdown": fuel,
        "cheapest": cheapest,
        "most_expensive": expensive
    }



@app.get("/cars/filter")
def filter_cars(
    type: str = Query(None),
    brand: str = Query(None),
    fuel_type: str = Query(None),
    max_price: int = Query(None),
    is_available: bool = Query(None)
):
    result = cars

    if type is not None:
        result = [c for c in result if c["type"] == type]
    if brand is not None:
        result = [c for c in result if c["brand"] == brand]
    if fuel_type is not None:
        result = [c for c in result if c["fuel_type"] == fuel_type]
    if max_price is not None:
        result = [c for c in result if c["price_per_day"] <= max_price]
    if is_available is not None:
        result = [c for c in result if c["is_available"] == is_available]

    return {"filtered": result}



@app.get("/cars/unavailable")
def unavailable():
    return [c for c in cars if not c["is_available"]]

@app.get("/cars/search")
def search(keyword: str):
    result = [
        c for c in cars
        if keyword.lower() in c["model"].lower()
        or keyword.lower() in c["brand"].lower()
        or keyword.lower() in c["type"].lower()
    ]
    return {"results": result, "total_found": len(result)}


@app.get("/cars/sort")
def sort_cars(
    sort_by: str = Query("price_per_day", pattern="^(price_per_day|brand|type)$"),
    order: str = Query("asc", pattern="^(asc|desc)$")
):
    reverse = True if order == "desc" else False

    sorted_list = sorted(cars, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_list),
        "cars": sorted_list
    }

@app.get("/cars/page")
def paginate_cars(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(3, ge=1, le=20, description="Items per page")
):
    total = len(cars)

  
    start = (page - 1) * limit
    end = start + limit

    paginated_data = cars[start:end]

    total_pages = -(-total // limit)

    return {
        "page": page,
        "limit": limit,
        "total_cars": total,
        "total_pages": total_pages,
        "cars": paginated_data
    }

@app.get("/cars/browse")
def browse_cars(
    keyword: str = Query(None),
    type: str = Query(None),
    fuel_type: str = Query(None),
    max_price: float = Query(None),
    is_available: bool = Query(None),
    sort_by: str = Query("price_per_day", pattern="^(price_per_day|brand|type)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20)
):
    filtered = cars

    # KEYWORD SEARCH
    if keyword:
        keyword = keyword.lower()
        filtered = [
            c for c in filtered
            if keyword in c["model"].lower()
            or keyword in c["brand"].lower()
            or keyword in c["type"].lower()
        ]

    #  TYPE FILTER
    if type:
        filtered = [c for c in filtered if c["type"].lower() == type.lower()]

    #  FUEL FILTER
    if fuel_type:
        filtered = [c for c in filtered if c["fuel_type"].lower() == fuel_type.lower()]

    #  PRICE FILTER
    if max_price is not None:
        filtered = [c for c in filtered if c["price_per_day"] <= max_price]

    #  AVAILABILITY FILTER
    if is_available is not None:
        filtered = [c for c in filtered if c["is_available"] == is_available]

    #  SORTING
    reverse = True if order == "desc" else False
    filtered = sorted(filtered, key=lambda x: x[sort_by], reverse=reverse)

    #  PAGINATION
    total = len(filtered)
    start = (page - 1) * limit
    end = start + limit
    paginated = filtered[start:end]

    total_pages = (total + limit - 1) // limit

    return {
        "filters_applied": {
            "keyword": keyword,
            "type": type,
            "fuel_type": fuel_type,
            "max_price": max_price,
            "is_available": is_available
        },
        "sort": {
            "sort_by": sort_by,
            "order": order
        },
        "pagination": {
            "page": page,
            "limit": limit,
            "total_results": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        },
        "results": paginated
    }


@app.get("/cars/{car_id}")
def get_car(car_id: int):
    car = find_car(car_id)
    return car if car else {"error": "Car not found"}


@app.get("/rentals")
def get_rentals():
    return {"rentals": rentals, "total": len(rentals)}





@app.post("/rentals")
def create_rental(data: RentalRequest):
    global rental_counter

    car = find_car(data.car_id)
    if not car:
        return {"error": "Car not found"}

    if not car["is_available"]:
        return {"error": "Car not available"}

    cost = calculate_rental_cost(
        car["price_per_day"],
        data.days,
        data.insurance,
        data.driver_required
    )

    rental = {
        "rental_id": rental_counter,
        "customer": data.customer_name,
        "car": f"{car['brand']} {car['model']}",
        "car_id": data.car_id,
        "days": data.days,
        "insurance": data.insurance,
        "driver_required": data.driver_required,
        **cost,
        "status": "active"
    }

    rentals.append(rental)
    car["is_available"] = False
    rental_counter += 1

    return rental






@app.post("/cars")
def add_car(car: NewCar, response: Response):


    for c in cars:
        if c["model"].lower() == car.model.lower() and c["brand"].lower() == car.brand.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Car already exists"}

    new_id = max(c["id"] for c in cars) + 1

    new_car = {
        "id": new_id,
        **car.dict()
    }

    cars.append(new_car)

    response.status_code = status.HTTP_201_CREATED
    return {
        "message": "Car added successfully",
        "car": new_car
    }

@app.put("/cars/{car_id}")
def update_car(
    car_id: int,
    response: Response,
    price_per_day: int = Query(None),
    is_available: bool = Query(None)
):
    car = find_car(car_id)

    if not car:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Car not found"}

    if price_per_day is not None:
        car["price_per_day"] = price_per_day

    if is_available is not None:
        car["is_available"] = is_available

    return {
        "message": "Car updated successfully",
        "car": car
    }



@app.get("/cars/unavailable")
def unavailable():
    return [c for c in cars if not c["is_available"]]

@app.delete("/cars/{car_id}")
def delete_car(car_id: int, response: Response):

    car = find_car(car_id)

    if not car:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Car not found"}

    for r in rentals:
        if r["car_id"] == car_id and r["status"] == "active":
            return {"error": "Car has active rental"}
        
    cars.remove(car)

    return {"message": "Car deleted successfully"}

@app.get("/rentals/{rental_id}")
def get_rental(rental_id: int):
    for r in rentals:
        if r["rental_id"] == rental_id:
            return r
    return {"error": "Not found"}

@app.post("/return/{rental_id}")
def return_car(rental_id: int):
    for r in rentals:
        if r["rental_id"] == rental_id:
            r["status"] = "returned"
            car = find_car(r["car_id"])
            if car:
                car["is_available"] = True
            return r
    return {"error": "Rental not found"}

@app.get("/rentals/active")
def active():
    return [r for r in rentals if r["status"] == "active"]

@app.get("/rentals/by-car/{car_id}")
def by_car(car_id: int):
    return [r for r in rentals if r["car_id"] == car_id]



@app.get("/cars/page")
def paginate(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    return cars[start:start+limit]

@app.get("/rentals/search")
def rental_search(customer_name: str):
    return [r for r in rentals if customer_name.lower() in r["customer"].lower()]

@app.get("/rentals/sort")
def rental_sort(sort_by: str = "total_cost"):
    return sorted(rentals, key=lambda x: x[sort_by])

@app.get("/rentals/page")
def rental_page(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    return rentals[start:start+limit]

