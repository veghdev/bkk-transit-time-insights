def transform_to_vizzu(api_data: dict) -> dict:
    series_date = []
    series_day = []
    series_period = []
    series_deviation = []

    for day_obj in api_data.get("days", []):
        date = day_obj["date"]
        day_name = day_obj["day"]
        avg = day_obj["avg_minutes"]

        for period, value in day_obj["periods"].items():
            series_date.append(date)
            series_day.append(day_name)
            series_period.append(period)
            series_deviation.append(value - avg)

    return {
        "series": [
            {"name": "Date", "type": "dimension", "values": series_date},
            {"name": "Day", "type": "dimension", "values": series_day},
            {"name": "Period", "type": "dimension", "values": series_period},
            {"name": "Deviation(min) from avg", "type": "measure", "values": series_deviation},
        ]
    }
