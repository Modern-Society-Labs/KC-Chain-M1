# Public Datasets Used in Stress-Test

The simulator consumes real CSV data stored in `smartcity-test/data/`.

| File | Rows | SHA-256 | Licence |
|------|------|---------|---------|
| EV_Predictive_Maintenance_Dataset_15min.csv | 4 000 | fbd6ba9635a98c72eba37970033bf2528760d7548eacd5eaefc73c6d24341daf | CC-BY-4.0 |
| Greenhouse Plant Growth Metrics.csv | 1 200 | 4012c127e9481c6b1f565e831c3ceb387967943472446e679f63dbba772af4ca | CC-BY-4.0 |
| sales_data_sample.csv | 1 000 | 6a20c7e5ce9d8a2d196f8247b6d92c1e2dc8716c5c135d737cd2465e801ca7c1 | MIT |

> Checksums generated with `sha256sum` on 2024-05-29.

---

## Column Schemas

### EV Predictive Maintenance
| Column | Unit |
|--------|------|
| timestamp | ISO-8601 |
| battery_voltage | V |
| battery_current | A |
| battery_temperature | °C |
| motor_temperature | °C |
| speed | km/h |
| acceleration | m/s² |
| regenerative_braking | % |
| energy_consumption | kWh |

### Greenhouse Metrics (excerpt)
| Column | Unit |
|--------|------|
| temperature | °C |
| humidity | % |
| soil_moisture | % |
| light_intensity | lux |
| co2_level | ppm |

### Sales Sample
| Column | Description |
|--------|-------------|
| transaction_id | Unique ID |
| product_code | SKU |
| quantity | units |
| unit_price | USD |
| total_amount | USD |

---

The simulator adds temporal jitter and variance to produce realistic synthetic streams without altering the underlying statistical distribution. 