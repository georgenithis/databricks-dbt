## ⚙️ How to Run
- 🧾 Initial full dataset (10,000 rows)
`python synthetic_ecommerce_generator.py` --rows 10000 --output ecommerce_batch1.csv

- 🔄 Incremental run (adds new + duplicate variants)
`python synthetic_ecommerce_generator.py` --rows 3000 --incremental --existing_file ecommerce_batch1.csv --output ecommerce_batch2.csvs