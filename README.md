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
- **Multi-role User System**: Landowners, Farmers, Workers, Investors, Students, Admins
- **User Registration & Authentication**: Secure login/logout system
- **Profile Management**: User profiles with contact information and expertise
- **Role-based Access Control**: Different permissions for different user types
- **Flexible Permission System**: Granular permission delegation for admin tasks

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

### 💬 **Discussion Forums** *(NEW)*
- **Topic-based Discussions**: Create and participate in farming-related discussions
- **Category Management**: Organized forums by farming topics and techniques
- **Interactive Features**: Like posts, subscribe to topics, mark solutions
- **Search Functionality**: Find relevant discussions across all topics
- **Topic Request System**: Regular users can request new discussion topics
- **Admin Notifications**: Real-time alerts for new topic requests

### 📊 **Dashboard Analytics** *(NEW)*
- **Activity Analytics**: Visual charts showing daily/weekly/monthly trends
- **Progress Tracking**: Visual progress bars for ongoing projects
- **Role-based Dashboards**: Customized dashboards for each user type
- **Quick Actions**: One-click buttons for common tasks
- **Real-time Statistics**: Live updates on platform activity

### 🔐 **Permission Management** *(NEW)*
- **Granular Permissions**: Create, Read, Update, Delete, Approve, Reject controls
- **Time-limited Access**: Set expiration dates for delegated permissions
- **Scope Control**: Limit permissions to specific categories or user types
- **Audit Logging**: Complete trail of all permission usage
- **Permission Templates**: Quick setup for common roles (Forum Moderator, Land Approver, etc.)

### 🔔 **Enhanced Notification System** *(NEW)*
- **Real-time Notifications**: AJAX-powered live updates with badges and sound alerts
- **User Preferences**: Customizable email, push, and sound notification settings
- **Notification Frequency**: Choose between immediate, hourly, daily, or weekly digests
- **Email Integration**: Automatic email notifications for important updates
- **Notification Center**: Centralized management interface for all notifications
- **Test Functionality**: Built-in notification testing for system verification
- **Enhanced Types**: Support for forums, permissions, system events, and user activities

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
   python manage.py load_forum_data
   python manage.py load_permission_categories
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
│   ├── models.py            # Custom User model with roles and notification preferences
│   ├── views.py             # User views, dashboards, analytics, notification management
│   ├── forms.py             # Registration and profile forms
│   ├── admin.py             # Admin interface customization
│   ├── notification_utils.py # Enhanced notification utility functions
│   ├── utils.py             # URL routing utilities
│   ├── context_processors.py # Dashboard URL context processor
│   └── management/          # Custom management commands
│       └── commands/
│           ├── load_sample_data.py
│           └── load_forum_data.py
├── lands/                   # Land management app
│   ├── models.py            # Land model with filtering
│   ├── views.py             # Land views with advanced filtering
│   ├── forms.py             # Land forms
│   └── admin.py             # Land admin interface
├── farming/                 # Farming projects app
│   ├── models.py            # Project and crop models
│   ├── views.py             # Project views and management
│   ├── forms.py             # Project forms
│   └── admin.py             # Project admin interface
├── marketplace/             # Marketplace app
│   ├── models.py            # Listing and transaction models
│   ├── views.py             # Marketplace views
│   ├── forms.py             # Marketplace forms
│   └── admin.py             # Marketplace admin interface
├── forums/                  # Discussion forums app *(NEW)*
│   ├── models.py            # Category, Topic, Post, TopicRequest models
│   ├── views.py             # Forum views with CRUD operations
│   ├── forms.py             # Forum forms
│   ├── admin.py             # Forum admin with topic request management
│   ├── urls.py              # Forum URL patterns
│   └── management/          # Forum management commands
│       └── commands/
│           └── load_forum_data.py
├── user_permissions/        # Permission management app *(NEW)*
│   ├── models.py            # PermissionCategory, UserPermission, PermissionLog
│   ├── views.py             # Permission management views
│   ├── admin.py             # Permission admin interface
│   ├── utils.py             # Permission utility functions
│   ├── urls.py              # Permission URL patterns
│   └── management/          # Permission management commands
│       └── commands/
│           └── load_permission_categories.py
├── payments/                # Payment processing app
│   ├── models.py            # Payment models
│   ├── views.py             # Payment views
│   └── admin.py             # Payment admin interface
├── farmcom/                 # Main project settings
│   ├── settings.py          # Django settings with all apps
│   ├── urls.py              # Main URL configuration
│   ├── views.py             # Home page view
│   └── app_urls.py          # Additional app URLs
├── templates/               # HTML templates
│   ├── base.html            # Base template with navigation
│   ├── home.html            # Home page
│   ├── accounts/            # User templates and dashboards
│   │   ├── user_dashboard.html
│   │   ├── farmer_dashboard.html
│   │   ├── worker_dashboard.html
│   │   ├── investor_dashboard.html
│   │   ├── student_dashboard.html
│   │   ├── admin_dashboard.html
│   │   ├── notifications.html # Notification center *(NEW)*
│   │   └── notification_settings.html # Notification preferences *(NEW)*
│   ├── lands/               # Land templates
│   ├── farming/             # Farming templates
│   ├── marketplace/         # Marketplace templates
│   ├── forums/              # Forum templates *(NEW)*
│   │   ├── category_list.html
│   │   ├── topic_list.html
│   │   ├── topic_detail.html
│   │   ├── create_topic.html
│   │   ├── edit_topic.html
│   │   ├── delete_topic.html
│   │   ├── request_topic.html
│   │   └── my_topic_requests.html
│   └── user_permissions/    # Permission templates *(NEW)*
│       └── manage_permissions.html
├── static/                  # Static files
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   └── images/              # Images and icons
├── media/                   # User uploaded files
├── requirements.txt         # Python dependencies
├── manage.py                # Django management script
├── README.md                # Project documentation
├── FARMCOM_RECOMMENDATIONS.md  # Development roadmap
├── DASHBOARD_ENHANCEMENTS_PROGRESS.md  # Progress tracking
└── COMMUNITY_NEWS_README.md # Community news management documentation
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
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Configuration
The project uses PostgreSQL for production with SQLite as development fallback.

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 📝 API Documentation

The application provides RESTful endpoints for:
- User management and authentication
- Land listings with advanced filtering
- Farming project management
- Marketplace operations
- Discussion forums with CRUD operations
- Permission management and delegation
- Enhanced notification system with user preferences

## 🚀 Recent Updates (July 19, 2025)

### ✅ **Enhanced Notification System**
- Real-time notification updates via AJAX
- Notification badges and sound alerts
- Email notification integration
- User notification preferences (email, push, sound, frequency)
- Notification center with management interface
- Test notification functionality
- Enhanced notification types for forums, permissions, and system events

### ✅ **Discussion Forums System**
- Complete CRUD operations for topics
- Role-based permissions (superusers vs regular users)
- Topic request system with admin notifications
- Interactive features (likes, subscriptions, solutions)
- Search functionality across topics
- Admin dashboard integration

### ✅ **Flexible Permission System**
- 8 permission categories with granular control
- Time-limited permissions with automatic expiration
- Scope control for limiting permissions
- Comprehensive audit logging
- Admin interface for permission management
- Permission templates for common roles

### ✅ **Dashboard Enhancements**
- Activity analytics with visual charts
- Progress tracking for projects
- Role-based dashboards for all user types
- Quick actions for common tasks
- Real-time statistics and notifications

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

**FarmCom** - Where Opportunity Grows -- Empowering Ghanaian Agriculture Through Technology 🌱🇬🇭