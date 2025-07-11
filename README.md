# 🌱 FarmCom - Ghanaian Agricultural Community Platform

## 🌍 **The Challenge & Our Solution**

Ghana is a nation blessed with fertile lands, a vibrant culture, and a youthful population eager to contribute to national growth. Yet, despite these advantages, unemployment remains a pressing issue, leaving many skilled individuals without opportunities to thrive. At the same time, vast stretches of arable land—backyards, unused plots, and idle spaces—lie dormant, waiting to be transformed into sources of prosperity.

**The critical question is: How can we turn these untapped resources into engines of economic growth, food security, and community empowerment?**

The answer lies in **FarmCom**—an innovative, collaborative ecosystem designed to bridge the gap between unemployment and opportunity through sustainable agriculture.

## 🚀 **What is FarmCom?**

FarmCom is more than just a platform; it's a revolutionary movement that connects:

- **🏠 Landowners** with unused arable land
- **👥 Unemployed individuals** seeking meaningful work
- **👨‍🌾 Professional farmers** with expertise to share
- **💰 Investors** looking for impactful opportunities
- **🎓 Students** eager to learn and innovate

By fostering collaboration among these stakeholders, FarmCom cultivates crops, builds skills, and generates income—all while promoting food security, environmental sustainability, and economic empowerment.

**FarmCom** is a project within **AHAJAH Creo**, dedicated to revolutionizing agricultural practices and community building in Ghana.

## 🏢 About AHAJAH Creo

**AHAJAH Creo** is a forward-thinking company committed to sustainable development and community empowerment through innovative technology solutions. Our mission is to bridge the gap between traditional agricultural practices and modern digital solutions.

- **Website**: [www.ahajahcreo.org](https://www.ahajahcreo.org)
- **Blog**: [FarmCom: Cultivating Opportunity, Harvesting Prosperity](https://ahajahcreo.org/farmcom-cultivating-opportunity-harvesting-prosperity/)
- **Social Media**: Follow us for updates and community stories
  - Instagram: [@ahajahcreo_](https://instagram.com/ahajahcreo_)
  - Twitter: [@ahajahcreo_](https://twitter.com/ahajahcreo_)
  - Facebook: [@ahajahcreo_](https://facebook.com/ahajahcreo_)

## 🇬🇭 Features

### 🏠 **User Management**
- **Multi-role User System**: Landowners, Farmers, Workers, Investors, Students
- **User Registration & Authentication**: Secure login/logout system
- **Profile Management**: User profiles with contact information and expertise
- **Role-based Access Control**: Different permissions for different user types

### 🗺️ **Land Management**
- **Land Listings**: Browse available agricultural lands
- **Advanced Filtering**: Filter by location, soil type, land size, and crop preferences
- **Land Details**: Comprehensive land information including soil type, water source, and preferred crops
- **Ghanaian Focus**: Lands from major Ghanaian regions (Kumasi, Tamale, Sunyani, Cape Coast, Accra)

### 🌾 **Farming Projects**
- **Project Management**: Create and manage farming projects
- **Status Tracking**: Active, Planning, Harvested project states
- **Crop Management**: Track different crops and their progress
- **Financial Tracking**: Budget and actual yield monitoring

### 🛒 **Marketplace**
- **Crop Listings**: Buy and sell agricultural products
- **Market Integration**: Connect harvested crops to marketplace
- **Price Tracking**: Monitor crop prices and market trends

### 🎨 **User Interface**
- **Modern Design**: Clean, responsive Bootstrap-based interface
- **Ghanaian Theme**: Culturally relevant design elements
- **Mobile Responsive**: Works seamlessly on all devices
- **Intuitive Navigation**: Easy-to-use interface for all user types

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/streetprophet90/FarmCom_BETA.git
   cd FarmCom_BETA
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv farmenv
   ```

3. **Activate the virtual environment**
   - **Windows:**
     ```bash
     farmenv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source farmenv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load sample data (optional)**
   ```bash
   python manage.py load_sample_data
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Open your browser and go to: `http://127.0.0.1:8000/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

## 📁 Project Structure

```
FarmCom_BETA/
├── accounts/                 # User management app
│   ├── models.py            # Custom User model
│   ├── views.py             # User views and forms
│   ├── forms.py             # Registration and profile forms
│   └── management/          # Custom management commands
│       └── commands/
│           └── load_sample_data.py
├── lands/                   # Land management app
│   ├── models.py            # Land model
│   ├── views.py             # Land views with filtering
│   └── forms.py             # Land forms
├── farming/                 # Farming projects app
│   ├── models.py            # Project and crop models
│   └── views.py             # Project views
├── marketplace/             # Marketplace app
│   ├── models.py            # Listing models
│   └── views.py             # Marketplace views
├── payments/                # Payment processing app
├── farmcom/                 # Main project settings
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   └── views.py             # Home page view
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   ├── home.html            # Home page
│   ├── accounts/            # User templates
│   ├── lands/               # Land templates
│   ├── farming/             # Farming templates
│   └── marketplace/         # Marketplace templates
├── static/                  # Static files
│   ├── css/                 # Stylesheets
│   └── images/              # Images and icons
└── manage.py                # Django management script
```

## 🌍 Ghanaian Agricultural Focus

### **Regional Coverage**
- **Ashanti Region (Kumasi)**: Cocoa farming, plantain, cassava
- **Northern Region (Tamale)**: Rice cultivation, maize, groundnuts
- **Bono Region (Sunyani)**: Oil palm, cassava, yam
- **Central Region (Cape Coast)**: Vegetables, tomatoes, peppers
- **Greater Accra Region (Accra)**: Pineapple, mixed crops

### **Crop Types**
- **Cash Crops**: Cocoa, Oil Palm, Pineapple
- **Food Crops**: Rice, Maize, Cassava, Yam, Plantain
- **Vegetables**: Tomatoes, Peppers, Garden Eggs
- **Legumes**: Groundnuts

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root with the following variables:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration
The project uses SQLite by default. For production, consider using PostgreSQL or MySQL.

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 📝 API Documentation

The application provides RESTful endpoints for:
- User management
- Land listings with filtering
- Farming project management
- Marketplace operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Harry Fynn Amoafo**
- **Email**: [harryfynn@ahajahcreo.org](mailto:harryfynn@ahajahcreo.org)
- **GitHub**: [@streetprophet90](https://github.com/streetprophet90)
- **Company**: AHAJAH Creo
- **Project**: FarmCom - Ghanaian Agricultural Community Platform

## 🌐 Connect With Us

- **Company Website**: [www.ahajahcreo.org](https://www.ahajahcreo.org)
- **FarmCom Blog**: Read our latest insights and updates
- **Social Media**:
  - 📸 Instagram: [@ahajahcreo_](https://instagram.com/ahajahcreo_)
  - 🐦 Twitter: [@ahajahcreo_](https://twitter.com/ahajahcreo_)
  - 📘 Facebook: [@ahajahcreo_](https://facebook.com/ahajahcreo_)

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap for the responsive design components
- Ghanaian agricultural community for inspiration
- AHAJAH Creo team for continuous support and innovation
- All contributors and testers who help improve FarmCom

---

**FarmCom** - Empowering Ghanaian Agriculture Through Technology 🌱🇬🇭 