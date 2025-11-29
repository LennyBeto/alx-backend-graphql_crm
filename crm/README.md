# CRM Celery Setup

Celery and Redis are used in this project to create weekly CRM reports. Celery handles the task queue and schedules the periodic generation of these reports, while Redis serves as the message broker, facilitating communication between the application and the Celery workers.

## Setup Instructions
1. Install Redis and dependencies

Install Redis on your system:

''' 
sudo apt-get update

sudo apt-get install redis-server
'''


