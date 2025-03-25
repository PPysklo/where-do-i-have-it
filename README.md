# Where Do I Have It
A Django application for managing items, their locations, and searching using images, QR codes, and barcodes.

Requirements
- Python 3.11
- Django 4.2.11
- Other dependencies are listed in the requirements.txt file.
## Installation
Clone the repository:
```bash
git clone https://github.com/your-repository.git
cd your-repository
```
Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
Install the required packages:
```bash
pip install -r source/requirements.txt
```
Apply database migrations:
```bash
cd source
python manage.py migrate
```
Start the development server:
```bash
python manage.py runserver
```
## Usage
1. Log in or register a new account.
2. Add new items, locations, and images.
3. Use the QR code or barcode scanner to search for items, or search using a live camera feed of an item image.

Application Structure
* app: Main Django configuration.
* app_front: Application frontend.
* app_thing: Item and location management.
* app_user: User management.