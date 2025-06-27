# 📚 Library Management System

A powerful and user-friendly desktop application for managing library operations. Built with Python, PyQt5, and MySQL, this system enables librarians to manage books, members, and transactions efficiently with real-time data analytics and a modern UI.

---

## 🚀 Features

- 🔐 **User Authentication**  
  Secure login system connected to a MySQL backend.

- 📖 **Book Management**  
  Add, update, and remove books. Track genres, authors, ISBNs, and available copies.

- 👤 **Member Management**  
  Register new members with full details and membership plans.

- 🔁 **Transactions**  
  Issue and return books with automatic date tracking and overdue handling.

- 📊 **Interactive Dashboard**  
  View stats like total books, active loans, overdue items, and recent activities.

- 📈 **Data Visualizations**  
  Includes:
  - Bar chart: Monthly checkouts vs. returns
  - Pie chart: Top 5 book genres
  - Line chart: Peak borrowing hours
  - Heatmap: Busiest library sections

---

## 🛠️ Tech Stack

| Layer        | Technology        |
|--------------|------------------|
| **Frontend** | Python, PyQt5     |
| **Backend**  | MySQL, PyMySQL    |
| **GUI Tools**| Qt Designer       |
| **Data Viz** | Matplotlib, PyQtGraph, Seaborn (optional) |

---

## 📁 Project Structure

```bash
LibrarySystem/
├── assets/             # Icons, images, UI files
├── db_config.py        # MySQL connection settings
├── main.py             # App entry point
├── login.py            # Login logic and UI
├── dashboard.py        # Dashboard UI and charts
├── members.py          # Member management UI
├── books.py            # Book management UI
├── transactions.py     # Issue/return logic
├── README.md
└── requirements.txt    # Python dependencies

⚙️ Setup Instructions

Clone the repo:
git clone https://github.com/clipperKE/Library-Management-System.git
cd Library-Management-System

Create a virtual environment:
python3 -m venv venv
source venv/bin/activate

Install dependencies:
pip install -r requirements.txt

Set up MySQL Database:
Use phpMyAdmin or MySQL CLI to create the necessary tables.

Update db_config.py with your MySQL credentials.

Run the app:
python main.py

Install all requirements with:
pip install -r requirements.txt

🧪 Screenshots
Coming soon... (You can add screenshots of your login page, dashboard, and charts.)

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

📬 Contact
Developed by Coddy
📧 [techcoddymaster@gmail.com]
🌐 github.com/clipperKE
