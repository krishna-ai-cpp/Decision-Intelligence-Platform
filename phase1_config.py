import os

db_host = "decision-intelligence-db-krishnagw08-7de7.b.aivencloud.com"
db_user = "avnadmin"
db_pass = os.environ.get("DB_PASSWORD")
db_name = "defaultdb"
db_port = 16744
db_ssl_ca = "ca.pem"

data_f = "data"
model_f = "models"
reports_f = "reports"
charts_f = "charts"
