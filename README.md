# 🎓 Online Learning & Earning Platform

A full-stack web application where **students enroll in courses, attend quizzes, and track results**, while **lecturers manage course content**, and **admins control the entire system**.

---

## 🚀 Features

* 👤 User Authentication (Login/Register)
* 🔐 Role-Based Access Control (Admin / Lecturer / Student)
* 📚 Course Management System
* 🎥 Upload Videos, PDFs, Images
* 📝 Quiz Creation & Participation
* 📊 Live Quiz Results
* 💳 Free & Paid Course Access
* 🧑‍🏫 Lecturer Dashboard
* 🎓 Student Dashboard
* 🛠️ Admin Control Panel

---

## 🧠 System Overview

This platform works as a **learning + earning system**:

* **Admins** manage everything
* **Lecturers** create courses, upload content, and manage quizzes
* **Students** enroll, learn, and take quizzes with instant results

---

## 🔐 Roles & Permissions

### 👑 Admin

* Full system control
* Manage users, courses, and platform
* Monitor all activities

### 🧑‍🏫 Lecturer

* Assigned to specific courses
* Upload:

  * 🎥 Videos
  * 📄 PDFs
  * 🖼️ Images
* Create quizzes
* View student quiz results
* Access Lecturer Dashboard

### 🎓 Student

* Access free or paid courses
* View course content
* Attend quizzes
* See live results
* Access Student Dashboard

---

## 🧑‍💻 Tech Stack

### 🔙 Backend

* Python
* Django Framework

### 🎨 Frontend

* HTML5
* CSS3
* JavaScript

### 🎯 UI Framework

* Bootstrap

### 🗄️ Database

* SQLite (default)
* PostgreSQL (production ready)

---

## 📂 Project Structure

```id="stack123"
earn/
│── migrations/
│── templates/
│── static/
│── models.py
│── views.py
│── urls.py
│── admin.py
│── forms.py
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```bash id="clone321"
git clone https://github.com/Sayidhk23/online_platform.git
cd online_platform
```

### 2️⃣ Create Virtual Environment

```bash id="venv321"
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash id="install321"
pip install -r requirements.txt
```

### 4️⃣ Run Migrations

```bash id="migrate321"
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Start Server

```bash id="run321"
python manage.py runserver
```

---

## 🔑 Usage

1. Admin manages courses and users
2. Lecturer uploads content & creates quizzes
3. Students enroll in courses
4. Students complete quizzes
5. Results are shown instantly

---

## 📊 Dashboards

* 👑 Admin Dashboard → Full system control
* 🧑‍🏫 Lecturer Dashboard → Manage courses & view results
* 🎓 Student Dashboard → Learn & track progress

---

## 💡 Future Enhancements

* 💳 Payment Integration
* 📱 Mobile App
* 🔔 Notifications
* 🎥 Live Classes
* 📊 Analytics Dashboard

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch
3. Commit changes
4. Open Pull Request

---

## 📄 License

MIT License

---

## 📬 Contact

sayidhk2@gmail.com
